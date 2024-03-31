import requests
from typing import Optional

class AirPorceApi:
    base_url = "https://aph.airproce.com"

    def __init__(self, token: str):
        self.headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Accept": "application/json",
            "token": token
        }

    def set_mode(self, device_id: str, mode_id: int, lang: str = "zh-Hans") -> Optional[bool]:
        """Set the mode of the air purifier."""
        url = f"{self.base_url}/addons/shopro/user_device/action_control"
        data = {"did": device_id, "mode": mode_id, "language": lang}
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()
        except requests.RequestException as e:
            print(f"Error communicating with Air Purifier: {e}")
            return None

