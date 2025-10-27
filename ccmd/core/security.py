"""Security utilities module for CCMD - v1.1.1
Provides command validation, secure subprocess execution, and file operations
"""

import os
import re
import shlex
import subprocess
import tempfile
import stat
import sys
from pathlib import Path
from typing import Tuple, List, Optional


class CommandSecurityValidator:
    """Validates commands for security issues before execution"""

    # Dangerous patterns that should be blocked
    DANGEROUS_PATTERNS = [
        r';\s*rm\s+-rf\s+/',  # Recursive delete from root
        r':\(\)\{.*\};:',      # Fork bomb
        r'>\s*/dev/sd[a-z]',   # Direct disk write
        r'\|\s*dd\s+of=',      # Piped disk write
        r'curl.*\|\s*bash',    # Pipe to bash
        r'wget.*\|\s*sh',      # Pipe to shell
    ]

    @classmethod
    def validate_command(cls, command: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a command for security issues

        Args:
            command: Command string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not command or not command.strip():
            return False, "Empty command"

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Command contains dangerous pattern: {pattern}"

        # Check for null bytes (command injection attempt)
        if '\0' in command:
            return False, "Command contains null bytes"

        return True, None

    @staticmethod
    def sanitize_user_input(user_input: str) -> str:
        """
        Sanitize user input to prevent injection attacks

        Args:
            user_input: Raw user input

        Returns:
            Sanitized input
        """
        # Remove null bytes
        sanitized = user_input.replace('\0', '')

        # Strip leading/trailing whitespace
        sanitized = sanitized.strip()

        return sanitized

    @staticmethod
    def sanitize_shell_arg(arg: str) -> str:
        """
        Safely quote a shell argument

        Args:
            arg: Argument to quote

        Returns:
            Safely quoted argument
        """
        return shlex.quote(arg)


class SecureSubprocess:
    """Handles secure subprocess execution without shell=True"""

    @staticmethod
    def parse_shell_command(command: str) -> List[str]:
        """
        Parse a shell command into safe argument list

        Args:
            command: Command string

        Returns:
            List of command parts
        """
        try:
            # Use shlex to properly parse the command
            # This handles quotes, escapes, etc.
            return shlex.split(command)
        except ValueError as e:
            # If parsing fails, fall back to simple split
            # This is safer than shell=True
            return command.split()

    @staticmethod
    def run_command_safe(cmd_parts: List[str], timeout: int = 30,
                        capture_output: bool = True) -> Tuple[int, str, str]:
        """
        Run a command safely without shell=True

        Args:
            cmd_parts: Command as list of arguments
            timeout: Timeout in seconds
            capture_output: Whether to capture stdout/stderr

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            if capture_output:
                result = subprocess.run(
                    cmd_parts,
                    shell=False,  # SECURITY: Never use shell=True
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(
                    cmd_parts,
                    shell=False,
                    timeout=timeout
                )
                return result.returncode, "", ""

        except subprocess.TimeoutExpired:
            return 1, "", f"Command timed out after {timeout} seconds"
        except FileNotFoundError:
            return 1, "", f"Command not found: {cmd_parts[0]}"
        except Exception as e:
            return 1, "", f"Execution error: {str(e)}"


class SecureFileOperations:
    """Handles secure file operations with atomic writes and proper permissions"""

    @staticmethod
    def atomic_write(file_path: Path, content: str, mode: int = 0o600) -> Tuple[bool, str]:
        """
        Atomically write to a file with secure permissions

        Args:
            file_path: Path to file
            content: Content to write
            mode: File permissions (Unix only)

        Returns:
            Tuple of (success, message)
        """
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temporary file first
            fd, temp_path = tempfile.mkstemp(
                dir=file_path.parent,
                prefix=f".{file_path.name}.",
                text=True
            )

            try:
                # Write content
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Set secure permissions before moving
                if sys.platform != 'win32':
                    os.chmod(temp_path, mode)
                else:
                    # Windows: Best effort
                    os.chmod(temp_path, stat.S_IREAD | stat.S_IWRITE)

                # Atomic move
                os.replace(temp_path, file_path)

                return True, "File written successfully"

            except Exception as e:
                # Clean up temp file on error
                try:
                    os.unlink(temp_path)
                except:
                    pass
                raise e

        except Exception as e:
            return False, f"Failed to write file: {e}"

    @staticmethod
    def set_secure_permissions(file_path: Path) -> bool:
        """
        Set secure permissions on a file (cross-platform)

        Args:
            file_path: Path to file

        Returns:
            True if successful
        """
        try:
            if sys.platform == 'win32':
                # Windows: Owner read/write only
                os.chmod(file_path, stat.S_IREAD | stat.S_IWRITE)
            else:
                # Unix: 0600 (owner read/write only)
                os.chmod(file_path, 0o600)
            return True
        except Exception:
            return False


class VersionSecurity:
    """Validates dependency versions for security"""

    MIN_VERSIONS = {
        'PyYAML': '6.0',
        'bcrypt': '4.0.0',
    }

    @classmethod
    def check_dependencies(cls) -> Tuple[bool, List[str]]:
        """
        Check if all security dependencies are installed with correct versions

        Returns:
            Tuple of (all_ok, list_of_warnings)
        """
        warnings = []

        # Check PyYAML
        try:
            import yaml
            # PyYAML doesn't have __version__, check safe_load exists
            if not hasattr(yaml, 'safe_load'):
                warnings.append("PyYAML is too old, please upgrade to >= 6.0")
        except ImportError:
            warnings.append("PyYAML not installed")

        # Check bcrypt
        try:
            import bcrypt
            if not hasattr(bcrypt, 'hashpw'):
                warnings.append("bcrypt is too old, please upgrade to >= 4.0.0")
        except ImportError:
            warnings.append("bcrypt not installed (optional for password protection)")

        return len(warnings) == 0, warnings


# Export main classes
__all__ = [
    'CommandSecurityValidator',
    'SecureSubprocess',
    'SecureFileOperations',
    'VersionSecurity',
]
