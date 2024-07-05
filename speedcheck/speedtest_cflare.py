import json
import logging
import statistics
import time
from enum import Enum
from typing import Any, NamedTuple

import requests

log = logging.getLogger("cfspeedtest")

class TestType(Enum):
    Down = "GET"
    Up = "POST"

class TestSpec(NamedTuple):
    size: int
    iterations: int
    name: str
    type: TestType

    @property
    def bits(self) -> int:
        return self.size * 8

TestSpecs = tuple[TestSpec, ...]

DOWNLOAD_TESTS: TestSpecs = (
    TestSpec(100_000, 10, "100kB", TestType.Down),
    TestSpec(1_000_000, 8, "1MB", TestType.Down),
    TestSpec(10_000_000, 6, "10MB", TestType.Down),
    TestSpec(25_000_000, 4, "25MB", TestType.Down),
)
UPLOAD_TESTS: TestSpecs = (
    TestSpec(100_000, 8, "100kB", TestType.Up),
    TestSpec(1_000_000, 6, "1MB", TestType.Up),
    TestSpec(10_000_000, 4, "10MB", TestType.Up),
)
DEFAULT_TESTS: TestSpecs = (
    TestSpec(1, 20, "latency", TestType.Down),
    *DOWNLOAD_TESTS,
    *UPLOAD_TESTS,
)

class TestResult(NamedTuple):
    value: Any
    time: float = time.time()

class TestTimers(NamedTuple):
    full: list[float]
    server: list[float]
    request: list[float]

    def to_speeds(self, test: TestSpec) -> list[int]:
        if test.type == TestType.Up:
            return [int(test.bits / server_time) for server_time in self.server]
        return [
            int(test.bits / (full_time - server_time))
            for full_time, server_time in zip(self.full, self.server)
        ]

    def to_latencies(self) -> list[float]:
        return [
            (request_time - server_time) * 1e3
            for request_time, server_time in zip(self.request, self.server)
        ]

    @staticmethod
    def jitter_from(latencies: list[float]) -> float | None:
        if len(latencies) < 2:
            return None
        return statistics.mean(
            [
                abs(latencies[i] - latencies[i - 1])
                for i in range(1, len(latencies))
            ]
        )

class TestMetadata(NamedTuple):
    ip: str
    isp: str
    location_code: str
    region: str

def _calculate_percentile(data: list[float], percentile: float) -> float:
    data = sorted(data)
    idx = (len(data) - 1) * percentile
    rem = idx % 1

    if rem == 0:
        return data[int(idx)]

    edges = (data[int(idx)], data[int(idx) + 1])
    return edges[0] + (edges[1] - edges[0]) * rem

SuiteResults = dict[str, dict[str, TestResult]]

