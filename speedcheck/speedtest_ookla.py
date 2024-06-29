import json

import speedtest


def ookla_speed_test():
    """
    Runs a speedtest and displays results
    """
    print("\n"+"Running Ookla Speed Test (speedtest.net)"+"\n")

    # Create a Speedtest object
    st = speedtest.Speedtest()

    try:
        result_dict = {}
        result_dict['Download Speed'] = f"{round(st.download() / 1000000,2)} Mbps"  # Convert to Mbps
        result_dict['Upload Speed'] = f"{round(st.upload() / 1000000,2)} Mbps"  # Convert to Mbps
        result_dict['Server Location'] = f"{st.results.server['name']}"
        result_dict['Ping'] = f"{st.results.ping} ms"
        print(json.dumps(result_dict,indent=2))
    except speedtest.SpeedtestException as e:
        print("An error occurred during the speed test:", str(e))

#ookla_speed_test()
