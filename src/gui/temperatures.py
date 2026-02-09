import requests
import time
from typing import Optional, Dict, Any

# Fill this with your ESP8266 server URL, e.g. "http://192.168.4.1/status"
ESP_url = "http://192.168.4.1"


def fetch_temperatures(url: str, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
    """Synchronously fetch temperatures from the given URL and return a normalized dict.

    Returns a dict with keys 'upper_coil', 'lower_coil' and 'ambient_temp' when successful,
    or None on failure. This function deliberately does not spawn threads — call it from
    your GUI main loop or a QTimer callback.
    """
    try:
        if not url:
            return None
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.json()

        if not isinstance(data, dict):
            return None

        return {
            "upper_coil": data.get("upper_coil"),
            "lower_coil": data.get("lower_coil"),
            "ambient_temp": data.get("ambient_temp"),
        }
    except Exception:
        return None


if __name__ == "__main__":
    # CLI poller for debugging the endpoint
    import sys
    url = ESP_url
    if not url:
        print("Usage: temperatures.py <url>")
        sys.exit(1)

    interval = 1.0
    try:
        while True:
            vals = fetch_temperatures(url)
            if vals:
                print(f"Upper Coil: {vals['upper_coil']} °C | Lower Coil: {vals['lower_coil']} °C | Ambient: {vals['ambient_temp']} °C")
            else:
                print("Failed to fetch temperatures")
            time.sleep(interval)
    except KeyboardInterrupt:
        pass