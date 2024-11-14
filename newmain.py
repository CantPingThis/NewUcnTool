import cmd
import logging
import sys
import yaml
from typing import Dict
from rich.console import Console

from network_framework import (
    DeviceCredentials
)

class NetworkShell(cmd.Cmd):
    intro = """
    Network Automation Shell
    Type 'help' or '?' to list commands.
    Type 'exit' or 'quit' to exit.
    """
    prompt = 'network-cli> '

    def __init__(self):
        super().__init__()
        self.console = Console()
        #self.manager = NetworkManager()
        self.config: Dict = {}
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format = '%(asctime)s - %(levelname)s - %(message)s',
            handlers = [
                logging.FileHandler('network_automation.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def do_load(self, arg):
        """
        Load configuration from a YAML file.
        Usage: load <config_file>
        """
        try:
            config_file = arg.strip() or "config.yaml"
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            self.initialize_devices()
            self.console.print(f"Successfully loaded configuration from {config_file}")
        except Exception as e:
            self.console.print(f"Error loading config fiel: {e}")

    def initialize_devices(self):
        """Initialize devices from loaded configuration file"""
        #self.console.print(self.config.get('devices', []))
        
        for device in self.config.get('devices', []):
            self.console.print(device)

            creds = DeviceCredentials(
                username = device['username'],
                password = device['password']
            )

            if device['type'] == 'ssh':
                connection = SSHConnection(device['host'], creds, device.get('device_type', 'cisco_ios'))
            else:
                self.logger.warning(f"Unknown device type: {device['type']}")
                continue

            self.manger.add_device(device['name'], connection)
            self.console.print(f"Initialized device: {device['name']}")



    def do_exit(self, arg):
        """Exit the network CLI."""
        return True
    
    def do_quit(self, arg):
        """Exit the network CLI."""
        return True
    
    def default(self, line):
        self.console.print(f"Unknow command: {line}")
        self.console.print("Type 'help' or '?' to list available commands.")
    
    def emptyline(self):
        """Do nothing on empty line."""
        pass

    def do_clear(self, arg):
        """Clear the screen."""
        self.console.clear()


def main():
    shell = NetworkShell()
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()