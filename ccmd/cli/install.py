"""Installation module for CCMD"""

import sys
import os
from pathlib import Path
from typing import Tuple

from ccmd.core.system_check import get_system_info
from ccmd.core.registry import CommandRegistry, create_default_config
from ccmd.core.rollback import RollbackManager


def install_ccmd() -> Tuple[bool, str]:
    """
    Install CCMD by adding command aliases to shell configuration

    Returns:
        Tuple of (success, message)
    """
    system_info = get_system_info()
    rollback = RollbackManager()

    # Get installation directory
    install_dir = Path(__file__).parent.parent.parent.resolve()
    run_py = install_dir / "run.py"

    if not run_py.exists():
        return False, f"run.py not found at {run_py}"

    # Create default commands.yaml if it doesn't exist
    commands_yaml = install_dir / "commands.yaml"
    if not commands_yaml.exists():
        try:
            create_default_config(commands_yaml)
        except Exception as e:
            return False, f"Failed to create commands.yaml: {e}"

    # Load commands
    registry = CommandRegistry(commands_yaml)
    commands = registry.list_commands()

    if not commands:
        return False, "No commands found in commands.yaml"

    # Get shell RC file
    rc_file = system_info.shell_rc_file
    if not rc_file:
        return False, f"Could not determine shell RC file for {system_info.shell_type}"

    # Generate shell integration code
    if system_info.shell_type in ['bash', 'zsh']:
        integration_code = generate_bash_integration(install_dir, run_py, commands)
    elif system_info.shell_type == 'fish':
        integration_code = generate_fish_integration(install_dir, run_py, commands)
    elif system_info.shell_type == 'powershell':
        integration_code = generate_powershell_integration(install_dir, run_py, commands)
    else:
        return False, f"Unsupported shell: {system_info.shell_type}"

    # Add integration code to RC file
    def edit_rc_file(content: str) -> str:
        # Check if CCMD is already installed
        if "# CCMD Integration" in content:
            # Remove old integration
            lines = content.split('\n')
            new_lines = []
            skip = False

            for line in lines:
                if "# CCMD Integration - Start" in line:
                    skip = True
                elif "# CCMD Integration - End" in line:
                    skip = False
                    continue
                elif not skip:
                    new_lines.append(line)

            content = '\n'.join(new_lines)

        # Add new integration
        if not content.endswith('\n'):
            content += '\n'

        content += '\n' + integration_code + '\n'
        return content

    # Safely edit RC file with backup
    success, message = rollback.safe_file_edit(
        rc_file,
        edit_rc_file,
        "CCMD installation"
    )

    if success:
        return True, f"CCMD installed successfully! Restart your shell or run: source {rc_file}"
    else:
        return False, message


def generate_bash_integration(install_dir: Path, run_py: Path, commands: list) -> str:
    """Generate Bash/Zsh integration code"""
    python_exec = sys.executable

    code = "# CCMD Integration - Start\n"
    code += f"export CCMD_HOME=\"{install_dir}\"\n\n"

    # Create function for each command
    for cmd in commands:
        # For navigation commands (cd), we need special handling
        code += f"""
{cmd}() {{
    local output
    output=$("{python_exec}" "{run_py}" {cmd} "$@")
    local exit_code=$?

    # Check if output is a cd command
    if [[ "$output" =~ ^cd[[:space:]] ]]; then
        eval "$output"
    else
        echo "$output"
    fi

    return $exit_code
}}
"""

    code += "\n# CCMD Integration - End\n"
    return code


def generate_fish_integration(install_dir: Path, run_py: Path, commands: list) -> str:
    """Generate Fish shell integration code"""
    python_exec = sys.executable

    code = "# CCMD Integration - Start\n"
    code += f"set -gx CCMD_HOME \"{install_dir}\"\n\n"

    for cmd in commands:
        code += f"""
function {cmd}
    set output ({python_exec} "{run_py}" {cmd} $argv)

    if string match -q -r '^cd ' "$output"
        eval "$output"
    else
        echo "$output"
    end
end
"""

    code += "\n# CCMD Integration - End\n"
    return code


def generate_powershell_integration(install_dir: Path, run_py: Path, commands: list) -> str:
    """Generate PowerShell integration code"""
    python_exec = sys.executable

    code = "# CCMD Integration - Start\n"
    code += f"$env:CCMD_HOME = \"{install_dir}\"\n\n"

    for cmd in commands:
        code += f"""
function {cmd} {{
    $output = & "{python_exec}" "{run_py}" {cmd} $args

    if ($output -match '^cd ') {{
        Invoke-Expression $output
    }} else {{
        Write-Output $output
    }}
}}
"""

    code += "\n# CCMD Integration - End\n"
    return code


def uninstall_ccmd() -> Tuple[bool, str]:
    """
    Uninstall CCMD by removing integration code

    Returns:
        Tuple of (success, message)
    """
    system_info = get_system_info()
    rollback = RollbackManager()

    rc_file = system_info.shell_rc_file
    if not rc_file or not rc_file.exists():
        return False, "Shell RC file not found"

    def remove_integration(content: str) -> str:
        lines = content.split('\n')
        new_lines = []
        skip = False

        for line in lines:
            if "# CCMD Integration - Start" in line:
                skip = True
            elif "# CCMD Integration - End" in line:
                skip = False
                continue
            elif not skip:
                new_lines.append(line)

        return '\n'.join(new_lines)

    success, message = rollback.safe_file_edit(
        rc_file,
        remove_integration,
        "CCMD uninstallation"
    )

    if success:
        return True, "CCMD uninstalled successfully"
    else:
        return False, message
