__copyright__ = """
Copyright 2024 Samapriya Roy

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

__license__ = "Apache 2.0"

import argparse
import importlib
import json
import logging
import os
import subprocess
import sys
import webbrowser
from importlib.metadata import version

import requests

os.chdir(os.path.dirname(os.path.realpath(__file__)))
lpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(lpath)

from .speedtest_cflare import cflare_speedtest
from .speedtest_fast import fast_speed_test
from .speedtest_mlab import mlab_speed_test
from .speedtest_ookla import ookla_speed_test
from .speedtest_openspeedtest import openspeedtest_speed_test
from .speedtest_speedsmart import speedsmart_speed_test

# Set a custom log formatter
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


class Solution:
    def compareVersion(self, version1, version2):
        versions1 = [int(v) for v in version1.split(".")]
        versions2 = [int(v) for v in version2.split(".")]
        for i in range(max(len(versions1), len(versions2))):
            v1 = versions1[i] if i < len(versions1) else 0
            v2 = versions2[i] if i < len(versions2) else 0
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        return 0


ob1 = Solution()


# Get package version
def version_latest(package):
    response = requests.get(f"https://pypi.org/pypi/{package}/json")
    if "message" in response.json():
        #print(f"Package {package} not found on PyPI")
        return None
    elif "info" in response.json():
        latest_version = response.json()["info"]["version"]
        #print(f"Latest version of {package} is {latest_version}")
        return latest_version


def install_version(package):
    try:
        installed_version = version(package)
        return installed_version
    except importlib.metadata.PackageNotFoundError:
        return None


def speedcheck_version(package):
    """
    Check and notify about the latest version of the 'speedcheck' package.
    """
    latest_version = version_latest(package)
    installed_version = install_version(package)
    if latest_version is not None and installed_version is not None:
        vcheck = ob1.compareVersion(
            latest_version,
            installed_version,
        )
        if vcheck == 1:
            print(
                f"Current version of speedcheck is {installed_version} upgrade to latest version: {latest_version}"
            )
        elif vcheck == -1:
            print(
                f"Possibly running staging code {installed_version} compared to pypi release {latest_version}"
            )
    elif latest_version is None and installed_version is not None:
        print(f"Package {package} not found on PyPI")
    elif latest_version is not None and installed_version is None:
        print(f"Package {package} not installed")
    elif latest_version is None and installed_version is None:
        print(f"Package {package} not found on PyPI and not installed")

speedcheck_version("speedcheck")

# # Go to the readMe
# def readme():
#     try:
#         a = webbrowser.open("https://samapriya.github.io/speedcheck/", new=2)
#         if a == False:
#             print("Your setup does not have a monitor to display the webpage")
#             print(" Go to {}".format("https://samapriya.github.io/speedcheck/"))
#     except Exception as e:
#         logging.exception(e)


# def read_from_parser(args):
#     readme()

def setup_playwright():
    try:
        result = subprocess.run(["playwright", "install"], capture_output=True, text=True)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.stderr)

        result = subprocess.run(["playwright", "install-deps"], capture_output=True, text=True)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.stderr)
        print("\n"+"Successfully set up Playwright. Setup complete")
    except subprocess.CalledProcessError as error:
        print(f"Error occurred during playwright setup: {error}")
        sys.exit("Issues setting up Playwright.")

def setup_env_from_parser(args):
    setup_playwright()

def speedcheck_info():
    speedcheck_dict = {}
    speedcheck_dict["cloudflare"] = "Runs speedtest from Cloudflare: speed.cloudflare.com"
    speedcheck_dict["fast"] = "Runs speedtest from fast.com"
    speedcheck_dict["ookla"] = "Runs speedtest from Ookla speedtest: speedtest.ookla.com"
    speedcheck_dict["mlab"] = "Runs speedtest from mlab: speedtest.mlab.com"
    speedcheck_dict["openspeedtest"] = "Runs speedtest from Open Speed Test: openspeedtest.com"
    speedcheck_dict["speedsmart"] = "Runs speedtest from Speed Smart: speedsmart.net"
    print(json.dumps(speedcheck_dict, indent=2))


def speedcheck_info_from_parser(args):
    speedcheck_info()


def speedcheck_run(speedtest):
    if speedtest == "cloudflare":
        cflare_speedtest()
    elif speedtest == "fast":
        fast_speed_test()
    elif speedtest == "ookla":
        ookla_speed_test()
    elif speedtest == "mlab":
        mlab_speed_test()
    elif speedtest == "openspeedtest":
        openspeedtest_speed_test()
    elif speedtest == "speedsmart":
        speedsmart_speed_test()
    else:
        print("Invalid speedtest type")


def speedcheck_run_from_parser(args):
    speedcheck_run(speedtest=args.type)


# spacing = "                               "


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Simple CLI for running internet speed tests"
    )

    subparsers = parser.add_subparsers()

    # parser_read = subparsers.add_parser(
    #     "readme", help="Go the web based speedcheck readme page"
    # )
    # parser_read.set_defaults(func=read_from_parser)

    parser_setup = subparsers.add_parser(
        "setup", help="Setup speedcheck & install dependencies"
    )
    parser_setup.set_defaults(func=setup_env_from_parser)

    parser_info = subparsers.add_parser(
        "info", help="Prints info about speedcheck"
    )
    parser_info.set_defaults(func=speedcheck_info_from_parser)

    parser_run = subparsers.add_parser(
        "run", help="Runs speedcheck based on speedtest type"
    )
    required_named = parser_run.add_argument_group("Required named arguments.")
    required_named.add_argument(
        "--type",
        help="Speedtest type: cloudflare, fast, ookla, mlab, openspeedtest, speedsmart",
        required=True,
    )
    parser_run.set_defaults(func=speedcheck_run_from_parser)

    args = parser.parse_args()

    try:
        func = args.func
    except AttributeError:
        parser.error("too few arguments")
    func(args)


if __name__ == "__main__":
    main()
