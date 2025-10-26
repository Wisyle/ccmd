"""Interactive command editor for CCMD"""

import sys
from typing import Optional

from ccmd.core.registry import CommandRegistry
from ccmd.core.executor import sanitize_input


def launch_editor() -> int:
    """
    Launch interactive command editor

    Returns:
        Exit code
    """
    print("=" * 60)
    print("CCMD Command Editor")
    print("=" * 60)

    registry = CommandRegistry()

    while True:
        print("\nOptions:")
        print("  1. List all commands")
        print("  2. Add new command")
        print("  3. Edit existing command")
        print("  4. Delete command")
        print("  5. View command details")
        print("  6. Save and exit")
        print("  7. Exit without saving")

        choice = input("\nEnter choice (1-7): ").strip()

        if choice == '1':
            list_commands(registry)
        elif choice == '2':
            add_command(registry)
        elif choice == '3':
            edit_command(registry)
        elif choice == '4':
            delete_command(registry)
        elif choice == '5':
            view_command(registry)
        elif choice == '6':
            try:
                registry.save_commands()
                print("\n✓ Commands saved successfully!")
                return 0
            except Exception as e:
                print(f"\n✗ Failed to save commands: {e}")
                return 1
        elif choice == '7':
            print("\nExiting without saving...")
            return 0
        else:
            print("\n✗ Invalid choice. Please enter 1-7.")


def list_commands(registry: CommandRegistry):
    """List all commands"""
    commands = registry.list_commands()

    if not commands:
        print("\nNo commands registered.")
        return

    print("\nRegistered Commands:")
    print("-" * 60)
    for cmd in sorted(commands):
        cmd_def = registry.get_command(cmd)
        desc = cmd_def.get('description', 'No description')
        cmd_type = cmd_def.get('type', 'unknown')
        print(f"  {cmd:15} [{cmd_type:10}] - {desc}")


def add_command(registry: CommandRegistry):
    """Add a new command"""
    print("\n--- Add New Command ---")

    name = input("Command name: ").strip()
    if not name:
        print("✗ Command name cannot be empty")
        return

    if registry.command_exists(name):
        print(f"✗ Command '{name}' already exists")
        return

    description = input("Description: ").strip()
    action = input("Action (shell command): ").strip()

    if not action:
        print("✗ Action cannot be empty")
        return

    cmd_type = input("Type (git/system/navigation/custom) [custom]: ").strip() or "custom"

    command_def = {
        'description': description,
        'action': action,
        'type': cmd_type
    }

    # Check if action needs parameters
    if '{' in action and '}' in action:
        prompt = input("Prompt for parameter: ").strip()
        if prompt:
            command_def['prompt'] = prompt

    registry.add_command(name, command_def)
    print(f"\n✓ Command '{name}' added successfully!")


def edit_command(registry: CommandRegistry):
    """Edit an existing command"""
    print("\n--- Edit Command ---")

    commands = registry.list_commands()
    if not commands:
        print("No commands to edit.")
        return

    name = input("Command name to edit: ").strip()

    if not registry.command_exists(name):
        print(f"✗ Command '{name}' not found")
        return

    cmd_def = registry.get_command(name)

    print(f"\nCurrent definition:")
    print(f"  Description: {cmd_def.get('description', 'N/A')}")
    print(f"  Action: {cmd_def.get('action', 'N/A')}")
    print(f"  Type: {cmd_def.get('type', 'N/A')}")
    if 'prompt' in cmd_def:
        print(f"  Prompt: {cmd_def.get('prompt')}")

    print("\nEnter new values (press Enter to keep current value):")

    description = input(f"Description [{cmd_def.get('description', '')}]: ").strip()
    if description:
        cmd_def['description'] = description

    action = input(f"Action [{cmd_def.get('action', '')}]: ").strip()
    if action:
        cmd_def['action'] = action

    cmd_type = input(f"Type [{cmd_def.get('type', 'custom')}]: ").strip()
    if cmd_type:
        cmd_def['type'] = cmd_type

    # Check if action needs parameters
    if '{' in str(cmd_def.get('action', '')) and '}' in str(cmd_def.get('action', '')):
        prompt = input(f"Prompt [{cmd_def.get('prompt', '')}]: ").strip()
        if prompt:
            cmd_def['prompt'] = prompt

    registry.add_command(name, cmd_def)
    print(f"\n✓ Command '{name}' updated successfully!")


def delete_command(registry: CommandRegistry):
    """Delete a command"""
    print("\n--- Delete Command ---")

    commands = registry.list_commands()
    if not commands:
        print("No commands to delete.")
        return

    name = input("Command name to delete: ").strip()

    if not registry.command_exists(name):
        print(f"✗ Command '{name}' not found")
        return

    confirm = input(f"Are you sure you want to delete '{name}'? (yes/no): ").strip().lower()

    if confirm == 'yes':
        registry.remove_command(name)
        print(f"\n✓ Command '{name}' deleted successfully!")
    else:
        print("Deletion cancelled.")


def view_command(registry: CommandRegistry):
    """View command details"""
    print("\n--- View Command Details ---")

    commands = registry.list_commands()
    if not commands:
        print("No commands registered.")
        return

    name = input("Command name: ").strip()

    if not registry.command_exists(name):
        print(f"✗ Command '{name}' not found")
        return

    cmd_def = registry.get_command(name)

    print(f"\nCommand: {name}")
    print("-" * 60)
    for key, value in cmd_def.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    sys.exit(launch_editor())
