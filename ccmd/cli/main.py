"""Main CLI entry point for CCMD"""

import argparse
import sys
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for Unicode support (v1.1.1 Enhanced)
if sys.platform == 'win32':
    try:
        # Set console to UTF-8 mode (Windows 10+)
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # UTF-8

        # Reconfigure stdout/stderr to use UTF-8
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception as e:
        # Fallback: If UTF-8 fails, at least don't crash
        pass

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
    if sys.platform == 'win32':
        # More targeted search paths for Windows
        username = os.getenv('USERNAME')
        search_paths = []
        if username:
            search_paths.extend([
                f"C:\\Users\\{username}",
                f"C:\\Users\\{username}\\Downloads",
                f"C:\\Users\\{username}\\Documents",
                f"C:\\Users\\{username}\\Desktop",
                f"C:\\Users\\{username}\\targlobal",
            ])
        search_paths.append(os.path.expanduser("~"))
    else:
        search_paths = [
            os.path.expanduser("~"),
            "/mnt/c/Users/rober",
            "/mnt/c/Users/rober/Downloads",
            "/mnt/c/Users/rober/targlobal",
        ]

    debug_print(f"Searching for directory: {dir_name}")

    # Use Python's os.walk for cross-platform compatibility
    for base_path in search_paths:
        if not os.path.exists(base_path):
            continue

        try:
            # Search up to 3 levels deep
            for root, dirs, files in os.walk(base_path):
                # Calculate depth
                depth = root[len(base_path):].count(os.sep)

                # If we're at max depth, don't descend further
                if depth >= 3:
                    dirs[:] = []  # Don't descend into subdirectories
                    continue

                # Check directories (case-insensitive)
                for d in dirs:
                    if d.lower() == dir_name.lower():
                        found_path = os.path.join(root, d)
                        debug_print(f"Found directory: {found_path}")
                        return found_path

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
    parser.add_argument('--check-paths', action='store_true',
                       help='Validate CCMD installation paths and environment (v1.1.5)')
    parser.add_argument('--edit', action='store_true',
                       help='Open interactive command editor')
    parser.add_argument('--test', action='store_true',
                       help='Test CCMD installation')
    parser.add_argument('--reload', action='store_true',
                       help='Reload commands from configuration')
    parser.add_argument('--list', action='store_true',
                       help='List all available commands')
    parser.add_argument('--version', action='store_true',
                       help='Show current and latest CCMD version')
    parser.add_argument('--update', action='store_true',
                       help='Update CCMD to latest version from GitHub')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode with verbose output')
    parser.add_argument('--init', action='store_true',
                       help='Initialize CCMD master password (v1.1.1)')
    parser.add_argument('--change-password', action='store_true',
                       help='Change the master password (requires current password)')
    parser.add_argument('--reset-password', action='store_true',
                       help='Reset (delete) master password - use if you forgot it')
    parser.add_argument('--exec', type=str,
                       help=argparse.SUPPRESS)  # Hidden: internal use only

    # Command execution
    parser.add_argument('command', nargs='?', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')

    args = parser.parse_args()

    # Set global debug mode
    global DEBUG_MODE
    DEBUG_MODE = args.debug

    # Handle debug mode if no other command
    if args.debug and not any([args.install, args.uninstall, args.restore,
                                args.check, args.check_paths, args.edit, args.test, args.reload,
                                args.list, args.version, args.update, args.init,
                                args.change_password, args.reset_password, args.exec, args.command]):
        return handle_debug()

    # Handle management flags
    if args.install:
        return handle_install()
    elif args.uninstall:
        return handle_uninstall()
    elif args.version:
        return handle_version()
    elif args.update:
        return handle_update()
    elif args.restore:
        return handle_restore()
    elif args.check:
        return handle_check()
    elif args.check_paths:
        return handle_check_paths()
    elif args.edit:
        return handle_edit()
    elif args.test:
        return handle_test()
    elif args.reload:
        return handle_reload()
    elif args.list:
        return handle_list()
    elif args.init:
        return handle_init()
    elif args.change_password:
        return handle_change_password()
    elif args.reset_password:
        return handle_reset_password()
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


def handle_update():
    """Handle update from GitHub"""
    import json
    import urllib.request
    import tarfile
    import shutil
    import tempfile
    from ccmd.cli.install import install_ccmd

    CommandOutput.print_info("Checking for latest CCMD version on GitHub...")

    try:
        # Get latest release info from GitHub API
        api_url = "https://api.github.com/repos/Wisyle/ccmd/releases/latest"
        # SECURITY: Validate URL scheme to prevent file:// or other schemes
        if not api_url.startswith('https://'):
            CommandOutput.print_error("Invalid URL scheme - only HTTPS allowed")
            return 1
        with urllib.request.urlopen(api_url) as response:
            release_data = json.loads(response.read().decode())

        latest_version = release_data['tag_name']
        tarball_url = release_data['tarball_url']

        # Check current version
        try:
            from ccmd import __version__
            current_version = f"v{__version__}"
        except:
            current_version = "unknown"

        CommandOutput.print_info(f"Current version: {current_version}")
        CommandOutput.print_info(f"Latest version: {latest_version}")

        if current_version == latest_version:
            CommandOutput.print_success("You are already on the latest version!")
            return 0

        CommandOutput.print_info(f"Downloading CCMD {latest_version}...")

        # Download tarball to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as tmp_file:
            # SECURITY: Validate URL scheme
            if not tarball_url.startswith('https://'):
                CommandOutput.print_error("Invalid tarball URL - only HTTPS allowed")
                return 1
            with urllib.request.urlopen(tarball_url) as response:
                tmp_file.write(response.read())
            tarball_path = tmp_file.name

        # Extract to temp directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            CommandOutput.print_info("Extracting files...")
            with tarfile.open(tarball_path, 'r:gz') as tar:
                # SECURITY: Validate tar members before extraction (CVE-2007-4559)
                def is_safe_path(path, base_dir):
                    """Check if a path is safe to extract"""
                    # Resolve the absolute path
                    resolved = os.path.normpath(os.path.join(base_dir, path))
                    # Ensure it's within the base directory
                    return resolved.startswith(os.path.normpath(base_dir))
                
                # Check all members before extraction
                for member in tar.getmembers():
                    if not is_safe_path(member.name, tmp_dir):
                        CommandOutput.print_error(f"Unsafe path in tarball: {member.name}")
                        return 1
                    # Also check for absolute paths and parent directory references
                    if member.name.startswith('/') or '..' in member.name:
                        CommandOutput.print_error(f"Suspicious path in tarball: {member.name}")
                        return 1
                
                # Safe to extract - we validated all members above
                tar.extractall(tmp_dir)  # nosec B202

            # Find extracted directory (GitHub tarballs have a single root directory)
            extracted_dirs = [d for d in Path(tmp_dir).iterdir() if d.is_dir()]
            if not extracted_dirs:
                CommandOutput.print_error("Failed to extract release")
                return 1

            source_dir = extracted_dirs[0]

            # Get CCMD_HOME
            ccmd_home = os.environ.get('CCMD_HOME')
            if not ccmd_home:
                CommandOutput.print_error("CCMD_HOME not set")
                return 1

            dest_dir = Path(ccmd_home)

            CommandOutput.print_info(f"Installing to {dest_dir}...")

            # Copy files (excluding .git, .github, etc.)
            for item in source_dir.iterdir():
                if item.name.startswith('.'):
                    continue

                dest_item = dest_dir / item.name
                if item.is_dir():
                    if dest_item.exists():
                        shutil.rmtree(dest_item)
                    shutil.copytree(item, dest_item)
                else:
                    shutil.copy2(item, dest_item)

        # Clean up tarball
        os.unlink(tarball_path)

        # Reinstall shell integration
        CommandOutput.print_info("Updating shell integration...")
        success, message = install_ccmd()

        if success:
            CommandOutput.print_success(f"Successfully updated to CCMD {latest_version}!")
            CommandOutput.print_info("Please restart your shell or run: source ~/.bashrc (or ~/.zshrc)")
            return 0
        else:
            CommandOutput.print_error(f"Update succeeded but shell integration failed: {message}")
            return 1

    except urllib.error.URLError as e:
        CommandOutput.print_error(f"Failed to connect to GitHub: {e}")
        return 1
    except Exception as e:
        CommandOutput.print_error(f"Update failed: {e}")
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


def handle_check_paths():
    """
    Validate CCMD installation paths and environment (v1.1.5 Security Enhancement)

    Helps diagnose installation issues, path problems, and environment misconfigurations.
    """
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}CCMD Path Diagnostics (v1.1.5){Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

    issues_found = 0
    warnings_found = 0

    # 1. Check CCMD_HOME environment variable
    print(f"{Colors.CYAN}[1/7] Checking CCMD_HOME environment variable...{Colors.END}")
    ccmd_home = os.environ.get('CCMD_HOME')
    if ccmd_home:
        print(f"  {Colors.GREEN}✓{Colors.END} CCMD_HOME is set: {ccmd_home}")
    else:
        print(f"  {Colors.RED}✗{Colors.END} CCMD_HOME is not set")
        print(f"    {Colors.YELLOW}→{Colors.END} CCMD may not be installed. Run: python3 run.py --install")
        issues_found += 1

    # 2. Check if CCMD_HOME points to valid directory
    print(f"\n{Colors.CYAN}[2/7] Validating CCMD_HOME directory...{Colors.END}")
    if ccmd_home:
        ccmd_path = Path(ccmd_home)
        if ccmd_path.exists() and ccmd_path.is_dir():
            print(f"  {Colors.GREEN}✓{Colors.END} Directory exists: {ccmd_path}")
        else:
            print(f"  {Colors.RED}✗{Colors.END} Directory does not exist: {ccmd_path}")
            print(f"    {Colors.YELLOW}→{Colors.END} CCMD was moved or deleted")
            print(f"    {Colors.YELLOW}→{Colors.END} Fix: python3 /new/path/to/ccmd/run.py --uninstall")
            print(f"    {Colors.YELLOW}→{Colors.END} Then: python3 /new/path/to/ccmd/run.py --install")
            issues_found += 1
    else:
        print(f"  {Colors.YELLOW}⚠{Colors.END} Skipped (CCMD_HOME not set)")
        warnings_found += 1

    # 3. Check run.py exists
    print(f"\n{Colors.CYAN}[3/7] Checking for run.py entry point...{Colors.END}")
    if ccmd_home:
        run_py = Path(ccmd_home) / "run.py"
        if run_py.exists():
            print(f"  {Colors.GREEN}✓{Colors.END} Found: {run_py}")
        else:
            print(f"  {Colors.RED}✗{Colors.END} Missing: {run_py}")
            print(f"    {Colors.YELLOW}→{Colors.END} CCMD installation is incomplete or corrupted")
            issues_found += 1
    else:
        print(f"  {Colors.YELLOW}⚠{Colors.END} Skipped (CCMD_HOME not set)")
        warnings_found += 1

    # 4. Check commands.yaml exists
    print(f"\n{Colors.CYAN}[4/7] Checking for commands.yaml configuration...{Colors.END}")
    if ccmd_home:
        commands_yaml = Path(ccmd_home) / "commands.yaml"
        if commands_yaml.exists():
            print(f"  {Colors.GREEN}✓{Colors.END} Found: {commands_yaml}")
            # Try to load and count commands
            try:
                registry = CommandRegistry(commands_yaml)
                commands = registry.list_commands()
                print(f"  {Colors.GREEN}✓{Colors.END} Loaded {len(commands)} commands successfully")
            except Exception as e:
                print(f"  {Colors.RED}✗{Colors.END} Failed to load commands: {e}")
                print(f"    {Colors.YELLOW}→{Colors.END} commands.yaml may be corrupted")
                issues_found += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Missing: {commands_yaml}")
            print(f"    {Colors.YELLOW}→{Colors.END} Run: python3 {run_py} --install (to regenerate)")
            issues_found += 1
    else:
        print(f"  {Colors.YELLOW}⚠{Colors.END} Skipped (CCMD_HOME not set)")
        warnings_found += 1

    # 5. Check Python executable
    print(f"\n{Colors.CYAN}[5/7] Checking Python executable...{Colors.END}")
    python_exec = sys.executable
    print(f"  {Colors.GREEN}✓{Colors.END} Python: {python_exec}")
    print(f"  {Colors.GREEN}✓{Colors.END} Version: {sys.version.split()[0]}")

    # 6. Check shell integration
    print(f"\n{Colors.CYAN}[6/7] Checking shell integration...{Colors.END}")
    system_info = get_system_info()
    rc_file = system_info.shell_rc_file

    if rc_file and Path(rc_file).exists():
        print(f"  {Colors.GREEN}✓{Colors.END} Shell config: {rc_file}")

        # Check if CCMD integration exists
        with open(rc_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if "# CCMD Integration" in content:
            print(f"  {Colors.GREEN}✓{Colors.END} CCMD integration found in shell config")
        else:
            print(f"  {Colors.YELLOW}⚠{Colors.END} CCMD integration NOT found in shell config")
            print(f"    {Colors.YELLOW}→{Colors.END} CCMD may not be installed")
            print(f"    {Colors.YELLOW}→{Colors.END} Run: python3 /path/to/ccmd/run.py --install")
            warnings_found += 1
    else:
        print(f"  {Colors.RED}✗{Colors.END} Shell config not found: {rc_file}")
        issues_found += 1

    # 7. Check backups
    print(f"\n{Colors.CYAN}[7/7] Checking backup system...{Colors.END}")
    backup_dir = Path.home() / ".ccmd" / "backups"
    if backup_dir.exists():
        backups = list(backup_dir.glob("*.bak"))
        print(f"  {Colors.GREEN}✓{Colors.END} Backup directory exists: {backup_dir}")
        print(f"  {Colors.GREEN}✓{Colors.END} Found {len(backups)} backup(s)")
    else:
        print(f"  {Colors.YELLOW}⚠{Colors.END} No backup directory found (will be created on first use)")
        warnings_found += 1

    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}Diagnostic Summary{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

    if issues_found == 0 and warnings_found == 0:
        print(f"{Colors.GREEN}✓ All checks passed! CCMD is properly configured.{Colors.END}\n")
        return 0
    elif issues_found == 0:
        print(f"{Colors.YELLOW}⚠ {warnings_found} warning(s) found, but no critical issues.{Colors.END}")
        print(f"{Colors.YELLOW}  CCMD should work, but may have minor issues.{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}✗ {issues_found} issue(s) found that may prevent CCMD from working.{Colors.END}")
        if warnings_found > 0:
            print(f"{Colors.YELLOW}⚠ {warnings_found} warning(s) also found.{Colors.END}")
        print(f"\n{Colors.CYAN}→ See messages above for suggested fixes.{Colors.END}")
        print(f"{Colors.CYAN}→ For more help, see: {Colors.END}RECOVERY.md\n")
        return 1


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
    """Handle command reload and shell integration update"""
    from ccmd.cli.install import install_ccmd

    CommandOutput.print_info("Reloading CCMD configuration...")

    # Reload commands from config
    registry = CommandRegistry()
    registry.reload()
    commands = registry.list_commands()

    CommandOutput.print_success(f"✓ Reloaded {len(commands)} commands")

    # Reinstall shell integration to apply changes
    CommandOutput.print_info("Updating shell integration...")
    success, message = install_ccmd()

    if success:
        CommandOutput.print_success("✓ Shell integration updated!")
        print()
        # Show appropriate reload command based on platform
        if sys.platform == 'win32':
            print(f"{Colors.BOLD}→ Run: . $PROFILE{Colors.END}")
        else:
            print(f"{Colors.BOLD}→ Run: source ~/.bashrc{Colors.END}")
            print(f"{Colors.CYAN}   (or ~/.zshrc for zsh, ~/.config/fish/config.fish for fish){Colors.END}")
        print()
        return 0
    else:
        CommandOutput.print_error(f"Shell integration failed: {message}")
        return 1


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

    print()
    print("Options:")
    print("  1. Done (exit)")
    print("  2. Edit commands (enable/disable)")
    print()
    sys.stdout.flush()

    choice = input("Enter choice (1-2) or press Enter to exit: ").strip()

    if choice == '2':
        from ccmd.cli.interactive import interactive_list_editor
        return interactive_list_editor()

    return 0


def handle_version():
    """Show version information"""
    import json
    import urllib.request
    from ccmd import __version__

    print()
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  CCMD Version Information{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}")
    print()

    # Current version
    print(f"{Colors.BOLD}{Colors.BLUE}[Current Version]{Colors.END}")
    print(f"  {Colors.GREEN}v{__version__}{Colors.END}")
    print()

    # Check latest version from GitHub
    print(f"{Colors.BOLD}{Colors.BLUE}[Latest Version]{Colors.END}")
    try:
        api_url = "https://api.github.com/repos/Wisyle/ccmd/releases/latest"
        # SECURITY: Validate URL scheme
        if not api_url.startswith('https://'):
            raise ValueError("Invalid URL scheme - only HTTPS allowed")
        with urllib.request.urlopen(api_url, timeout=5) as response:
            release_data = json.loads(response.read().decode())

        latest_version = release_data['tag_name']
        release_name = release_data.get('name', latest_version)
        release_body = release_data.get('body', 'No release notes available')
        published_at = release_data.get('published_at', '')

        # Parse date
        if published_at:
            from datetime import datetime
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            date_str = pub_date.strftime('%B %d, %Y')
        else:
            date_str = 'Unknown'

        # Show latest version
        if f"v{__version__}" == latest_version:
            print(f"  {Colors.GREEN}{latest_version}{Colors.END} {Colors.CYAN}(You are up to date!){Colors.END}")
        else:
            print(f"  {Colors.YELLOW}{latest_version}{Colors.END} {Colors.RED}(Update available!){Colors.END}")

        print(f"  {Colors.CYAN}Released: {date_str}{Colors.END}")
        print()

        # Show release notes
        print(f"{Colors.BOLD}{Colors.BLUE}[Release Notes]{Colors.END}")
        # Parse and colorize release notes (v1.1.1 fix: handle Unicode properly)
        for line in release_body.split('\n'):
            line = line.strip()
            if line.startswith('##'):
                print(f"  {Colors.BOLD}{Colors.PURPLE}{line}{Colors.END}")
            elif line.startswith('- ') or line.startswith('* '):
                # Don't add another checkmark if line already has Unicode
                bullet_text = line[2:].strip()
                if bullet_text.startswith('✓') or bullet_text.startswith('✅') or bullet_text.startswith('❌'):
                    # Already has Unicode symbol, just print it
                    print(f"  {bullet_text}")
                else:
                    # Add checkmark for plain bullets
                    print(f"  {Colors.GREEN}✓{Colors.END} {bullet_text}")
            elif line.startswith('###'):
                print(f"  {Colors.BOLD}{Colors.CYAN}{line}{Colors.END}")
            elif line:
                # Print line as-is, preserving any Unicode characters
                print(f"  {line}")

        print()

        # Show update command if outdated
        if f"v{__version__}" != latest_version:
            print(f"{Colors.YELLOW}→ Run 'update' to install the latest version{Colors.END}")
            print()

    except Exception as e:
        print(f"  {Colors.YELLOW}Could not fetch latest version{Colors.END}")
        print(f"  {Colors.CYAN}(Check your internet connection){Colors.END}")
        print()

    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}")
    print()

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


def handle_init():
    """Initialize CCMD master password (v1.1.1)"""
    from ccmd.core.auth import initialize_password_interactive, HAS_BCRYPT

    if not HAS_BCRYPT:
        print(f"{Colors.RED}✗ bcrypt not installed{Colors.END}")
        print(f"{Colors.YELLOW}→ Install with: pip install bcrypt{Colors.END}")
        return 1

    print()
    print(f"{Colors.BOLD}{Colors.CYAN}=== Initialize CCMD Master Password ==={Colors.END}")
    print()

    success, message = initialize_password_interactive()

    if success:
        print()
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
        print()
        print(f"{Colors.CYAN}Your master password is now active!{Colors.END}")
        print(f"{Colors.CYAN}It will protect sensitive commands like SSH and sudo.{Colors.END}")
        print()
        return 0
    else:
        print()
        print(f"{Colors.RED}✗ {message}{Colors.END}")
        print()
        return 1


def handle_change_password():
    """Change the master password"""
    from ccmd.core.auth import change_password_interactive, HAS_BCRYPT

    if not HAS_BCRYPT:
        print(f"{Colors.RED}✗ bcrypt not installed{Colors.END}")
        print(f"{Colors.YELLOW}→ Install with: pip install bcrypt{Colors.END}")
        return 1

    success, message = change_password_interactive()

    if success:
        print()
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
        print()
        return 0
    else:
        print()
        print(f"{Colors.RED}✗ {message}{Colors.END}")
        print()
        return 1


def handle_reset_password():
    """Reset (delete) master password"""
    from ccmd.core.auth import reset_password_interactive, HAS_BCRYPT

    if not HAS_BCRYPT:
        print(f"{Colors.RED}✗ bcrypt not installed{Colors.END}")
        print(f"{Colors.YELLOW}→ Install with: pip install bcrypt{Colors.END}")
        return 1

    success, message = reset_password_interactive()

    if success:
        print()
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
        print()
        print(f"{Colors.YELLOW}→ Run 'python3 run.py --init' to set a new password{Colors.END}")
        print()
        return 0
    else:
        print()
        print(f"{Colors.RED}✗ {message}{Colors.END}")
        print()
        return 1


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
    """Execute a raw command (INTERNAL USE ONLY)"""
    # SECURITY: Only allow internal calls via environment variable
    # This prevents external users from bypassing command validation
    if os.environ.get('CCMD_INTERNAL') != '1':
        print("Error: --exec is for internal use only", file=sys.stderr)
        print("Use regular CCMD commands instead (e.g., 'ccmd <command>')", file=sys.stderr)
        return 1

    system_info = get_system_info()
    executor = CommandExecutor(system_info)

    returncode, stdout, stderr = executor.execute(command)
    CommandOutput.print_command_output(stdout, stderr)

    return returncode


def handle_command(command_name: str, args: list):
    """Handle command execution"""
    debug_print(f"Executing command: {command_name} with args: {args}")

    # Special handling for internal commands (v1.1.1 fix)
    # These commands have direct handler functions and should not execute shell actions
    internal_commands = {
        'hi': handle_hi,
        'list': handle_list,
        'init': handle_init,
        'debug': handle_debug,
        'version': handle_version,
        'reload': handle_reload,
        'change-password': handle_change_password,
        'reset-password': handle_reset_password,
        'update': handle_update,
        'restore': handle_restore,
        'uninstall': handle_uninstall,
    }

    if command_name in internal_commands:
        return internal_commands[command_name]()

    # Special handling for interactive commands
    if command_name == 'push':
        from ccmd.cli.interactive import interactive_push
        return interactive_push()

    if command_name == 'add':
        from ccmd.cli.interactive import interactive_add_command
        return interactive_add_command()

    if command_name == 'remove':
        from ccmd.cli.interactive import interactive_remove_command
        return interactive_remove_command()

    # Special handling for 'kap' - dangerous command needs confirmation
    if command_name == 'kap':
        print()
        print(f"{Colors.RED}{Colors.BOLD}⚠️  WARNING: DANGEROUS OPERATION{Colors.END}")
        print(f"{Colors.YELLOW}This will kill ALL processes owned by you!{Colors.END}")
        print(f"{Colors.YELLOW}This may cause data loss and unsaved work.{Colors.END}")
        print()

        try:
            confirm = input(f"{Colors.CYAN}Type 'yes' to confirm: {Colors.END}").strip().lower()
            if confirm != 'yes':
                print(f"{Colors.GREEN}→ Operation cancelled{Colors.END}")
                return 0
        except KeyboardInterrupt:
            print(f"\n{Colors.GREEN}→ Operation cancelled{Colors.END}")
            return 0

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

        # Show searching feedback to stderr
        print(f"{Colors.GREEN}→ Searching for '{dir_name}'...{Colors.END}", file=sys.stderr)

        found_path = search_directory(dir_name)

        if found_path:
            debug_print(f"Directory found at: {found_path}")
            # Show going feedback with colored path to stderr
            print(f"{Colors.GREEN}→ Going to {Colors.BLUE}{found_path}{Colors.END}", file=sys.stderr)
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
        # Show colorful feedback for predefined shortcuts to stderr
        print(f"{Colors.GREEN}→ Going to {Colors.BLUE}{path}{Colors.END}", file=sys.stderr)
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

    # Execute command with security (v1.1.1 - password protection for sensitive commands)
    debug_print("Executing command with security checks...")

    # Get command definition for security checks
    cmd_def = registry.get_command(cmd_name)

    # Check if command is interactive (needs terminal I/O)
    is_interactive = cmd_def.get('interactive', False) if cmd_def else False

    # Use secure execution with password protection
    returncode, stdout, stderr = executor.execute_with_security(
        formatted_action,
        command_def=cmd_def,
        interactive=is_interactive
    )
    debug_print(f"Return code: {returncode}")

    CommandOutput.print_command_output(stdout, stderr)

    return returncode


if __name__ == "__main__":
    sys.exit(main())
