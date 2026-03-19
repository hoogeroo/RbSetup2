import requests
import time
from typing import Optional, Dict, Any

# Fill this with your ESP8266 server URL
ESP_url = "http://192.168.4.1/status"


def fetch_temperatures(url: str, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
    """Synchronously fetch temperatures from the given URL and return a normalized dict."""
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.json()

        if not isinstance(data, dict):
            return None
        
        temps = {}
   
        # Extract temperatures
        devices = data.get("devices", [])
        for dev in devices:
            device_id = dev.get("device_id")
            temperature = dev.get("temperature")

            if device_id and temperature is not None:
                temps[device_id] = temperature

        return temps
    
    except Exception:
        return None