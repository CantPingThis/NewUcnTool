from abc import ABC, abstractmethod
import requests
from netmiko import ConnectHandler
from typing import Dict, List, Any, Optional
import json
from dataclasses import dataclass

@dataclass
class DeviceCredentials:
    username: str
    password: str
    enable_secret: Optional[str] = None

class DeviceConnection(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def execute_command(self, command: str) -> str:
        pass

class SSHConnection(DeviceConnection):
    def __init__(self, host: str, credentials: DeviceCredentials, device_type: str = "cisco_ios"):
        self.host = host
        self.credentials = credentials
        self.device_type = device_type
        self.connection = None

    def connect(self) -> None:
        device = {
            'device_type': self.device_type,
            'host': self.host,
            'username': self.credentials.username,
            'password': self.credentials.password,
            'secret': self.credentials.enable_secret
        }
        self.connection = ConnectHandler(**device)
        if self.credentials.enable_secret:
            self.connection.enable()

    def disconnect(self) -> None:
        if self.connection:
            self.connection.disconnect()

    def execute_command(self, command: str) -> str:
        return self.connection.send_command(command)

class APIConnection(DeviceConnection):
    def __init__(self, base_url: str, credentials: DeviceCredentials):
        self.base_url = base_url.rstrip('/')
        self.credentials = credentials
        self.session = requests.Session()
        self.token = None

    def connect(self) -> None:
        # This is a generic implementation - modify based on specific API requirements
        auth_endpoint = f"{self.base_url}/auth"
        response = self.session.post(
            auth_endpoint,
            json={
                "username": self.credentials.username,
                "password": self.credentials.password
            }
        )
        response.raise_for_status()
        self.token = response.json().get("token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def disconnect(self) -> None:
        self.session.close()

    def execute_command(self, endpoint: str) -> str:
        response = self.session.get(f"{self.base_url}/{endpoint}")
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)

class NetworkManager:
    def __init__(self):
        self.devices: Dict[str, DeviceConnection] = {}

    def add_device(self, name: str, connection: DeviceConnection) -> None:
        self.devices[name] = connection

    def connect_all(self) -> None:
        for device in self.devices.values():
            device.connect()

    def disconnect_all(self) -> None:
        for device in self.devices.values():
            device.disconnect()

    def execute_command_on_devices(self, devices: List[str], command: str) -> Dict[str, str]:
        results = {}
        for device_name in devices:
            if device_name in self.devices:
                try:
                    results[device_name] = self.devices[device_name].execute_command(command)
                except Exception as e:
                    results[device_name] = f"Error: {str(e)}"
            else:
                results[device_name] = "Error: Device not found"
        return results

class CiscoISE(APIConnection):
    def __init__(self, base_url: str, credentials: DeviceCredentials):
        super().__init__(base_url, credentials)

    def get_endpoints(self) -> str:
        return self.execute_command("endpoints")

    def get_endpoint_groups(self) -> str:
        return self.execute_command("endpoint-groups")

class CiscoDNACenter(APIConnection):
    def __init__(self, base_url: str, credentials: DeviceCredentials):
        super().__init__(base_url, credentials)

    def get_devices(self) -> str:
        return self.execute_command("devices")

    def get_sites(self) -> str:
        return self.execute_command("sites")