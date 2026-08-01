"""System detection module for OS and shell identification"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Tuple, Optional


class SystemInfo:
    """Detect and store system information"""

    def __init__(self):
        self.os_type = self._detect_os()
        self.shell_type = self._detect_shell()
        self.shell_rc_file = self._get_rc_file()
        self.is_wsl = self._is_wsl()

    def _detect_os(self) -> str:
        """Detect the operating system"""
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"

    def _is_wsl(self) -> bool:
        """Check if running under WSL"""
        if self.os_type == "linux":
            try:
                with open("/proc/version", "r") as f:
                    return "microsoft" in f.read().lower()
            except:
                return False
        return False

    def _detect_shell(self) -> str:
        """Detect the current shell"""
        # Check SHELL environment variable
        shell_path = os.environ.get("SHELL", "")

        if shell_path:
            shell_name = Path(shell_path).name
            if "bash" in shell_name:
                return "bash"
            elif "zsh" in shell_name:
                return "zsh"
            elif "fish" in shell_name:
                return "fish"

        # Windows detection
        if self.os_type == "windows":
            # Check if running in PowerShell
            if os.environ.get("PSModulePath"):
                return "powershell"
            else:
                return "cmd"

        # Default fallback
        return "bash"

    def _get_rc_file(self) -> Optional[Path]:
        """Get the appropriate shell RC file path"""
        home = Path.home()

        if self.shell_type == "bash":
            # Check for .bashrc first, then .bash_profile
            bashrc = home / ".bashrc"
            if bashrc.exists():
                return bashrc
            return home / ".bash_profile"

        elif self.shell_type == "zsh":
            return home / ".zshrc"

        elif self.shell_type == "fish":
            config_dir = home / ".config" / "fish"
            config_dir.mkdir(parents=True, exist_ok=True)
            return config_dir / "config.fish"

        elif self.shell_type == "powershell":
            # PowerShell profile path
            try:
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", "echo $PROFILE"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return Path(result.stdout.strip())
            except:
                pass
            # Fallback
            return home / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"

        return None

    def get_path_separator(self) -> str:
        """Get the PATH separator for the OS"""
        return ";" if self.os_type == "windows" else ":"

    def get_line_ending(self) -> str:
        """Get the appropriate line ending for the OS"""
        return "\r\n" if self.os_type == "windows" else "\n"

    def __str__(self) -> str:
        """String representation of system info"""
        return f"OS: {self.os_type}, Shell: {self.shell_type}, RC: {self.shell_rc_file}"


def get_system_info() -> SystemInfo:
    """Factory function to get system information"""
    return SystemInfo()


def is_unix_like() -> bool:
    """Check if running on Unix-like system"""
    return platform.system().lower() in ["linux", "darwin"]


def is_windows() -> bool:
    """Check if running on Windows"""
    return platform.system().lower() == "windows"
