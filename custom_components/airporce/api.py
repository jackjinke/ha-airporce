import requests
from typing import Optional

class AirPorceApi:
    base_url = "https://aph.airproce.com"
    lang = 'zh-Hans'

    def __init__(self, token: str):
        self.headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Accept": "application/json",
            "token": token
        }

    
    def list_groups(self):
        """Fetch the list of devices from the API."""
        url = f"{self.base_url}/addons/shopro/user_device/groupList"
        data = {"language": self.lang}
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()['data']
        except requests.RequestException as e:
            print(f"Error communicating with API: {e}")
            return None


    def set_mode(self, device_id: str, mode_id: int) -> Optional[bool]:
        """Set the mode of the air purifier."""
        url = f"{self.base_url}/addons/shopro/user_device/action_control"
        data = {"did": device_id, "mode": mode_id, "language": self.lang}
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()
        except requests.RequestException as e:
            print(f"Error communicating with API: {e}")
            return None

