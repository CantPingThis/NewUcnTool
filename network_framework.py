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

    def disconnect(self) -> None:
        pass

    def execute_command(self,command: str) -> str:
        pass

class SSHConnection(DeviceConnection):
    def __init__(self, host: str, credentials: DeviceCredentials, device_type: str = "cisco_ios"):
        self.host = host
        self.credentials = credentials
        self.device_type = device_type
        self.connection = None
    
    def connect(self):
        device = {
            'device_type': self.device_type,
            'host': self.host,
            'username': self.credentials.username,
            'password': self.credentials.password,
            'enable_secret': self.credentials.enable_secret
        }
        self.connection = ConnectHandler(**device)
        if self.credentials.enable_secret:
            self.connection.enable()

    def disconnect(self):
        self.connection.disconnect()

    def execute_command(self, command):
        return self.connection.send_command(command)