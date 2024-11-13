#!/usr/bin/env python3
import cmd
import yaml
import sys
import shlex
from typing import Dict, List, Optional
import logging
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm

# Import the network framework
from network_framework import (
    DeviceCredentials, 
    SSHConnection, 
    NetworkManager, 
    CiscoISE, 
    CiscoDNACenter
)

class NetworkShell(cmd.Cmd):
    intro = """
    Network Automation Shell
    Type 'help' or '?' to list commands.
    Type 'exit' or 'quit' to exit.
    """
    prompt = '[cyan]network-cli[/cyan]> '

    def __init__(self):
        super().__init__()
        self.console = Console()
        #self.manager = NetworkManager()
        self.config: Dict = {}
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
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
            self.console.print(f"[green]Successfully loaded configuration from {config_file}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error loading config file: {e}[/red]")

    def initialize_devices(self):
        """Initialize devices from loaded configuration."""
        for device in self.config.get('devices', []):
            creds = DeviceCredentials(
                username=device['username'],
                password=device['password'],
                enable_secret=device.get('enable_secret')
            )
            
            if device['type'] == 'ssh':
                connection = SSHConnection(device['host'], creds, device.get('device_type', 'cisco_ios'))
            elif device['type'] == 'ise':
                connection = CiscoISE(device['host'], creds)
            elif device['type'] == 'dnac':
                connection = CiscoDNACenter(device['host'], creds)
            else:
                self.logger.warning(f"Unknown device type: {device['type']}")
                continue
                
            self.manager.add_device(device['name'], connection)
            self.console.print(f"[green]Initialized device: {device['name']}[/green]")

    def do_devices(self, arg):
        """
        List all configured devices.
        Usage: devices
        """
        table = Table(title="Configured Devices")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Host", style="blue")
        
        for device in self.config.get('devices', []):
            table.add_row(
                device['name'],
                device['type'],
                device['host']
            )
        
        self.console.print(table)

    def do_exec(self, arg):
        """
        Execute command on specified devices.
        Usage: exec <device1,device2,...> <command>
        Example: exec switch1,switch2 show version
        """
        try:
            args = shlex.split(arg)
            if len(args) < 2:
                self.console.print("[red]Error: Please specify devices and command[/red]")
                return
            
            devices = args[0].split(',')
            command = ' '.join(args[1:])
            
            self.console.print(f"[yellow]Executing '{command}' on {', '.join(devices)}...[/yellow]")
            
            self.manager.connect_all()
            results = self.manager.execute_command_on_devices(devices, command)
            
            table = Table(title=f"Command Results: {command}")
            table.add_column("Device", style="cyan")
            table.add_column("Output", style="green")
            
            for device, output in results.items():
                table.add_row(device, output)
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error executing command: {e}[/red]")
        finally:
            self.manager.disconnect_all()

    def do_ise(self, arg):
        """
        Execute ISE-specific commands.
        Usage: ise <endpoints|groups>
        """
        if not arg:
            self.console.print("[red]Please specify action: endpoints or groups[/red]")
            return
            
        action = arg.strip()
        if action not in ['endpoints', 'groups']:
            self.console.print("[red]Invalid action. Use 'endpoints' or 'groups'[/red]")
            return
            
        for device in self.manager.devices.values():
            if isinstance(device, CiscoISE):
                try:
                    device.connect()
                    if action == 'endpoints':
                        result = device.get_endpoints()
                    else:
                        result = device.get_endpoint_groups()
                    syntax = Syntax(result, "json", theme="monokai")
                    self.console.print(syntax)
                finally:
                    device.disconnect()

    def do_dnac(self, arg):
        """
        Execute DNA Center-specific commands.
        Usage: dnac <devices|sites>
        """
        if not arg:
            self.console.print("[red]Please specify action: devices or sites[/red]")
            return
            
        action = arg.strip()
        if action not in ['devices', 'sites']:
            self.console.print("[red]Invalid action. Use 'devices' or 'sites'[/red]")
            return
            
        for device in self.manager.devices.values():
            if isinstance(device, CiscoDNACenter):
                try:
                    device.connect()
                    if action == 'devices':
                        result = device.get_devices()
                    else:
                        result = device.get_sites()
                    syntax = Syntax(result, "json", theme="monokai")
                    self.console.print(syntax)
                finally:
                    device.disconnect()

    def do_exit(self, arg):
        """Exit the network CLI."""
        return True
        
    def do_quit(self, arg):
        """Exit the network CLI."""
        return True

    def default(self, line):
        self.console.print(f"[red]Unknown command: {line}[/red]")
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