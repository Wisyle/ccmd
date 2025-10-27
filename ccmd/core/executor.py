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

    def validate_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a command for safety using security module

        Args:
            command: Command string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        return self.validator.validate_command(command)

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
        # Step 1: Validate command syntax
        is_valid, error = self.validate_command(command)
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

        # Step 6: Execute command
        try:
            return self.execute(command, interactive=interactive, shell=allow_shell)
        except KeyboardInterrupt:
            return 1, "", "\n→ Operation cancelled"

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
                    # shell=True allowed ONLY for predefined system commands
                    # These are from commands.yaml with type=system/internal
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    return result.returncode, result.stdout, result.stderr
                else:
                    # Secure execution without shell=True (for user commands)
                    cmd_parts = self.subprocess_runner.parse_shell_command(command)
                    return self.subprocess_runner.run_command_safe(
                        cmd_parts,
                        timeout=30,
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
        Safely expand environment variables in command (v1.1.1 FIX)

        Only expands CCMD-related variables for security

        Args:
            command: Command string with env vars

        Returns:
            Command with expanded env vars
        """
        import re

        # Only expand safe, known CCMD variables
        safe_vars = {
            'CCMD_HOME': os.environ.get('CCMD_HOME', ''),
            'HOME': os.path.expanduser('~'),
        }

        # Replace each safe variable
        for var_name, var_value in safe_vars.items():
            # Replace $VAR_NAME and ${VAR_NAME}
            command = command.replace(f'${var_name}', var_value)
            command = command.replace(f'${{{var_name}}}', var_value)

        return command

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
            cmd_parts = self.subprocess_runner.parse_shell_command(command)
            result = subprocess.run(
                cmd_parts,
                shell=False,  # SECURITY: Never use shell=True
                stdin=None,   # Inherit from parent (connected to terminal)
                stdout=None,  # Inherit from parent (connected to terminal)
                stderr=None,  # Inherit from parent (connected to terminal)
                timeout=30
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

        return f'"{python_exec}" "{ccmd_path}/run.py" --exec "{command}"'


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
