"""SSH connection manager for CCMD"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ccmd.core.registry import CommandRegistry


class SSHManager:
    """Manage SSH connection aliases"""

    def __init__(self, registry: Optional[CommandRegistry] = None):
        """
        Initialize SSH manager

        Args:
            registry: CommandRegistry instance
        """
        self.registry = registry or CommandRegistry()

    def add_ssh_alias(self, alias: str, host: str, user: Optional[str] = None,
                     port: int = 22, key_file: Optional[str] = None) -> Tuple[bool, str]:
        """
        Add an SSH connection alias

        Args:
            alias: Alias name for the connection
            host: Hostname or IP address
            user: SSH username
            port: SSH port (default 22)
            key_file: Path to SSH key file

        Returns:
            Tuple of (success, message)
        """
        # Build SSH command
        ssh_cmd = "ssh"

        if port != 22:
            ssh_cmd += f" -p {port}"

        if key_file:
            ssh_cmd += f' -i "{key_file}"'

        if user:
            ssh_cmd += f" {user}@{host}"
        else:
            ssh_cmd += f" {host}"

        # Create command definition
        command_def = {
            'description': f'SSH to {host}',
            'action': ssh_cmd,
            'type': 'ssh',
            'ssh_config': {
                'host': host,
                'user': user,
                'port': port,
                'key_file': key_file
            }
        }

        # Add to registry
        self.registry.add_command(alias, command_def)

        try:
            self.registry.save_commands()
            return True, f"SSH alias '{alias}' added successfully"
        except Exception as e:
            return False, f"Failed to save SSH alias: {e}"

    def remove_ssh_alias(self, alias: str) -> Tuple[bool, str]:
        """
        Remove an SSH alias

        Args:
            alias: Alias name to remove

        Returns:
            Tuple of (success, message)
        """
        if not self.registry.command_exists(alias):
            return False, f"SSH alias '{alias}' not found"

        cmd_def = self.registry.get_command(alias)
        if cmd_def.get('type') != 'ssh':
            return False, f"'{alias}' is not an SSH alias"

        self.registry.remove_command(alias)

        try:
            self.registry.save_commands()
            return True, f"SSH alias '{alias}' removed successfully"
        except Exception as e:
            return False, f"Failed to remove SSH alias: {e}"

    def list_ssh_aliases(self) -> List[Dict]:
        """
        List all SSH aliases

        Returns:
            List of SSH alias definitions
        """
        ssh_aliases = []

        for cmd_name in self.registry.list_commands():
            cmd_def = self.registry.get_command(cmd_name)
            if cmd_def.get('type') == 'ssh':
                ssh_config = cmd_def.get('ssh_config', {})
                ssh_aliases.append({
                    'alias': cmd_name,
                    'host': ssh_config.get('host'),
                    'user': ssh_config.get('user'),
                    'port': ssh_config.get('port', 22),
                    'key_file': ssh_config.get('key_file'),
                    'description': cmd_def.get('description', '')
                })

        return ssh_aliases

    def get_ssh_alias(self, alias: str) -> Optional[Dict]:
        """
        Get SSH alias details

        Args:
            alias: Alias name

        Returns:
            SSH alias details or None
        """
        if not self.registry.command_exists(alias):
            return None

        cmd_def = self.registry.get_command(alias)
        if cmd_def.get('type') != 'ssh':
            return None

        ssh_config = cmd_def.get('ssh_config', {})
        return {
            'alias': alias,
            'host': ssh_config.get('host'),
            'user': ssh_config.get('user'),
            'port': ssh_config.get('port', 22),
            'key_file': ssh_config.get('key_file'),
            'description': cmd_def.get('description', ''),
            'command': cmd_def.get('action')
        }


def launch_ssh_manager() -> int:
    """
    Launch interactive SSH manager

    Returns:
        Exit code
    """
    print("=" * 60)
    print("CCMD SSH Manager")
    print("=" * 60)

    manager = SSHManager()

    while True:
        print("\nOptions:")
        print("  1. List SSH aliases")
        print("  2. Add SSH alias")
        print("  3. Remove SSH alias")
        print("  4. View SSH alias details")
        print("  5. Exit")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == '1':
            list_ssh_aliases_interactive(manager)
        elif choice == '2':
            add_ssh_alias_interactive(manager)
        elif choice == '3':
            remove_ssh_alias_interactive(manager)
        elif choice == '4':
            view_ssh_alias_interactive(manager)
        elif choice == '5':
            print("\nExiting SSH manager...")
            return 0
        else:
            print("\n✗ Invalid choice. Please enter 1-5.")


def list_ssh_aliases_interactive(manager: SSHManager):
    """List SSH aliases interactively"""
    aliases = manager.list_ssh_aliases()

    if not aliases:
        print("\nNo SSH aliases configured.")
        return

    print("\nSSH Aliases:")
    print("-" * 60)
    for alias_info in aliases:
        user_part = f"{alias_info['user']}@" if alias_info['user'] else ""
        port_part = f":{alias_info['port']}" if alias_info['port'] != 22 else ""
        print(f"  {alias_info['alias']:15} - {user_part}{alias_info['host']}{port_part}")
        if alias_info['description']:
            print(f"                    ({alias_info['description']})")


def add_ssh_alias_interactive(manager: SSHManager):
    """Add SSH alias interactively"""
    print("\n--- Add SSH Alias ---")

    alias = input("Alias name: ").strip()
    if not alias:
        print("✗ Alias name cannot be empty")
        return

    host = input("Hostname/IP: ").strip()
    if not host:
        print("✗ Hostname cannot be empty")
        return

    user = input("Username (optional): ").strip() or None
    port_str = input("Port [22]: ").strip()
    port = int(port_str) if port_str else 22

    key_file = input("SSH key file path (optional): ").strip() or None

    success, message = manager.add_ssh_alias(alias, host, user, port, key_file)

    if success:
        print(f"\n✓ {message}")
    else:
        print(f"\n✗ {message}")


def remove_ssh_alias_interactive(manager: SSHManager):
    """Remove SSH alias interactively"""
    print("\n--- Remove SSH Alias ---")

    alias = input("Alias name to remove: ").strip()
    if not alias:
        print("✗ Alias name cannot be empty")
        return

    confirm = input(f"Remove SSH alias '{alias}'? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Removal cancelled.")
        return

    success, message = manager.remove_ssh_alias(alias)

    if success:
        print(f"\n✓ {message}")
    else:
        print(f"\n✗ {message}")


def view_ssh_alias_interactive(manager: SSHManager):
    """View SSH alias details interactively"""
    print("\n--- SSH Alias Details ---")

    alias = input("Alias name: ").strip()
    if not alias:
        print("✗ Alias name cannot be empty")
        return

    alias_info = manager.get_ssh_alias(alias)

    if not alias_info:
        print(f"✗ SSH alias '{alias}' not found")
        return

    print(f"\nAlias: {alias_info['alias']}")
    print("-" * 60)
    print(f"Host: {alias_info['host']}")
    if alias_info['user']:
        print(f"User: {alias_info['user']}")
    print(f"Port: {alias_info['port']}")
    if alias_info['key_file']:
        print(f"Key file: {alias_info['key_file']}")
    print(f"Description: {alias_info['description']}")
    print(f"Command: {alias_info['command']}")


if __name__ == "__main__":
    sys.exit(launch_ssh_manager())
