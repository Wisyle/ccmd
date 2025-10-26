"""Main CLI entry point for CCMD"""

import argparse
import sys
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ccmd.core.system_check import get_system_info
from ccmd.core.registry import CommandRegistry
from ccmd.core.parser import CommandParser
from ccmd.core.executor import CommandExecutor, CommandOutput, prompt_user
from ccmd.core.rollback import BackupManager, RollbackManager

# Global debug mode flag
DEBUG_MODE = False

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    PURPLE = '\033[35m'
    ORANGE = '\033[33m'


def debug_print(message):
    """Print debug messages when debug mode is enabled"""
    if DEBUG_MODE:
        print(f"[DEBUG] {message}", file=sys.stderr)


def typewriter(text, delay=0.03, color=Colors.END):
    """Print text with typewriter effect"""
    for char in text:
        sys.stdout.write(color + char + Colors.END)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def show_loading_dots(message, color=Colors.CYAN, dots=3, delay=0.3):
    """Show a message with animated loading dots"""
    sys.stdout.write(f"{color}{message}{Colors.END}")
    sys.stdout.flush()
    for _ in range(dots):
        time.sleep(delay)
        sys.stdout.write(f"{color}.{Colors.END}")
        sys.stdout.flush()
    print()


def show_command_feedback(command, action_text, color=Colors.CYAN):
    """Show colorful feedback for command execution"""
    # Command-specific colors
    command_colors = {
        'go': Colors.GREEN,
        'push': Colors.BLUE,
        'cpu': Colors.YELLOW,
        'mem': Colors.YELLOW,
        'proc': Colors.PURPLE,
        'kap': Colors.RED,
        'update': Colors.CYAN,
        'restore': Colors.ORANGE,
        'uninstall': Colors.RED,
    }

    cmd_color = command_colors.get(command, Colors.CYAN)
    show_loading_dots(f"{cmd_color}→ {action_text}{Colors.END}", color=cmd_color, dots=3, delay=0.2)


def get_username():
    """Get the current username"""
    return os.getenv('USER') or os.getenv('USERNAME') or 'User'


def get_greeting():
    """Get time-based greeting"""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


