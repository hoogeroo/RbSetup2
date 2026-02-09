import requests
import json
import time
import sys

ESP_url = "fill in"
poll_s = 1.0

def main():
    while True:
        try:
            response = requests.get(ESP_url, timeout=5)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            msg.update({
                "upper_coil": data.get("upper_coil"),
                "lower_coil": data.get("lower_coil"),
                "ambient_temp": data.get("ambient_temp")
            })
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

        sys.stdout.write(f"\rUpper Coil: {msg['upper_coil']} °C | Lower Coil: {msg['lower_coil']} °C | Ambient Temp: {msg['ambient_temp']} °C")
        sys.stdout.flush() 
        time.sleep(poll_s)

if __name__ == "__main__":
    main()