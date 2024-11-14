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