class CloudflareSpeedtest:
    def __init__(self, results: SuiteResults | None = None, tests: TestSpecs = DEFAULT_TESTS, timeout: tuple[float, float] | float = (10, 25)) -> None:
        self.results = results or {}
        self.results.setdefault("tests", {})
        self.results.setdefault("meta", {})

        self.tests = tests
        self.request_sess = requests.Session()
        self.timeout = timeout

    def get_location_data(self, ip_address: str, max_retries: int = 3) -> dict[str, str | float]:
        url = f'https://json.geoiplookup.io/{ip_address}'
        attempt = 0

        while attempt < max_retries:
            response = requests.get(url)
            if response.status_code == 200:
                response_data = response.json()
                return {
                    "ip": ip_address,
                    "region": response_data.get("region", "NA"),  # Update field name
                    "country": response_data.get("country_name"),
                    "latitude": response_data.get("latitude"),
                    "longitude": response_data.get("longitude"),
                    "isp": response_data.get("isp"),
                    "timezone": response_data.get("timezone_name")
                }
            attempt += 1

        return {"region": "NA"}

    def metadata(self) -> TestMetadata:
        result_data: dict[str, str] = self.request_sess.get(
            "https://speed.cloudflare.com/meta"
        ).json()

        ip_address = result_data["clientIp"]
        location_data = self.get_location_data(ip_address)

        return TestMetadata(
            result_data["clientIp"],
            result_data["asOrganization"],
            result_data["colo"],
            location_data.get("region", "NA"),
        )

    def run_test(self, test: TestSpec) -> TestTimers:
        coll = TestTimers([], [], [])
        url = f"https://speed.cloudflare.com/__down?bytes={test.size}"
        data = None
        if test.type == TestType.Up:
            url = "https://speed.cloudflare.com/__up"
            data = b"".zfill(test.size)

        for _ in range(test.iterations):
            start = time.time()
            r = self.request_sess.request(
                test.type.value, url, data=data, timeout=self.timeout
            )
            coll.full.append(time.time() - start)
            coll.server.append(
                float(r.headers["Server-Timing"].split("=")[1].split(",")[0]) / 1e3
            )
            coll.request.append(
                r.elapsed.seconds + r.elapsed.microseconds / 1e6
            )
        return coll

    def _sprint(self, label: str, result: TestResult, *, meta: bool = False) -> None:
        #log.info("%s: %s", label, result.value)
        save_to = self.results["meta"] if meta else self.results["tests"]
        if label not in save_to:
            save_to[label] = []
        save_to[label].append(result)

    def run_all(self, *, megabits: bool = False) -> SuiteResults:
        animation = "|/-\\"
        animation_index = 0
        meta = self.metadata()
        self._sprint("ip", TestResult(meta.ip), meta=True)
        self._sprint("isp", TestResult(meta.isp))
        self._sprint("location_code", TestResult(meta.location_code), meta=True)
        self._sprint("location_region", TestResult(meta.region), meta=True)

        data = {"down": [], "up": []}
        for test in self.tests:
            timers = self.run_test(test)
            print(f"\r{animation[animation_index % len(animation)]} Running speed test...", end="")
            animation_index += 1
            if test.name == "latency":
                latencies = timers.to_latencies()
                jitter = timers.jitter_from(latencies)
                if jitter:
                    jitter = round(jitter, 2)
                self._sprint(
                    "latency",
                    TestResult(round(statistics.mean(latencies), 2)),
                )
                self._sprint("jitter", TestResult(jitter))
                continue

            speeds = timers.to_speeds(test)
            data[test.type.name.lower()].extend(speeds)
            mean_speed = int(statistics.mean(speeds))
            label_suffix = "bps"
            if megabits:
                mean_speed = round(mean_speed / 1e6, 2)
                label_suffix = "mbps"
            self._sprint(
                f"{test.name}_{test.type.name.lower()}_{label_suffix}",
                TestResult(mean_speed),
            )
            print(f"\r{animation[animation_index % len(animation)]} Running speed test...", end="")
            animation_index += 1
        for k, v in data.items():
            result = None
            if len(v) > 0:
                result = int(_calculate_percentile(v, 0.9))
            label_suffix = "bps"
            if megabits:
                result = round(result / 1e6, 2) if result else result
                label_suffix = "mbps"
            self._sprint(
                f"90th_percentile_{k}_{label_suffix}",
                TestResult(result),
            )
        print(f"\r{animation[animation_index % len(animation)]} Running speed test...", end="")
        animation_index += 1
        return self.results

    @staticmethod
    def results_to_dict(results: SuiteResults) -> dict[str, dict[str, dict[str, float]]]:
        return {
            k: {sk: [res._asdict() for res in sv]}
            for k, v in results.items()
            for sk, sv in v.items()
        }

def cflare_speedtest():
    print("\nRunning Cloudflare Speed Test (speed.cloudflare.com)\n")
    speedtest = CloudflareSpeedtest()
    data = speedtest.run_all()
    for key in data:
        for subkey in data[key]:
            data[key][subkey] = [item[0] for item in data[key][subkey]]

    result_dict = {
        'Download Speed': f"{round(data['tests']['90th_percentile_down_bps'][0] / 1_000_000, 2)} Mbps",
        'Upload Speed': f"{round(data['tests']['90th_percentile_up_bps'][0] / 1_000_000, 2)} Mbps",
        'Latency': f"{round(data['tests']['latency'][0], 2)} ms",
        'Jitter': f"{round(data['tests']['jitter'][0], 2)} ms"
    }

    # Print metadata
    metadata = speedtest.metadata()
    result_dict["IP"] = metadata.ip
    result_dict["ISP"] = metadata.isp
    result_dict["Location Code"] = metadata.location_code
    result_dict["Region"] = metadata.region
    print("\n"+json.dumps(result_dict, indent=2))

if __name__ == "__main__":
    cflare_speedtest()
