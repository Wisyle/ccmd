"""Safe command executor module - Security Enhanced v1.1.1"""

import subprocess
import shlex
import sys
import os
from typing import Tuple, Optional, List, Dict, Any
from pathlib import Path

# Import security utilities
from ccmd.core.security import (
    CommandSecurityValidator,
    SecureSubprocess,
    VersionSecurity
)

# Import authentication utilities
from ccmd.core.auth import (
    verify_password_interactive,
    detect_sensitive_command,
    check_key_file_permissions,
    extract_ssh_key_path
)


class CommandExecutor:
    """Safely execute shell commands with enhanced security"""

    def __init__(self, system_info=None):
        """
        Initialize executor

        Args:
            system_info: SystemInfo instance
        """
        self.system_info = system_info
        self.validator = CommandSecurityValidator()
        self.subprocess_runner = SecureSubprocess()

    def validate_command(self, command: str, allow_chaining: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validate a command for safety using security module (v1.1.2 - context-aware)

        Args:
            command: Command string to validate
            allow_chaining: If True, allow shell operators (&&, ||, ;) - for custom commands

        Returns:
            Tuple of (is_valid, error_message)
        """
        return self.validator.validate_command(command, allow_chaining=allow_chaining)

    def execute_with_security(self, command: str, command_def: Optional[Dict[str, Any]] = None,
                             interactive: bool = False) -> Tuple[int, str, str]:
        """
        Execute a command with full security checks (NEW in v1.1.1)

        Args:
            command: Command to execute
            command_def: Command definition dict (may contain require_password flag)
            interactive: Whether command needs interactive terminal

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        # Step 1: Validate command syntax (v1.1.2 - context-aware)
        # Custom commands can use chaining operators since they run with shell=False
        allow_chaining = command_def and command_def.get('type') == 'custom'
        is_valid, error = self.validate_command(command, allow_chaining=allow_chaining)
        if not is_valid:
            return 1, "", f"Command validation failed: {error}"

        # Step 2: Check if password is required
        require_password = False

        # Check explicit flag in command definition
        if command_def and command_def.get('require_password', False):
            require_password = True

        # Auto-detect sensitive commands
        is_sensitive, reason = detect_sensitive_command(command)
        if is_sensitive:
            require_password = True
            if not command_def or not command_def.get('require_password'):
                # Warn user about auto-detected sensitive command
                print(f"⚠ Sensitive command detected: {reason}", file=sys.stderr)

        # Step 3: If SSH key is referenced, validate permissions
        key_path = extract_ssh_key_path(command)
        if key_path:
            is_valid_key, key_error = check_key_file_permissions(key_path)
            if not is_valid_key:
                return 1, "", f"SSH key validation failed: {key_error}"

        # Step 4: Require password authentication if needed
        if require_password:
            try:
                if not verify_password_interactive():
                    return 1, "", "Authentication failed - command aborted"
            except KeyboardInterrupt:
                return 1, "", "\n→ Operation cancelled"

        # Step 5: Determine if shell=True is safe for this command
        # System commands (cpu, mem, proc) are predefined and safe
        allow_shell = False
        if command_def and command_def.get('type') in ['system', 'internal']:
            # Predefined system commands can use shell for pipes/redirects
            allow_shell = True

        # Step 6: Execute command (check for chaining first - v1.1.2)
        if '>>>' in command:
            return self.execute_chained_commands(command, command_def, interactive)

        try:
            return self.execute(command, interactive=interactive, shell=allow_shell)
        except KeyboardInterrupt:
            return 1, "", "\n→ Operation cancelled"

    def execute_chained_commands(self, command_string: str, command_def: Optional[Dict[str, Any]] = None,
                                 interactive: bool = False, _depth: int = 0) -> Tuple[int, str, str]:
        """
        Execute commands chained with >>> operator (v1.1.2 - Command Composability)

        Features:
        - Each part can be a CCMD command OR shell command
        - CCMD commands executed through internal method
        - Shell commands executed with execute_with_security()
        - Special handling for 'go' to actually change directory
        - Recursion guard to prevent infinite loops

        Args:
            command_string: Command string with >>> separators
            command_def: Command definition dict
            interactive: Whether commands need interactive terminal
            _depth: Recursion depth (internal, prevents infinite loops)

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        # Recursion guard - max depth 10
        if _depth > 10:
            return 1, "", "Error: Maximum command chain depth exceeded (possible infinite loop)"

        # Split on >>> separator
        parts = [p.strip() for p in command_string.split('>>>')]

        # Validate each part individually
        for part in parts:
            # Parse to check if it's a CCMD command
            cmd_parts = part.split()
            if not cmd_parts:
                continue

            cmd_name = cmd_parts[0]

            # Get registry to check if this is a CCMD command
            from ccmd.core.registry import CommandRegistry
            registry = CommandRegistry()

            # If it's NOT a CCMD command, validate it as shell command
            if not registry.has_command(cmd_name):
                # Custom commands can use chaining operators
                allow_chaining = command_def and command_def.get('type') == 'custom'
                is_valid, error = self.validate_command(part, allow_chaining=allow_chaining)
                if not is_valid:
                    return 1, "", f"Invalid command in chain: {error}"

        # Execute in sequence
        all_stdout = []
        all_stderr = []

        for i, part in enumerate(parts):
            print(f"→ Step {i+1}/{len(parts)}: {part}", file=sys.stderr)

            # Parse command name and arguments
            cmd_parts = part.split()
            cmd_name = cmd_parts[0]
            cmd_args = cmd_parts[1:] if len(cmd_parts) > 1 else []

            # Get registry
            from ccmd.core.registry import CommandRegistry
            registry = CommandRegistry()

            # Check if this is a CCMD command
            if registry.has_command(cmd_name):
                # Execute CCMD command (allows command composability!)
                print(f"  (executing CCMD command: {cmd_name})", file=sys.stderr)

                returncode, stdout, stderr = self._execute_ccmd_command(
                    cmd_name, cmd_args, registry, _depth + 1
                )

                # Special handling for 'go' command - actually change directory
                if cmd_name == 'go' and returncode == 0:
                    if stdout.startswith('cd '):
                        target_dir = stdout.replace('cd ', '').strip()
                        # Expand ~ to home directory and environment variables
                        target_dir = os.path.expanduser(target_dir)
                        target_dir = os.path.expandvars(target_dir)
                        try:
                            os.chdir(target_dir)
                            print(f"  (changed directory to: {target_dir})", file=sys.stderr)
                        except Exception as e:
                            return 1, '', f"Failed to change directory: {e}"
            else:
                # Regular shell command - run without capturing output for better UX
                # This allows interactive commands to show their output in real-time
                try:
                    cmd_parts = self.subprocess_runner.parse_shell_command(part)

                    # For interactive commands, don't apply timeout (they might run indefinitely)
                    is_interactive = command_def and command_def.get('interactive', False)
                    timeout_value = None if is_interactive else 180

                    result = subprocess.run(
                        cmd_parts,
                        shell=False,  # SECURITY: Never use shell=True for user commands
                        stdin=None,   # Inherit from parent
                        stdout=None,  # Inherit - shows output in real-time
                        stderr=None,  # Inherit - shows errors in real-time
                        timeout=timeout_value
                    )
                    returncode = result.returncode
                    stdout, stderr = "", ""
                except subprocess.TimeoutExpired:
                    print("Command timed out after 180 seconds", file=sys.stderr)
                    return 1, '\n'.join(all_stdout), "Command timed out"
                except Exception as e:
                    print(f"Execution error: {e}", file=sys.stderr)
                    return 1, '\n'.join(all_stdout), str(e)

            all_stdout.append(stdout)
            all_stderr.append(stderr)

            if returncode != 0:
                print(f"✗ Step {i+1} failed with code {returncode}", file=sys.stderr)
                return returncode, '\n'.join(all_stdout), '\n'.join(all_stderr)

            print(f"✓ Step {i+1} completed", file=sys.stderr)

        return 0, '\n'.join(all_stdout), '\n'.join(all_stderr)

    def _execute_ccmd_command(self, cmd_name: str, cmd_args: list, registry,
                             depth: int) -> Tuple[int, str, str]:
        """
        Execute a CCMD command programmatically (v1.1.2 - Internal use)

        Args:
            cmd_name: Command name
            cmd_args: Command arguments
            registry: CommandRegistry instance
            depth: Recursion depth

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        from ccmd.core.parser import CommandParser

        # Get command definition
        cmd_def = registry.get_command(cmd_name)
        if not cmd_def:
            return 1, "", f"Command not found: {cmd_name}"

        # Parse the command
        parser = CommandParser(registry)
        _, subcommand, parameters = parser.parse([cmd_name] + cmd_args)

        if 'error' in parameters:
            return 1, "", parameters['error']

        # Handle directory search for 'go' command (v1.1.7 fix)
        # When 'go <dirname>' is called and dirname isn't a known subcommand,
        # we need to search for it just like main.py does
        if 'search_dir' in parameters:
            dir_name = parameters['search_dir']
            print(f"  (searching for directory: {dir_name})", file=sys.stderr)
            found_path = self._search_directory(dir_name)
            if found_path:
                return 0, f"cd {found_path}", ""
            else:
                return 1, "", f"Directory '{dir_name}' not found"

        # Get the action (using subcommand and os_type)
        os_type = self.system_info.os_type if self.system_info else None
        action = parser.get_action(cmd_name, subcommand, os_type)

        if not action:
            return 1, "", f"No action defined for command: {cmd_name}"

        # Format the action with parameters
        formatted_action = parser.format_action(action, parameters)

        # Check if this command also has chaining (recursive)
        if '>>>' in formatted_action:
            return self.execute_chained_commands(formatted_action, cmd_def, False, depth)
        else:
            # Special handling for navigation commands (cd)
            if formatted_action.startswith('cd '):
                # Return the cd command in stdout for our special handler to process
                return 0, formatted_action, ""

            # Execute with security checks (password protection, sensitive detection)
            is_interactive = cmd_def.get('interactive', False)
            return self.execute_with_security(formatted_action, command_def=cmd_def, interactive=is_interactive)

    def execute(self, command: str, interactive: bool = False,
                shell: bool = False) -> Tuple[int, str, str]:
        """
        Execute a command safely (SECURITY ENHANCED v1.1.1)

        Note: Use execute_with_security() for full security checks

        Args:
            command: Command to execute
            interactive: Whether command needs interactive terminal
            shell: Allow shell=True ONLY for predefined system commands

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        # Validate command first
        is_valid, error = self.validate_command(command)
        if not is_valid:
            return 1, "", f"Command validation failed: {error}"

        # Expand environment variables (SECURITY: Only expand known safe variables)
        command = self._expand_safe_env_vars(command)

        try:
            if interactive:
                # For interactive commands like cd, we need special handling
                return self._execute_interactive(command)
            else:
                # Standard execution
                if shell:
                    # SECURITY NOTICE: shell=True is required here for specific reasons:
                    # 1. System commands from commands.yaml need shell features like:
                    #    - Variable expansion ($HOME, $USER, etc.)
                    #    - Glob patterns (*.txt, ~/Documents/*)
                    #    - Pipes and redirections (ps aux | grep python)
                    #    - Shell built-ins (cd, export, source)
                    # 2. This is ONLY allowed for predefined system/internal commands
                    # 3. User-defined custom commands NEVER get shell=True
                    # 4. All commands go through security validation before reaching here
                    # 5. This is a conscious security trade-off for functionality
                    result = subprocess.run(
                        command,
                        shell=True,  # nosec B602
                        capture_output=True,
                        text=True,
                        timeout=180  # Increased from 30 to 180 seconds for slow commands
                    )
                    return result.returncode, result.stdout, result.stderr
                else:
                    # Secure execution without shell=True (for user commands)
                    cmd_parts = self.subprocess_runner.parse_shell_command(command)
                    return self.subprocess_runner.run_command_safe(
                        cmd_parts,
                        timeout=180,  # Increased from 30 to 180 seconds for slow commands
                        capture_output=True
                    )

        except subprocess.TimeoutExpired:
            return 1, "", "Command execution timed out"
        except KeyboardInterrupt:
            return 1, "", "\n→ Operation cancelled"
        except Exception as e:
            return 1, "", f"Execution error: {str(e)}"

    def _expand_safe_env_vars(self, command: str) -> str:
        """
        Safely expand environment variables in command (v1.1.1 Enhanced Auto-Locator)

        Only expands CCMD-related variables for security
        Auto-detects CCMD_HOME if not set or incorrect

        Args:
            command: Command string with env vars

        Returns:
            Command with expanded env vars
        """
        import re

        # Auto-detect CCMD installation directory
        ccmd_home = self._get_ccmd_home()

        # Only expand safe, known CCMD variables
        safe_vars = {
            'CCMD_HOME': ccmd_home,
            'HOME': os.path.expanduser('~'),
        }

        # Replace each safe variable (handle Windows and Unix paths)
        for var_name, var_value in safe_vars.items():
            # Normalize path separators for the platform
            if var_value:
                var_value = str(Path(var_value))

            # Replace $VAR_NAME and ${VAR_NAME}
            command = command.replace(f'${var_name}', var_value)
            command = command.replace(f'${{{var_name}}}', var_value)

        return command

    def _get_ccmd_home(self) -> str:
        """
        Auto-detect CCMD installation directory (v1.1.1 Auto-Locator)

        This method intelligently finds the CCMD installation directory by:
        1. First checking CCMD_HOME environment variable
        2. If not set or invalid, calculating from the current file location
        3. Validating that run.py exists at the detected location

        Returns:
            Absolute path to CCMD installation directory
        """
        # Method 1: Try environment variable first
        env_ccmd_home = os.environ.get('CCMD_HOME', '')
        if env_ccmd_home:
            env_path = Path(env_ccmd_home)
            if env_path.exists() and (env_path / 'run.py').exists():
                return str(env_path.resolve())

        # Method 2: Calculate from current file location
        # This file is at: ccmd/core/executor.py
        # CCMD_HOME is 2 levels up
        current_file = Path(__file__).resolve()
        ccmd_home = current_file.parent.parent.parent

        # Validate that run.py exists
        if (ccmd_home / 'run.py').exists():
            return str(ccmd_home)

        # Method 3: Fallback to environment variable even if invalid
        # (let the command fail with a clear error message)
        return env_ccmd_home or str(ccmd_home)

    def _search_directory(self, dir_name: str) -> Optional[str]:
        """
        Search for a directory by name in common locations (v1.1.7)

        This mirrors the search_directory function in main.py for use
        in command chaining when 'go <dir>' needs to find a directory.

        Args:
            dir_name: Directory name to search for

        Returns:
            Full path to directory if found, None otherwise
        """
        # Common search locations
        if sys.platform == 'win32':
            username = os.environ.get('USERNAME', '')
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
            # Linux/macOS/WSL
            search_paths = [
                os.path.expanduser("~"),
                "/mnt/c/Users/rober",
                "/mnt/c/Users/rober/Downloads",
                "/mnt/c/Users/rober/targlobal",
            ]

        # Search up to 3 levels deep in each path
        for base_path in search_paths:
            if not os.path.exists(base_path):
                continue

            try:
                for root, dirs, files in os.walk(base_path):
                    # Calculate depth
                    depth = root[len(base_path):].count(os.sep)

                    # Limit search depth to 3
                    if depth >= 3:
                        dirs[:] = []  # Don't descend further
                        continue

                    # Check for exact match (case-insensitive)
                    for d in dirs:
                        if d.lower() == dir_name.lower():
                            return os.path.join(root, d)

            except PermissionError:
                continue

        return None

    def _execute_interactive(self, command: str) -> Tuple[int, str, str]:
        """
        Execute interactive commands that need terminal control (SECURITY ENHANCED v1.1.1)

        Args:
            command: Command to execute

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            # For commands like cd, we need to output the command for shell evaluation
            # The actual directory change must happen in the shell that sourced CCMD
            if command.startswith('cd '):
                # Output command to be evaluated by calling shell
                return 0, command, ""

            # For other interactive commands, parse safely and run without shell=True
            # IMPORTANT: Explicitly inherit stdin/stdout/stderr for interactive input
            # NOTE: No timeout for interactive commands (they run as long as user needs)
            cmd_parts = self.subprocess_runner.parse_shell_command(command)
            result = subprocess.run(
                cmd_parts,
                shell=False,  # SECURITY: Never use shell=True
                stdin=None,   # Inherit from parent (connected to terminal)
                stdout=None,  # Inherit from parent (connected to terminal)
                stderr=None,  # Inherit from parent (connected to terminal)
                timeout=None  # No timeout for interactive commands
            )
            return result.returncode, "", ""

        except Exception as e:
            return 1, "", f"Interactive execution error: {str(e)}"

    def execute_git_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute git commands with additional validation (SECURITY ENHANCED v1.1.1)

        Args:
            command: Git command to execute

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        # Ensure we're in a git repository
        if not self._is_git_repository():
            return 1, "", "Not a git repository"

        # Execute the command securely (shell=False is now default)
        return self.execute(command, interactive=False, shell=False)

    def _is_git_repository(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def get_shell_command_wrapper(self, command: str) -> str:
        """
        Wrap a command for shell execution

        Args:
            command: Command to wrap

        Returns:
            Wrapped command string
        """
        # For cd commands, return as-is for shell evaluation
        if command.startswith('cd '):
            return command

        # For other commands, execute via Python
        ccmd_path = Path(__file__).parent.parent.parent
        python_exec = sys.executable

        # SECURITY: Set CCMD_INTERNAL=1 to allow --exec for internal command chaining
        # This prevents external users from calling --exec directly
        shell_type = self.system_info.shell_type if self.system_info else 'bash'

        if shell_type == 'powershell':
            # PowerShell syntax: $env:VAR=value; command
            env_prefix = '$env:CCMD_INTERNAL=1; '
        else:
            # Bash/Zsh/Fish syntax: VAR=value command
            env_prefix = 'CCMD_INTERNAL=1 '

        return f'{env_prefix}"{python_exec}" "{ccmd_path}/run.py" --exec "{command}"'


class CommandOutput:
    """Handle command output formatting"""

    @staticmethod
    def print_success(message: str):
        """Print success message"""
        print(f"✓ {message}")

    @staticmethod
    def print_error(message: str):
        """Print error message"""
        print(f"✗ Error: {message}", file=sys.stderr)

    @staticmethod
    def print_info(message: str):
        """Print info message"""
        print(f"→ {message}")

    @staticmethod
    def print_command_output(stdout: str, stderr: str):
        """Print command output"""
        if stdout:
            print(stdout, end='')
        if stderr:
            print(stderr, end='', file=sys.stderr)


def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input to prevent injection attacks (SECURITY ENHANCED v1.1.1)

    Args:
        user_input: Raw user input

    Returns:
        Sanitized input
    """
    # Use the security module's sanitizer
    return CommandSecurityValidator.sanitize_user_input(user_input)


def quote_shell_arg(arg: str) -> str:
    """
    Safely quote a shell argument (NEW in v1.1.1)

    Args:
        arg: Argument to quote

    Returns:
        Safely quoted argument
    """
    return CommandSecurityValidator.sanitize_shell_arg(arg)


def prompt_user(prompt_text: str) -> str:
    """
    Safely prompt user for input

    Args:
        prompt_text: Prompt message

    Returns:
        Sanitized user input
    """
    try:
        user_input = input(f"{prompt_text}: ")
        return sanitize_input(user_input)
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        sys.exit(0)
    except EOFError:
        return ""