def get_process_count():
    """Get number of running processes"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return len(result.stdout.strip().split('\n')) - 1  # Minus header
    except:
        return 0


def get_high_memory_processes(limit=3):
    """Get top memory consuming processes"""
    try:
        result = subprocess.run(
            ['ps', 'aux', '--sort=-%mem'],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().split('\n')[1:limit+1]  # Skip header, get top N
        processes = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 11:
                processes.append({
                    'pid': parts[1],
                    'mem': parts[3],
                    'command': ' '.join(parts[10:])[:50]  # Limit command length
                })
        return processes
    except:
        return []


def save_command_history(command):
    """Save command to history file"""
    history_file = Path.home() / '.ccmd' / 'history.txt'
    history_file.parent.mkdir(exist_ok=True)

    try:
        with open(history_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()}|{command}\n")
    except:
        pass


def get_recent_commands(limit=5):
    """Get recent commands from history"""
    history_file = Path.home() / '.ccmd' / 'history.txt'

    if not history_file.exists():
        return []

    try:
        with open(history_file, 'r') as f:
            lines = f.readlines()

        recent = []
        for line in reversed(lines[-limit:]):
            parts = line.strip().split('|')
            if len(parts) == 2:
                recent.append(parts[1])
        return recent
    except:
        return []


def get_favorite_commands(limit=5):
    """Get most used commands"""
    history_file = Path.home() / '.ccmd' / 'history.txt'

    if not history_file.exists():
        return []

    try:
        with open(history_file, 'r') as f:
            lines = f.readlines()

        command_counts = {}
        for line in lines:
            parts = line.strip().split('|')
            if len(parts) == 2:
                cmd = parts[1]
                command_counts[cmd] = command_counts.get(cmd, 0) + 1

        # Sort by count and return top N
        sorted_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)
        return [(cmd, count) for cmd, count in sorted_commands[:limit]]
    except:
        return []


def search_directory(dir_name: str) -> str:
    """
    Search for a directory by name in common locations

    Args:
        dir_name: Directory name to search for

    Returns:
        Full path to directory if found, None otherwise
    """
    import subprocess

    # Common search locations
    search_paths = [
        os.path.expanduser("~"),
        "/mnt/c/Users/rober",
        "/mnt/c/Users/rober/Downloads",
        "/mnt/c/Users/rober/targlobal",
    ]

    debug_print(f"Searching for directory: {dir_name}")

    for base_path in search_paths:
        if not os.path.exists(base_path):
            continue

        # Try to find the directory with find command (faster)
        try:
            result = subprocess.run(
                ["find", base_path, "-maxdepth", "3", "-type", "d", "-iname", dir_name],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                paths = result.stdout.strip().split('\n')
                # Return first match
                first_match = paths[0]
                debug_print(f"Found directory: {first_match}")
                return first_match
        except Exception as e:
            debug_print(f"Search error in {base_path}: {e}")
            continue

    debug_print(f"Directory '{dir_name}' not found")
    return None


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


def handle_hi():
    """Display personalized dashboard with system overview"""
    username = get_username()
    greeting = get_greeting()

    # Greeting with typewriter effect
    print()
    typewriter(f"{greeting}, Master {username}!", delay=0.04, color=Colors.BOLD + Colors.CYAN)
    time.sleep(0.3)
    typewriter("I hope you are having a great day!", delay=0.03, color=Colors.GREEN)
    print()

    # System Overview Header
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}  SYSTEM OVERVIEW{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}\n")

    # System Information
    system_info = get_system_info()
    print(f"{Colors.BOLD}{Colors.BLUE}[Machine Details]{Colors.END}")
    print(f"  {Colors.CYAN}OS:{Colors.END} {system_info.os_type}")
    print(f"  {Colors.CYAN}Shell:{Colors.END} {system_info.shell_type}")
    print(f"  {Colors.CYAN}WSL:{Colors.END} {'Yes' if system_info.is_wsl else 'No'}")
    print()

    # Available Commands
    registry = CommandRegistry()
    commands = registry.list_commands()
    print(f"{Colors.BOLD}{Colors.BLUE}[Available Commands]{Colors.END} {Colors.GREEN}({len(commands)} total){Colors.END}")
    for cmd in sorted(commands):
        cmd_def = registry.get_command(cmd)
        desc = cmd_def.get('description', 'No description')
        print(f"  {Colors.YELLOW}{cmd:12}{Colors.END} - {desc[:50]}")
    print()

    # Running Processes
    proc_count = get_process_count()
    print(f"{Colors.BOLD}{Colors.BLUE}[System Processes]{Colors.END}", end=" ")

    if proc_count > 100:
        print(f"{Colors.RED}({proc_count} running){Colors.END}")
        print(f"  {Colors.YELLOW}⚠  Quick Note:{Colors.END} You have {Colors.RED}{proc_count}{Colors.END} processes running.")
        print(f"  {Colors.YELLOW}   You might want to check and stop unnecessary ones.{Colors.END}")
    else:
        print(f"{Colors.GREEN}({proc_count} running){Colors.END}")
        print(f"  {Colors.GREEN}✓{Colors.END} System load looks good!")
    print()

    # High Memory Processes
    high_mem_procs = get_high_memory_processes(3)
    if high_mem_procs:
        print(f"{Colors.BOLD}{Colors.BLUE}[Top Memory Consumers]{Colors.END}")
        for proc in high_mem_procs:
            mem_color = Colors.RED if float(proc['mem']) > 5.0 else Colors.YELLOW
            print(f"  {mem_color}{proc['mem']:>5}%{Colors.END} | PID {proc['pid']:>6} | {proc['command']}")
        print()

    # Recent Activity
    recent = get_recent_commands(5)
    if recent:
        print(f"{Colors.BOLD}{Colors.BLUE}[Recent Activity]{Colors.END}")
        for i, cmd in enumerate(recent, 1):
            print(f"  {Colors.PURPLE}{i}.{Colors.END} {cmd}")
        print()

    # Favorites
    favorites = get_favorite_commands(5)
    if favorites:
        print(f"{Colors.BOLD}{Colors.BLUE}[Most Used Commands]{Colors.END}")
        for cmd, count in favorites:
            print(f"  {Colors.GREEN}{'█' * min(count, 20)}{Colors.END} {cmd} {Colors.CYAN}({count}x){Colors.END}")
        print()

    # Footer
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}Type a command to get started, or 'python3 run.py --help' for help{Colors.END}\n")

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

    # Special handling for 'hi' command
    if command_name == 'hi':
        return handle_hi()

    # Save command to history
    save_command_history(f"{command_name} {' '.join(args)}")

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

    # Handle directory search for 'go' command
    if 'search_dir' in parameters:
        dir_name = parameters['search_dir']
        debug_print(f"Searching for directory: {dir_name}")

        # Show searching feedback
        show_command_feedback('go', f"Searching for '{dir_name}'", Colors.GREEN)

        found_path = search_directory(dir_name)

        if found_path:
            debug_print(f"Directory found at: {found_path}")
            # Show going feedback with colored path
            print(f"{Colors.GREEN}→ Going to {Colors.BLUE}{found_path}{Colors.END}")
            print(f"cd {found_path}")
            return 0
        else:
            CommandOutput.print_error(f"Directory '{dir_name}' not found")
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

        # Extract the path from cd command
        path = formatted_action[3:].strip()
        # Show colorful feedback for predefined shortcuts
        print(f"{Colors.GREEN}→ Going to {Colors.BLUE}{path}{Colors.END}")
        print(formatted_action)
        return 0

    # Show command execution feedback
    if cmd_name in ['push', 'cpu', 'mem', 'proc', 'update', 'restore']:
        action_descriptions = {
            'push': 'Pushing to Git',
            'cpu': 'Checking CPU usage',
            'mem': 'Checking memory usage',
            'proc': 'Listing processes',
            'update': 'Updating CCMD',
            'restore': 'Restoring configuration',
        }
        if cmd_name in action_descriptions:
            show_command_feedback(cmd_name, action_descriptions[cmd_name])

    # Execute command
    debug_print("Executing command...")
    returncode, stdout, stderr = executor.execute(formatted_action)
    debug_print(f"Return code: {returncode}")

    CommandOutput.print_command_output(stdout, stderr)

    return returncode


if __name__ == "__main__":
    sys.exit(main())
