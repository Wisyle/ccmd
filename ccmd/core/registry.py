"""Command registry module for loading and saving command definitions"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil


class CommandRegistry:
    """Manages command definitions stored in YAML"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the command registry

        Args:
            config_path: Path to commands.yaml file. If None, uses default location.
        """
        if config_path is None:
            # Default to commands.yaml in the ccmd installation directory
            self.config_path = self._get_default_config_path()
        else:
            self.config_path = Path(config_path)

        self.commands: Dict[str, Dict[str, Any]] = {}
        self._load_commands()

    def _get_default_config_path(self) -> Path:
        """Get the default config path"""
        # Look for commands.yaml in the same directory as this file
        module_dir = Path(__file__).parent.parent.parent
        config_file = module_dir / "commands.yaml"

        # If not found, check user's home directory
        if not config_file.exists():
            home_config = Path.home() / ".ccmd" / "commands.yaml"
            if home_config.exists():
                return home_config

        return config_file

    def _load_commands(self):
        """Load commands from YAML file"""
        if not self.config_path.exists():
            self.commands = {}
            return

        try:
            with open(self.config_path, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'commands' in data:
                    self.commands = data['commands']
                else:
                    self.commands = {}
        except Exception as e:
            raise RuntimeError(f"Failed to load commands from {self.config_path}: {e}")

    def save_commands(self):
        """Save commands to YAML file"""
        try:
            # Ensure parent directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Create backup before saving
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix('.yaml.bak')
                shutil.copy2(self.config_path, backup_path)

            # Save commands
            data = {'commands': self.commands}
            with open(self.config_path, 'w') as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

        except Exception as e:
            raise RuntimeError(f"Failed to save commands to {self.config_path}: {e}")

    def get_command(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a command definition by name

        Args:
            name: Command name

        Returns:
            Command definition dict or None if not found
        """
        return self.commands.get(name)

    def add_command(self, name: str, command_def: Dict[str, Any]):
        """
        Add or update a command definition

        Args:
            name: Command name
            command_def: Command definition dictionary
        """
        self.commands[name] = command_def

    def remove_command(self, name: str) -> bool:
        """
        Remove a command definition

        Args:
            name: Command name

        Returns:
            True if command was removed, False if not found
        """
        if name in self.commands:
            del self.commands[name]
            return True
        return False

    def list_commands(self) -> List[str]:
        """Get list of all command names"""
        return list(self.commands.keys())

    def get_all_commands(self) -> Dict[str, Dict[str, Any]]:
        """Get all command definitions"""
        return self.commands.copy()

    def command_exists(self, name: str) -> bool:
        """Check if a command exists"""
        return name in self.commands

    def validate_command(self, command_def: Dict[str, Any]) -> bool:
        """
        Validate a command definition

        Args:
            command_def: Command definition to validate

        Returns:
            True if valid, raises ValueError if invalid
        """
        required_fields = ['action']

        for field in required_fields:
            if field not in command_def:
                raise ValueError(f"Command definition missing required field: {field}")

        # Validate action type
        action = command_def.get('action')
        if not isinstance(action, (str, dict)):
            raise ValueError("Command action must be a string or dictionary")

        return True

    def reload(self):
        """Reload commands from file"""
        self._load_commands()


def create_default_config(path: Path):
    """
    Create a default commands.yaml file

    Args:
        path: Path where to create the config file
    """
    default_commands = {
        'commands': {
            'go': {
                'description': 'Navigate to common directories',
                'action': {
                    'downloads': 'cd ~/Downloads',
                    'documents': 'cd ~/Documents',
                    'desktop': 'cd ~/Desktop',
                    'home': 'cd ~',
                },
                'type': 'navigation'
            },
            'push': {
                'description': 'Git add, commit, and push',
                'action': 'git add . && git commit -m "{message}" && git push',
                'type': 'git',
                'prompt': 'Enter commit message'
            },
            'cpu': {
                'description': 'Show CPU usage',
                'action': {
                    'linux': 'top -bn1 | grep "Cpu(s)" | sed "s/.*, *\\([0-9.]*\\)%* id.*/\\1/" | awk \'{print 100 - $1"%"}\'',
                    'macos': 'top -l 1 | grep "CPU usage"',
                    'windows': 'powershell "Get-Counter \'\\Processor(_Total)\\% Processor Time\' | Select-Object -ExpandProperty CounterSamples | Select-Object CookedValue"'
                },
                'type': 'system'
            },
            'mem': {
                'description': 'Show memory usage',
                'action': {
                    'linux': 'free -h',
                    'macos': 'vm_stat',
                    'windows': 'powershell "Get-Counter \'\\Memory\\Available MBytes\' | Select-Object -ExpandProperty CounterSamples | Select-Object CookedValue"'
                },
                'type': 'system'
            },
            'proc': {
                'description': 'Show running processes',
                'action': {
                    'linux': 'ps aux',
                    'macos': 'ps aux',
                    'windows': 'tasklist'
                },
                'type': 'system'
            },
            'kap': {
                'description': 'Kill a process by name or PID',
                'action': {
                    'linux': 'kill -9 {pid}',
                    'macos': 'kill -9 {pid}',
                    'windows': 'taskkill /F /PID {pid}'
                },
                'type': 'system',
                'prompt': 'Enter process ID'
            },
            'update': {
                'description': 'Update CCMD commands from config',
                'action': 'ccmd --reload',
                'type': 'internal'
            },
            'restore': {
                'description': 'Restore shell configuration from backup',
                'action': 'ccmd --restore',
                'type': 'internal'
            }
        }
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        yaml.safe_dump(default_commands, f, default_flow_style=False, sort_keys=False)
