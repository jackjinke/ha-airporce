import requests
from typing import Optional

class AirPorceApi:
    base_url = "https://aph.airproce.com"
    country = '中国,大陆'
    lang = 'zh-Hans'    

    def __init__(self, token: str = None):
        self.headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Accept": "application/json",
        }
        if token is not None:
            self.headers['token'] = token
    
    def set_token(self, token: str):
        self.headers['token'] = token

    def send_login_sms(self, phone_number: str) -> Optional[bool]:
        url = f"{self.base_url}/addons/shopro/sms/send"
        data = {"event": "loginOrRegister", "mobile": phone_number, "language": self.lang}
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()
        except requests.RequestException as e:
            print(f"Error communicating with API: {e}")
            return None

    def user_login(self, phone_number: str, sms_code: str) -> Optional[bool]:
        url = f"{self.base_url}/addons/shopro/user/smsLoginOrRegister"
        data = {"mobile": phone_number, "code": sms_code, "language": self.lang, "country": self.country}
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()
        except requests.RequestException as e:
            print(f"Error communicating with API: {e}")
            return None
        
    def user_logout(self):
        url = f"{self.base_url}/addons/shopro/user/logout"
        data = {"language": self.lang}
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()
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
    
    def list_groups(self):
        """Fetch the list of devices from the API."""
        url = f"{self.base_url}/addons/shopro/user_device/groupList"
        data = {"language": self.lang}
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()
        except requests.RequestException as e:
            print(f"Error communicating with API: {e}")
            return None


    def get_device_status(self, device_id: str):
        """Get the current status of the device from the API."""
        url = f"{self.base_url}/addons/shopro/user_device/get_status"
        data = {"did": device_id, "language": self.lang}
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()
        except requests.RequestException as e:
            print(f"Error communicating with API: {e}")
            return None
        
    def get_devices_status(self, device_id_list: list[str]):
        """Fetch data from API for all devices."""
        devices_status = {}
        for device_id in device_id_list:
            device_status = self.get_device_status(device_id).get('data')
            devices_status[device_id] = device_status
        return devices_status
