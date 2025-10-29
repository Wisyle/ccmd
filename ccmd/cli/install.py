"""Installation module for CCMD"""

import sys
import os
from pathlib import Path
from typing import Tuple

# Fix Windows console encoding for Unicode support
if sys.platform == 'win32':
    try:
        # Try to set console to UTF-8 mode (Windows 10+)
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # UTF-8
    except:
        pass  # Ignore if fails

from ccmd.core.system_check import get_system_info
from ccmd.core.registry import CommandRegistry, create_default_config
from ccmd.core.rollback import RollbackManager


def install_ccmd() -> Tuple[bool, str]:
    """
    Install CCMD by adding command aliases to shell configuration

    Returns:
        Tuple of (success, message)
    """
    import subprocess

    system_info = get_system_info()
    rollback = RollbackManager()

    # Get installation directory
    install_dir = Path(__file__).parent.parent.parent.resolve()
    run_py = install_dir / "run.py"

    if not run_py.exists():
        return False, f"run.py not found at {run_py}"

    # Install Python dependencies from requirements.txt
    requirements_file = install_dir / "requirements.txt"
    if requirements_file.exists():
        print("→ Installing Python dependencies...")
        try:
            # First try regular pip install
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", "-r", str(requirements_file)],
                check=True,
                capture_output=True
            )
            print("✓ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            # If regular install fails, try with --break-system-packages for externally-managed systems
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--break-system-packages", "-q", "-r", str(requirements_file)],
                    check=True,
                    capture_output=True
                )
                print("✓ Dependencies installed successfully")
            except subprocess.CalledProcessError:
                # If both attempts fail, show warning (dependencies might already be installed)
                print(f"⚠ Warning: Could not install dependencies automatically")
                print("  Dependencies may already be installed, or you may need to run:")
                print(f"  pip3 install -r {requirements_file}")

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

    # Load disabled commands
    disabled_config_path = install_dir / ".disabled_commands"
    disabled_commands = set()

    if disabled_config_path.exists():
        with open(disabled_config_path, 'r') as f:
            disabled_commands = set(line.strip() for line in f if line.strip())

    # Filter out disabled commands
    commands = [cmd for cmd in commands if cmd not in disabled_commands]

    if not commands:
        return False, "All commands are disabled"

    # Get shell RC file
    rc_file = system_info.shell_rc_file
    if not rc_file:
        return False, f"Could not determine shell RC file for {system_info.shell_type}"

    # Generate shell integration code
    if system_info.shell_type in ['bash', 'zsh']:
        integration_code = generate_bash_integration(install_dir, run_py, commands, registry)
    elif system_info.shell_type == 'fish':
        integration_code = generate_fish_integration(install_dir, run_py, commands)
    elif system_info.shell_type == 'powershell':
        integration_code = generate_powershell_integration(install_dir, run_py, commands, registry)
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
        # Platform-specific reload instructions
        if system_info.shell_type == 'powershell':
            reload_cmd = ". $PROFILE"
        elif system_info.shell_type == 'fish':
            reload_cmd = f"source {rc_file}"
        else:  # bash/zsh
            reload_cmd = f"source {rc_file}"

        return True, f"CCMD installed successfully! Restart your shell or run: {reload_cmd}"
    else:
        return False, message


