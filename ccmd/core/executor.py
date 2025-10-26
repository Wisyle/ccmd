"""Safe command executor module"""

import subprocess
import shlex
import sys
import os
import re
from typing import Tuple, Optional, List
from pathlib import Path


class CommandExecutor:
    """Safely execute shell commands"""

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r';\s*rm\s+-rf',  # Destructive rm commands
        r'\|\s*rm\s+-rf',
        r'&&\s*rm\s+-rf',
        r'>\s*/dev/sd[a-z]',  # Writing to disk devices
        r':\(\)\{.*\|.*&\};:',  # Fork bombs
        r'dd\s+if=/dev/zero',  # Disk wiping
        r'mkfs\.',  # Filesystem formatting
        r':\(\)\{',  # Fork bomb pattern
    ]

    def __init__(self, system_info=None):
        """
        Initialize executor

        Args:
            system_info: SystemInfo instance
        """
        self.system_info = system_info

    def validate_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a command for safety

        Args:
            command: Command string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not command or not command.strip():
            return False, "Empty command"

        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Potentially dangerous command pattern detected"

        # Additional validation
        # Block commands that try to modify system directories
        dangerous_paths = ['/etc', '/sys', '/boot', '/dev', 'C:\\Windows', 'C:\\System32']
        for path in dangerous_paths:
            if f'rm -rf {path}' in command or f'del /s {path}' in command.lower():
                return False, f"Cannot execute commands targeting system directories"

        return True, None

    def execute(self, command: str, interactive: bool = False,
                shell: bool = True) -> Tuple[int, str, str]:
        """
        Execute a command safely

        Args:
            command: Command to execute
            interactive: Whether command needs interactive terminal
            shell: Whether to use shell execution

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        # Validate command first
        is_valid, error = self.validate_command(command)
        if not is_valid:
            return 1, "", f"Command validation failed: {error}"

        try:
            if interactive:
                # For interactive commands like cd, we need special handling
                return self._execute_interactive(command)
            else:
                # Standard execution
                result = subprocess.run(
                    command,
                    shell=shell,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            return 1, "", "Command execution timed out"
        except Exception as e:
            return 1, "", f"Execution error: {str(e)}"

    def _execute_interactive(self, command: str) -> Tuple[int, str, str]:
        """
        Execute interactive commands that need terminal control

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

            # For other interactive commands, run with inherited stdio
            result = subprocess.run(
                command,
                shell=True,
                timeout=30
            )
            return result.returncode, "", ""

        except Exception as e:
            return 1, "", f"Interactive execution error: {str(e)}"

    def execute_git_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute git commands with additional validation

        Args:
            command: Git command to execute

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        # Ensure we're in a git repository
        if not self._is_git_repository():
            return 1, "", "Not a git repository"

        # Execute the command
        return self.execute(command, interactive=False, shell=True)

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
    Sanitize user input to prevent injection attacks

    Args:
        user_input: Raw user input

    Returns:
        Sanitized input
    """
    if not user_input:
        return ""

    # Remove null bytes
    sanitized = user_input.replace('\0', '')

    # Remove or escape dangerous characters
    # Keep alphanumeric, spaces, basic punctuation
    sanitized = re.sub(r'[;\|&$`<>]', '', sanitized)

    return sanitized.strip()


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
