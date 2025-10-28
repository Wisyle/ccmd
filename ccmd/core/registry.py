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

        # Path for custom user commands
        self.custom_config_path = Path.home() / ".ccmd" / "custom_commands.yaml"

        self.commands: Dict[str, Dict[str, Any]] = {}
        self.custom_commands: Dict[str, Dict[str, Any]] = {}
        self._load_commands()
        self._load_custom_commands()

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
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and 'commands' in data:
                    self.commands = data['commands']
                else:
                    self.commands = {}
        except Exception as e:
            raise RuntimeError(f"Failed to load commands from {self.config_path}: {e}")

    def _load_custom_commands(self):
        """Load custom user commands from personal config"""
        if not self.custom_config_path.exists():
            self.custom_commands = {}
            return

        try:
            with open(self.custom_config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and 'commands' in data:
                    self.custom_commands = data['commands']
                else:
                    self.custom_commands = {}
        except Exception as e:
            # Don't raise error for custom commands, just log warning
            print(f"Warning: Failed to load custom commands from {self.custom_config_path}: {e}")
            self.custom_commands = {}

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
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

        except Exception as e:
            raise RuntimeError(f"Failed to save commands to {self.config_path}: {e}")

    def save_custom_commands(self):
        """Save custom user commands to personal config"""
        try:
            # Ensure parent directory exists
            self.custom_config_path.parent.mkdir(parents=True, exist_ok=True)

            # Create backup before saving
            if self.custom_config_path.exists():
                backup_path = self.custom_config_path.with_suffix('.yaml.bak')
                shutil.copy2(self.custom_config_path, backup_path)

            # Save custom commands
            data = {'commands': self.custom_commands}
            with open(self.custom_config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

        except Exception as e:
            raise RuntimeError(f"Failed to save custom commands to {self.custom_config_path}: {e}")

    def get_command(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a command definition by name
        Custom commands override default commands if same name exists

        Args:
            name: Command name

        Returns:
            Command definition dict or None if not found
        """
        # Check custom commands first (they override defaults)
        if name in self.custom_commands:
            return self.custom_commands.get(name)
        return self.commands.get(name)

    def has_command(self, name: str) -> bool:
        """
        Check if a command exists (v1.1.2 - for command composability)

        Args:
            name: Command name

        Returns:
            True if command exists (in custom or default commands)
        """
        return name in self.custom_commands or name in self.commands

    def add_command(self, name: str, command_def: Dict[str, Any], is_custom: bool = False):
        """
        Add or update a command definition (v1.1.2 - Security hardened)

        Args:
            name: Command name
            command_def: Command definition dictionary
            is_custom: If True, adds to custom commands (user-defined)

        Security:
            Custom commands cannot use privileged types ('system', 'internal').
            This prevents abuse of shell=True execution path.
        """
        if is_custom:
            # SECURITY: Force custom commands to use 'custom' type only
            # Prevents users from bypassing safe execution by marking commands as 'system'
            command_def['type'] = 'custom'
            self.custom_commands[name] = command_def
        else:
            self.commands[name] = command_def

    def remove_command(self, name: str) -> bool:
        """
        Remove a command definition
        Removes from custom commands first, then default commands

        Args:
            name: Command name

        Returns:
            True if command was removed, False if not found
        """
        # Try removing from custom commands first
        if name in self.custom_commands:
            del self.custom_commands[name]
            return True

        if name in self.commands:
            del self.commands[name]
            return True

        return False

    def list_commands(self) -> List[str]:
        """Get list of all command names (default + custom, custom overrides)"""
        # Merge commands, custom overrides defaults
        all_cmds = {**self.commands, **self.custom_commands}
        return list(all_cmds.keys())

    def list_custom_commands(self) -> List[str]:
        """Get list of custom command names only"""
        return list(self.custom_commands.keys())

    def is_custom_command(self, name: str) -> bool:
        """Check if a command is a custom user command"""
        return name in self.custom_commands

    def get_all_commands(self) -> Dict[str, Dict[str, Any]]:
        """Get all command definitions (default + custom, custom overrides)"""
        # Merge commands, custom overrides defaults
        return {**self.commands, **self.custom_commands}

    def command_exists(self, name: str) -> bool:
        """Check if a command exists (in default or custom commands)"""
        return name in self.commands or name in self.custom_commands

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
        """Reload commands from files (both default and custom)"""
        self._load_commands()
        self._load_custom_commands()


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
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(default_commands, f, default_flow_style=False, sort_keys=False)
