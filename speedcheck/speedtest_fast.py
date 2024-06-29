import asyncio
import json

from deepdiff import DeepDiff
from playwright.async_api import async_playwright


class Options:
    def __init__(self, measure_upload=False):
        self.measure_upload = measure_upload

class Result:
    def __init__(self, download_speed, upload_speed, download_unit, downloaded, upload_unit, latency, buffer_bloat, user_location, user_ip, is_done):
        self.download_speed = download_speed
        self.upload_speed = upload_speed
        self.download_unit = download_unit
        self.downloaded = downloaded
        self.upload_unit = upload_unit
        self.latency = latency
        self.buffer_bloat = buffer_bloat
        self.user_location = user_location
        self.user_ip = user_ip
        self.is_done = is_done

    def __eq__(self, other):
        if isinstance(other, Result):
            return self.__dict__ == other.__dict__
        return False

async def monitor_speed(page, options=None):
    previous_result = None
    iteration = 0
    animation = "|/-\\"
    animation_index = 0

    while True:
        result = await page.evaluate('''() => {
            const $ = document.querySelector.bind(document);

            return {
                downloadSpeed: Number($('#speed-value')?.textContent),
                uploadSpeed: Number($('#upload-value')?.textContent),
                downloadUnit: $('#speed-units')?.textContent?.trim(),
                downloaded: Number($('#down-mb-value')?.textContent?.trim()),
                uploadUnit: $('#upload-units')?.textContent?.trim(),
                latency: Number($('#latency-value')?.textContent?.trim()),
                bufferBloat: Number($('#bufferbloat-value')?.textContent?.trim()),
                userLocation: $('#user-location')?.textContent?.trim(),
                userIp: $('#user-ip')?.textContent?.trim(),
                isDone: Boolean($('#speed-value.succeeded') && $('#upload-value.succeeded')),
            };
        }''')

        result = Result(
            result['downloadSpeed'], result['uploadSpeed'], result['downloadUnit'], result['downloaded'],
            result['uploadUnit'], result['latency'], result['bufferBloat'],
            result['userLocation'], result['userIp'], result['isDone']
        )

        if result.is_done:
            return result

        previous_result = result

        # Show animation
        print(f"\r{animation[animation_index % len(animation)]} Running speed test...", end="")
        animation_index += 1

        iteration += 1
        await asyncio.sleep(0.1)

async def api(options=None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--no-sandbox'])
        page = await browser.new_page()
        await page.goto('https://fast.com')

        final_result = None
        try:
            final_result = await monitor_speed(page, options)
        finally:
            await browser.close()

        if final_result:
            print("\nFinal Result:")
            final_result.__dict__
            clean_dict = {}
            clean_dict['Download speed'] = f"{final_result.__dict__['download_speed']} {final_result.__dict__['download_unit']}"
            clean_dict['Upload speed'] = f"{final_result.__dict__['upload_speed']} {final_result.__dict__['upload_unit']}"
            clean_dict['Latency'] = f"{final_result.__dict__['latency']} ms"
            clean_dict['User Location'] = final_result.__dict__['user_location']
            clean_dict['User IP'] = final_result.__dict__['user_ip']
            clean_dict['Test Complete'] = final_result.__dict__['is_done']
            print(json.dumps(clean_dict,indent=2))
def fast_speed_test():
    print("\n"+"Running Fast.com Speed Test (fast.com)"+"\n")
    asyncio.run(api(Options()))

#fast_speed_test()
