import cmd
import logging
import sys
from typing import Dict
from rich.console import Console


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