def generate_bash_integration(install_dir: Path, run_py: Path, commands: list, registry) -> str:
    """Generate Bash/Zsh integration code"""
    python_exec = sys.executable

    code = "# CCMD Integration - Start\n"
    code += f"export CCMD_HOME=\"{install_dir}\"\n\n"

    # Add error flag to show message only once
    code += "export _CCMD_ERROR_SHOWN=0\n\n"

    # Helper function to check CCMD availability
    code += """_ccmd_check() {
    if [ ! -f "$CCMD_HOME/run.py" ]; then
        if [ "$_CCMD_ERROR_SHOWN" -eq 0 ]; then
            echo "⚠ CCMD not found at $CCMD_HOME"
            echo "→ Please reinstall CCMD or run: python3 /path/to/ccmd/run.py --uninstall"
            echo "→ To silence this message, remove CCMD integration from your shell config"
            export _CCMD_ERROR_SHOWN=1
        fi
        return 1
    fi
    return 0
}

"""

    # Create function for each command
    for cmd in commands:
        # Check if command is interactive
        cmd_def = registry.get_command(cmd)
        is_interactive = cmd_def.get('interactive', False)

        if is_interactive:
            # Interactive commands: run directly without output capture
            code += f"""{cmd}() {{
    _ccmd_check || return 1
    "{python_exec}" "$CCMD_HOME/run.py" {cmd} "$@"
    return $?
}}

"""
        else:
            # Non-interactive commands: capture output for cd handling
            code += f"""{cmd}() {{
    _ccmd_check || return 1

    local output
    output=$("{python_exec}" "$CCMD_HOME/run.py" {cmd} "$@")
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

    code += "# CCMD Integration - End\n"
    return code


def generate_fish_integration(install_dir: Path, run_py: Path, commands: list) -> str:
    """Generate Fish shell integration code"""
    python_exec = sys.executable

    code = "# CCMD Integration - Start\n"
    code += f"set -gx CCMD_HOME \"{install_dir}\"\n"
    code += "set -gx _CCMD_ERROR_SHOWN 0\n\n"

    # Helper function to check CCMD availability
    code += """function _ccmd_check
    if not test -f "$CCMD_HOME/run.py"
        if test "$_CCMD_ERROR_SHOWN" -eq 0
            echo "⚠ CCMD not found at $CCMD_HOME"
            echo "→ Please reinstall CCMD or run: python3 /path/to/ccmd/run.py --uninstall"
            echo "→ To silence this message, remove CCMD integration from your shell config"
            set -gx _CCMD_ERROR_SHOWN 1
        end
        return 1
    end
    return 0
end

"""

    for cmd in commands:
        code += f"""function {cmd}
    _ccmd_check; or return 1

    set output ({python_exec} "$CCMD_HOME/run.py" {cmd} $argv)

    if string match -q -r '^cd ' "$output"
        eval "$output"
    else
        echo "$output"
    end
end

"""

    code += "# CCMD Integration - End\n"
    return code


def generate_powershell_integration(install_dir: Path, run_py: Path, commands: list, registry) -> str:
    """Generate PowerShell integration code"""
    python_exec = sys.executable

    code = "# CCMD Integration - Start\n"
    code += f"$env:CCMD_HOME = \"{install_dir}\"\n"
    code += "$global:_CCMD_ERROR_SHOWN = 0\n\n"

    # Helper function to check CCMD availability
    code += """function _ccmd_check {
    if (-not (Test-Path "$env:CCMD_HOME/run.py")) {
        if ($global:_CCMD_ERROR_SHOWN -eq 0) {
            Write-Host "⚠ CCMD not found at $env:CCMD_HOME" -ForegroundColor Yellow
            Write-Host "→ Please reinstall CCMD or run: python3 /path/to/ccmd/run.py --uninstall"
            Write-Host "→ To silence this message, remove CCMD integration from your PowerShell profile"
            $global:_CCMD_ERROR_SHOWN = 1
        }
        return $false
    }
    return $true
}

"""

    # Create function for each command
    for cmd in commands:
        # Check if command is interactive
        cmd_def = registry.get_command(cmd)
        is_interactive = cmd_def.get('interactive', False)

        if is_interactive:
            # Interactive commands: run directly without output capture
            code += f"""function {cmd} {{
    if (-not (_ccmd_check)) {{ return }}
    & "{python_exec}" "$env:CCMD_HOME/run.py" {cmd} $args
}}

"""
        else:
            # Non-interactive commands: capture output for cd handling
            code += f"""function {cmd} {{
    if (-not (_ccmd_check)) {{ return }}

    $output = & "{python_exec}" "$env:CCMD_HOME/run.py" {cmd} $args

    if ($output -match '^cd ') {{
        Invoke-Expression $output
    }} else {{
        Write-Output $output
    }}
}}

"""

    code += "# CCMD Integration - End\n"
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
