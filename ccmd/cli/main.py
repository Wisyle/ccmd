"""Main CLI entry point for CCMD"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ccmd.core.system_check import get_system_info
from ccmd.core.registry import CommandRegistry
from ccmd.core.parser import CommandParser
from ccmd.core.executor import CommandExecutor, CommandOutput, prompt_user
from ccmd.core.rollback import BackupManager, RollbackManager

# Global debug mode flag
DEBUG_MODE = False


def debug_print(message):
    """Print debug messages when debug mode is enabled"""
    if DEBUG_MODE:
        print(f"[DEBUG] {message}", file=sys.stderr)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CCMD - Cross-platform Command Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Management flags
    parser.add_argument('--install', action='store_true',
                       help='Install CCMD and add commands to shell')
    parser.add_argument('--uninstall', action='store_true',
                       help='Uninstall CCMD and remove shell integration')
    parser.add_argument('--restore', action='store_true',
                       help='Restore shell configuration from backup')
    parser.add_argument('--check', action='store_true',
                       help='Check system configuration')
    parser.add_argument('--edit', action='store_true',
                       help='Open interactive command editor')
    parser.add_argument('--test', action='store_true',
                       help='Test CCMD installation')
    parser.add_argument('--reload', action='store_true',
                       help='Reload commands from configuration')
    parser.add_argument('--list', action='store_true',
                       help='List all available commands')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode with verbose output')
    parser.add_argument('--exec', type=str,
                       help='Execute a raw command (internal use)')

    # Command execution
    parser.add_argument('command', nargs='?', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')

    args = parser.parse_args()

    # Set global debug mode
    global DEBUG_MODE
    DEBUG_MODE = args.debug

    # Handle debug mode if no other command
    if args.debug and not any([args.install, args.uninstall, args.restore,
                                args.check, args.edit, args.test, args.reload,
                                args.list, args.exec, args.command]):
        return handle_debug()

    # Handle management flags
    if args.install:
        return handle_install()
    elif args.uninstall:
        return handle_uninstall()
    elif args.restore:
        return handle_restore()
    elif args.check:
        return handle_check()
    elif args.edit:
        return handle_edit()
    elif args.test:
        return handle_test()
    elif args.reload:
        return handle_reload()
    elif args.list:
        return handle_list()
    elif args.exec:
        return handle_exec(args.exec)

    # Handle command execution
    if args.command:
        return handle_command(args.command, args.args)
    else:
        parser.print_help()
        return 0


def handle_install():
    """Handle installation"""
    from ccmd.cli.install import install_ccmd

    CommandOutput.print_info("Installing CCMD...")
    success, message = install_ccmd()

    if success:
        CommandOutput.print_success(message)
        return 0
    else:
        CommandOutput.print_error(message)
        return 1


def handle_uninstall():
    """Handle uninstallation"""
    from ccmd.cli.install import uninstall_ccmd

    CommandOutput.print_info("Uninstalling CCMD...")
    success, message = uninstall_ccmd()

    if success:
        CommandOutput.print_success(message)
        CommandOutput.print_info("Please restart your shell or run: source ~/.bashrc (or ~/.zshrc)")
        return 0
    else:
        CommandOutput.print_error(message)
        return 1


def handle_restore():
    """Handle restoration of shell configs"""
    CommandOutput.print_info("Restoring shell configuration from backup...")

    rollback = RollbackManager()
    results = rollback.restore_all()

    success_count = sum(1 for _, success, _ in results if success)

    if success_count > 0:
        CommandOutput.print_success(f"Restored {success_count} file(s)")
        for file_path, success, message in results:
            if success:
                CommandOutput.print_info(f"  {file_path}: {message}")
        return 0
    else:
        CommandOutput.print_error("No files were restored")
        return 1


def handle_check():
    """Handle system check"""
    CommandOutput.print_info("Checking system configuration...")

    system_info = get_system_info()
    print(f"\nSystem Information:")
    print(f"  OS: {system_info.os_type}")
    print(f"  Shell: {system_info.shell_type}")
    print(f"  RC File: {system_info.shell_rc_file}")
    print(f"  WSL: {system_info.is_wsl}")

    # Check if commands.yaml exists
    registry = CommandRegistry()
    if registry.config_path.exists():
        commands = registry.list_commands()
        print(f"\nRegistered Commands: {len(commands)}")
        for cmd in commands:
            cmd_def = registry.get_command(cmd)
            desc = cmd_def.get('description', 'No description')
            print(f"  - {cmd}: {desc}")
    else:
        CommandOutput.print_error(f"Commands file not found: {registry.config_path}")

    return 0


def handle_edit():
    """Handle interactive editor"""
    from ccmd.cli.editor import launch_editor

    return launch_editor()


def handle_test():
    """Handle test mode"""
    CommandOutput.print_info("Testing CCMD installation...")

    # Test system detection
    system_info = get_system_info()
    CommandOutput.print_success(f"System detection: {system_info.os_type} / {system_info.shell_type}")

    # Test registry
    registry = CommandRegistry()
    commands = registry.list_commands()
    CommandOutput.print_success(f"Command registry: {len(commands)} commands loaded")

    # Test parser
    parser = CommandParser(registry)
    CommandOutput.print_success("Command parser: OK")

    # Test executor
    executor = CommandExecutor(system_info)
    CommandOutput.print_success("Command executor: OK")

    CommandOutput.print_success("All tests passed!")
    return 0


def handle_reload():
    """Handle command reload"""
    CommandOutput.print_info("Reloading commands...")

    registry = CommandRegistry()
    registry.reload()
    commands = registry.list_commands()

    CommandOutput.print_success(f"Reloaded {len(commands)} commands")
    return 0


def handle_list():
    """List all commands"""
    registry = CommandRegistry()
    commands = registry.list_commands()

    if not commands:
        CommandOutput.print_info("No commands registered")
        return 0

    print("\nAvailable Commands:")
    for cmd in sorted(commands):
        cmd_def = registry.get_command(cmd)
        desc = cmd_def.get('description', 'No description')
        print(f"  {cmd:12} - {desc}")

    return 0


def handle_debug():
    """Display debug information"""
    print("\n" + "="*60)
    print("CCMD Debug Information")
    print("="*60)

    # System info
    system_info = get_system_info()
    print(f"\n[System]")
    print(f"  OS: {system_info.os_type}")
    print(f"  Shell: {system_info.shell_type}")
    print(f"  RC File: {system_info.shell_rc_file}")
    print(f"  WSL: {system_info.is_wsl}")

    # Environment
    print(f"\n[Environment]")
    ccmd_home = os.environ.get('CCMD_HOME', 'Not set')
    print(f"  CCMD_HOME: {ccmd_home}")
    print(f"  PATH: {os.environ.get('PATH', 'Not set')[:100]}...")
    print(f"  Python: {sys.executable}")
    print(f"  Python Version: {sys.version.split()[0]}")

    # Installation
    print(f"\n[Installation]")
    install_dir = Path(__file__).parent.parent.parent.resolve()
    print(f"  Install Directory: {install_dir}")
    print(f"  run.py exists: {(install_dir / 'run.py').exists()}")
    print(f"  commands.yaml exists: {(install_dir / 'commands.yaml').exists()}")

    # Registry
    print(f"\n[Command Registry]")
    try:
        registry = CommandRegistry()
        commands = registry.list_commands()
        print(f"  Config Path: {registry.config_path}")
        print(f"  Commands Loaded: {len(commands)}")
        print(f"  Commands: {', '.join(sorted(commands))}")
    except Exception as e:
        print(f"  Error: {e}")

    # Version
    print(f"\n[Version]")
    try:
        from ccmd import __version__
        print(f"  CCMD Version: {__version__}")
    except:
        print(f"  CCMD Version: Unknown")

    print("\n" + "="*60)
    return 0


def handle_exec(command: str):
    """Execute a raw command"""
    system_info = get_system_info()
    executor = CommandExecutor(system_info)

    returncode, stdout, stderr = executor.execute(command)
    CommandOutput.print_command_output(stdout, stderr)

    return returncode


def handle_command(command_name: str, args: list):
    """Handle command execution"""
    debug_print(f"Executing command: {command_name} with args: {args}")

    # Initialize components
    system_info = get_system_info()
    debug_print(f"System: {system_info.os_type}, Shell: {system_info.shell_type}")

    registry = CommandRegistry()
    debug_print(f"Registry loaded from: {registry.config_path}")

    parser = CommandParser(registry)
    executor = CommandExecutor(system_info)

    # Parse command
    cmd_name, subcommand, parameters = parser.parse([command_name] + args)
    debug_print(f"Parsed - Command: {cmd_name}, Subcommand: {subcommand}, Parameters: {parameters}")

    if 'error' in parameters:
        CommandOutput.print_error(parameters['error'])
        return 1

    # Check if command needs prompt
    if parameters.get('needs_prompt'):
        prompt_text = parameters.get('prompt', 'Enter value')
        debug_print(f"Prompting user: {prompt_text}")
        user_input = prompt_user(prompt_text)
        if not user_input:
            CommandOutput.print_error("No input provided")
            return 1

        # Get parameter name from command definition
        cmd_def = registry.get_command(cmd_name)
        action = cmd_def.get('action', '')
        param_name = parser._extract_param_name(action)
        if param_name:
            parameters[param_name] = user_input
        parameters.pop('needs_prompt', None)
        parameters.pop('prompt', None)

    # Get action
    action = parser.get_action(cmd_name, subcommand, system_info.os_type)
    debug_print(f"Action template: {action}")

    if not action:
        CommandOutput.print_error(f"No action defined for command: {cmd_name}")
        return 1

    # Format action with parameters
    formatted_action = parser.format_action(action, parameters)
    debug_print(f"Formatted action: {formatted_action}")

    # Check if it's a navigation command (cd)
    if formatted_action.startswith('cd '):
        # For cd commands, we need to output the command for shell evaluation
        # The actual directory change must happen in the calling shell
        debug_print("Navigation command detected, outputting for shell evaluation")
        print(formatted_action)
        return 0

    # Execute command
    debug_print("Executing command...")
    returncode, stdout, stderr = executor.execute(formatted_action)
    debug_print(f"Return code: {returncode}")

    CommandOutput.print_command_output(stdout, stderr)

    return returncode


if __name__ == "__main__":
    sys.exit(main())
