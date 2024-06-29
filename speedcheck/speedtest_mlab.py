import asyncio
import json
import time

import requests
import websockets


async def download_test(uri):
    async with websockets.connect(uri, subprotocols=['net.measurementlab.ndt.v7']) as websocket:
        start = time.time() * 1000  # Start time in milliseconds
        previous = start
        total = 0
        animation = "|/-\\"
        animation_index = 0

        try:
            while True:
                message = await websocket.recv()

                if isinstance(message, bytes):
                    total += len(message)
                elif isinstance(message, str):
                    server_message = message
                    #print(f"Server message: {server_message}")
                else:
                    raise ValueError(f"Unknown message type: {type(message)}")

                current_time = time.time() * 1000  # Current time in milliseconds
                elapsed_time = (current_time - start) / 1000  # Elapsed time in seconds

                # Perform a client-side measurement 4 times per second.
                every = 250  # ms
                if current_time - previous > every:
                    mean_client_mbps = (total * 8 / 1_000_000) / elapsed_time
                    #print(f"Measurement: ElapsedTime = {elapsed_time:.2f} s, NumBytes = {total}, MeanClientMbps = {mean_client_mbps:.2f}")
                    print(f"\r{animation[animation_index % len(animation)]} Running download speed test...", end="")
                    animation_index += 1
                    previous = current_time
        except websockets.ConnectionClosed:
            print("\nConnection closed")
        except Exception as e:
            print(f"\nError: {e}")

        elapsed_time = (time.time() * 1000 - start) / 1000  # Final elapsed time in seconds
        mean_client_mbps = (total * 8 / 1_000_000) / elapsed_time
        download_dict = {}
        download_dict['Elapsed Time'] = "{:.2f} seconds".format(elapsed_time)
        download_dict['Mean Upload speed'] = "{:.2f} Mbps".format(mean_client_mbps)
        print("\n"+"Download test complete")
        print(json.dumps(download_dict,indent=2)+"\n")



async def upload_test(uri):
    async with websockets.connect(uri, subprotocols=['net.measurementlab.ndt.v7']) as websocket:
        start = time.time() * 1000  # Start time in milliseconds
        previous = start
        total = 0
        animation = "|/-\\"
        animation_index = 0
        data = bytearray(8192)  # Initial message size 8kB
        duration = 10000  # Test duration 10 seconds
        end = start + duration

        async def uploader():
            nonlocal total, previous, animation_index
            while time.time() * 1000 < end:
                await websocket.send(data)
                total += len(data)
                current_time = time.time() * 1000
                elapsed_time = (current_time - start) / 1000

                if current_time - previous >= 250:  # Report every 250ms
                    mean_client_mbps = (total * 8 / 1_000_000) / elapsed_time
                    print(f"\r{animation[animation_index % len(animation)]} Running upload speed test...", end="")
                    animation_index += 1
                    previous = current_time

        try:
            await uploader()
        except websockets.ConnectionClosed:
            print("\nConnection closed")
        except Exception as e:
            print(f"\nError: {e}")

        elapsed_time = (time.time() * 1000 - start) / 1000  # Final elapsed time in seconds
        mean_client_mbps = (total * 8 / 1_000_000) / elapsed_time
        upload_dict = {}
        upload_dict['Elapsed Time'] = "{:.2f} seconds".format(elapsed_time)
        upload_dict['Mean Upload speed'] = "{:.2f} Mbps".format(mean_client_mbps)
        print("\n"+"Upload test complete")
        print(json.dumps(upload_dict,indent=2))


def get_nearest_server():
    response = requests.get('https://locate.measurementlab.net/v2/nearest/ndt/ndt7')
    data = response.json()
    return data


async def main():
    data = get_nearest_server()

    # Choose the first server from the list
    server = data['results'][0]

    value_store = []
    for key, values in server['location'].items():
        value_store.append(values)
    print("\n"+"Running Measurement Lab Speed Test (speed.measurementlab.net)"+"\n")
    print(f"Selected Server location: {', '.join(value_store)}")

    download_url = server['urls']['ws:///ndt/v7/download']
    upload_url = server['urls']['ws:///ndt/v7/upload']

    await download_test(download_url)
    await upload_test(upload_url)

def mlab_speed_test():
    asyncio.run(main())

#mlab_speed_test()
