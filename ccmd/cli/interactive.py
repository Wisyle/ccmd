"""Interactive command features for CCMD"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import subprocess

# Fix Windows console encoding for Unicode support
if sys.platform == 'win32':
    try:
        # Try to set console to UTF-8 mode (Windows 10+)
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # UTF-8
    except:
        pass  # Ignore if fails

try:
    import questionary
    from questionary import Style
except ImportError:
    questionary = None

try:
    import git
except ImportError:
    git = None


# Custom style for questionary prompts
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),       # Question mark - purple
    ('question', 'bold'),                # Question text
    ('answer', 'fg:#2196f3 bold'),      # Selected answer - blue
    ('pointer', 'fg:#673ab7 bold'),     # Pointer - purple
    ('highlighted', 'fg:#673ab7 bold'), # Highlighted choice - purple
    ('selected', 'fg:#4caf50'),         # Selected items - green
    ('separator', 'fg:#cc5454'),        # Separator - red
    ('instruction', ''),                 # Instructions
    ('text', ''),                        # Plain text
    ('disabled', 'fg:#858585 italic')   # Disabled choices - gray
])


class Colors:
    """ANSI color codes"""
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


def safe_input(prompt: str) -> str:
    """Safe input wrapper that handles Ctrl+C gracefully"""
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}→ Action cancelled{Colors.END}")
        sys.exit(0)
    except EOFError:
        print(f"\n{Colors.YELLOW}→ Action cancelled{Colors.END}")
        sys.exit(0)


def check_dependencies() -> Tuple[bool, str]:
    """Check if required dependencies are installed"""
    missing = []

    if questionary is None:
        missing.append('questionary')
    if git is None:
        missing.append('GitPython')

    if missing:
        return False, f"Missing dependencies: {', '.join(missing)}\nRun: pip install {' '.join(missing)}"

    return True, ""


def check_git_repo(directory: Path) -> Tuple[bool, str, Optional[any]]:
    """
    Check if directory is a git repository

    Returns:
        Tuple of (is_repo, message, repo_object)
    """
    try:
        repo = git.Repo(directory, search_parent_directories=True)
        return True, "", repo
    except git.InvalidGitRepositoryError:
        return False, "Not a git repository", None
    except git.NoSuchPathError:
        return False, "Directory does not exist", None
    except Exception as e:
        return False, str(e), None


def check_git_config(repo) -> Tuple[bool, List[str]]:
    """Check if git is properly configured"""
    issues = []

    try:
        # Check if git is installed
        subprocess.run(['git', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        issues.append("Git is not installed")
        return False, issues

    # Check user config
    try:
        user_name = repo.config_reader().get_value('user', 'name', default=None)
        if not user_name:
            issues.append("Git user.name not configured")
    except:
        issues.append("Could not read git config")

    try:
        user_email = repo.config_reader().get_value('user', 'email', default=None)
        if not user_email:
            issues.append("Git user.email not configured")
    except:
        pass

    # Check for remote
    if not repo.remotes:
        issues.append("No remote repository configured")

    return len(issues) == 0, issues


def get_git_status(repo) -> dict:
    """Get detailed git status"""
    status = {
        'untracked': [],
        'modified': [],
        'staged': [],
        'deleted': [],
        'branch': 'unknown',
        'ahead': 0,
        'behind': 0
    }

    try:
        # Get branch
        status['branch'] = repo.active_branch.name

        # Get untracked files
        status['untracked'] = repo.untracked_files

        # Get modified files
        status['modified'] = [item.a_path for item in repo.index.diff(None)]

        # Get staged files
        status['staged'] = [item.a_path for item in repo.index.diff('HEAD')]

        # Get deleted files
        status['deleted'] = [item.a_path for item in repo.index.diff(None) if item.deleted_file]

    except Exception as e:
        print(f"{Colors.RED}Error getting git status: {e}{Colors.END}")

    return status


def generate_commit_message(repo) -> str:
    """Generate a commit message based on git diff"""
    try:
        # Get staged changes
        diff = repo.git.diff('--cached')

        if not diff:
            return "Update files"

        # Analyze diff to generate message
        lines = diff.split('\n')

        # Count file types and changes
        added_files = []
        modified_files = []
        deleted_files = []

        current_file = None
        for line in lines:
            if line.startswith('diff --git'):
                parts = line.split(' ')
                if len(parts) >= 4:
                    current_file = parts[3].replace('b/', '')
            elif line.startswith('new file'):
                if current_file:
                    added_files.append(current_file)
            elif line.startswith('deleted file'):
                if current_file:
                    deleted_files.append(current_file)
            elif current_file and current_file not in added_files and current_file not in deleted_files:
                if current_file not in modified_files:
                    modified_files.append(current_file)

        # Generate message based on changes
        parts = []

        if added_files:
            if len(added_files) == 1:
                parts.append(f"Add {Path(added_files[0]).name}")
            else:
                parts.append(f"Add {len(added_files)} files")

        if modified_files:
            if len(modified_files) == 1:
                parts.append(f"Update {Path(modified_files[0]).name}")
            else:
                parts.append(f"Update {len(modified_files)} files")

        if deleted_files:
            if len(deleted_files) == 1:
                parts.append(f"Delete {Path(deleted_files[0]).name}")
            else:
                parts.append(f"Delete {len(deleted_files)} files")

        if parts:
            return " and ".join(parts)
        else:
            return "Update files"

    except Exception as e:
        print(f"{Colors.YELLOW}Could not auto-generate commit message: {e}{Colors.END}")
        return "Update files"


def interactive_push():
    """Interactive git push with all features"""

    # Check dependencies
    if git is None:
        print(f"{Colors.RED}✗ GitPython not installed. Run: pip install GitPython{Colors.END}")
        return 1

    # Step 1: Select directory
    print()
    print(f"{Colors.BOLD}{Colors.CYAN}=== Interactive Git Push ==={Colors.END}")
    print()
    print("Where do you want to push from?")
    print(f"  {Colors.GREEN}1.{Colors.END} Current directory")
    print(f"  {Colors.GREEN}2.{Colors.END} Another directory")
    print()
    sys.stdout.flush()  # Force output to display

    choice = safe_input(f"{Colors.CYAN}Enter choice (1-2): {Colors.END}").strip()

    if choice == '2':
        dir_path = safe_input(f"{Colors.CYAN}Enter directory path [{os.getcwd()}]: {Colors.END}").strip()
        if not dir_path:
            dir_path = os.getcwd()
        directory = Path(dir_path).expanduser().resolve()
    elif choice == '1':
        directory = Path.cwd()
    else:
        print(f"{Colors.RED}✗ Invalid choice{Colors.END}")
        return 1

    print(f"\n{Colors.CYAN}→ Using directory: {directory}{Colors.END}\n")

    # Step 2: Check if it's a git repo
    is_repo, msg, repo = check_git_repo(directory)

    if not is_repo:
        print(f"{Colors.RED}✗ {msg}{Colors.END}")
        print(f"{Colors.YELLOW}→ Initialize a git repository with: git init{Colors.END}")
        return 1

    print(f"{Colors.GREEN}✓ Git repository found{Colors.END}")

    # Step 3: Check git configuration
    config_ok, config_issues = check_git_config(repo)

    if not config_ok:
        print(f"{Colors.RED}✗ Git configuration issues:{Colors.END}")
        for issue in config_issues:
            print(f"  {Colors.YELLOW}• {issue}{Colors.END}")
        print()

        if "not installed" in ' '.join(config_issues):
            return 1

        # Offer to configure
        cont = safe_input(f"\n{Colors.CYAN}Continue anyway? (y/N): {Colors.END}").strip().lower()
        if cont != 'y' and cont != 'yes':
            return 1
    else:
        print(f"{Colors.GREEN}✓ Git configuration OK{Colors.END}")

    print()

    # Step 4: Get git status
    status = get_git_status(repo)

    print(f"{Colors.BOLD}Current branch:{Colors.END} {Colors.CYAN}{status['branch']}{Colors.END}")
    print()

    # Show file status
    all_files = []

    if status['modified']:
        print(f"{Colors.YELLOW}Modified files:{Colors.END} {len(status['modified'])}")
        all_files.extend([(f, 'modified') for f in status['modified']])

    if status['untracked']:
        print(f"{Colors.YELLOW}Untracked files:{Colors.END} {len(status['untracked'])}")
        all_files.extend([(f, 'untracked') for f in status['untracked']])

    if status['deleted']:
        print(f"{Colors.RED}Deleted files:{Colors.END} {len(status['deleted'])}")
        all_files.extend([(f, 'deleted') for f in status['deleted']])

    if not all_files:
        print(f"{Colors.GREEN}✓ No changes to commit{Colors.END}")
        return 0

    print()

    # Step 5: File selection
    print("How do you want to stage files?")
    print(f"  {Colors.GREEN}1.{Colors.END} Add all files")
    print(f"  {Colors.GREEN}2.{Colors.END} Select specific files")
    print()
    sys.stdout.flush()

    file_choice = safe_input(f"{Colors.CYAN}Enter choice (1-2): {Colors.END}").strip()

    if file_choice == '1':
        # Add all files
        repo.git.add(A=True)
        print(f"{Colors.GREEN}✓ Added all files{Colors.END}\n")
    elif file_choice == '2':
        # Show files and let user select
        print(f"\n{Colors.BOLD}Available files:{Colors.END}")
        for i, (file, status_type) in enumerate(all_files, 1):
            print(f"  {Colors.GREEN}{i}.{Colors.END} [{status_type}] {file}")

        print()
        sys.stdout.flush()
        selection = safe_input(f"{Colors.CYAN}Enter file numbers (comma-separated, e.g., 1,3,5) or 'all': {Colors.END}").strip()

        if selection.lower() == 'all':
            for file, _ in all_files:
                repo.git.add(file)
            print(f"{Colors.GREEN}✓ Added all files{Colors.END}\n")
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
            except ValueError:
                print(f"{Colors.RED}✗ Invalid selection - please enter numbers{Colors.END}")
                return 1

            added = 0
            for idx in indices:
                if 0 <= idx < len(all_files):
                    try:
                        repo.git.add(all_files[idx][0])
                        added += 1
                    except Exception as e:
                        print(f"{Colors.YELLOW}⚠ Could not add {all_files[idx][0]}: {e}{Colors.END}")

            if added > 0:
                print(f"{Colors.GREEN}✓ Added {added} file(s){Colors.END}\n")
            else:
                print(f"{Colors.RED}✗ No files were added{Colors.END}")
                return 1
    else:
        print(f"{Colors.RED}✗ Invalid choice{Colors.END}")
        return 1

    # Step 6: Commit message
    auto_message = generate_commit_message(repo)

    print("Commit message:")
    print(f"  {Colors.GREEN}1.{Colors.END} Use auto-generated: {Colors.YELLOW}\"{auto_message}\"{Colors.END}")
    print(f"  {Colors.GREEN}2.{Colors.END} Write custom message")
    print()
    sys.stdout.flush()

    msg_choice = safe_input(f"{Colors.CYAN}Enter choice (1-2): {Colors.END}").strip()

    if msg_choice == '2':
        commit_message = safe_input(f"{Colors.CYAN}Enter commit message: {Colors.END}").strip()
        if not commit_message:
            print(f"{Colors.YELLOW}No commit message provided{Colors.END}")
            return 1
    elif msg_choice == '1':
        commit_message = auto_message
    else:
        print(f"{Colors.RED}✗ Invalid choice{Colors.END}")
        return 1

    # Create commit
    try:
        repo.git.commit('-m', commit_message)
        print(f"{Colors.GREEN}✓ Committed: {commit_message}{Colors.END}\n")
    except Exception as e:
        print(f"{Colors.RED}✗ Commit failed: {e}{Colors.END}")
        return 1

    # Step 7: Push
    push_confirm = safe_input(f"\n{Colors.CYAN}Push to '{status['branch']}'? (Y/n): {Colors.END}").strip().lower()

    if push_confirm != 'n' and push_confirm != 'no':
        try:
            print(f"{Colors.CYAN}→ Pushing to {status['branch']}...{Colors.END}")
            repo.git.push()
            print(f"{Colors.GREEN}✓ Successfully pushed to {status['branch']}!{Colors.END}\n")
        except Exception as e:
            print(f"{Colors.RED}✗ Push failed: {e}{Colors.END}")
            return 1
    else:
        print(f"{Colors.YELLOW}→ Skipped push{Colors.END}")

    return 0


def interactive_list_editor():
    """Interactive command list editor to enable/disable commands"""

    # Load config
    from ccmd.core.registry import CommandRegistry

    # Get CCMD_HOME
    ccmd_home = os.environ.get('CCMD_HOME')
    if not ccmd_home:
        print(f"{Colors.RED}✗ CCMD_HOME not set{Colors.END}")
        return 1

    config_path = Path(ccmd_home) / 'commands.yaml'
    if not config_path.exists():
        print(f"{Colors.RED}✗ commands.yaml not found{Colors.END}")
        return 1

    # Load disabled commands config
    disabled_config_path = Path(ccmd_home) / '.disabled_commands'
    disabled_commands = set()

    if disabled_config_path.exists():
        with open(disabled_config_path, 'r') as f:
            disabled_commands = set(line.strip() for line in f if line.strip())

    registry = CommandRegistry(config_path)
    all_commands = sorted(registry.list_commands())

    while True:
        # Show current status
        print()
        print(f"{Colors.BOLD}{Colors.CYAN}=== Command List Editor ==={Colors.END}")
        print()

        for i, cmd in enumerate(all_commands, 1):
            cmd_def = registry.get_command(cmd)
            desc = cmd_def.get('description', 'No description')
            status = f"{Colors.RED}[DISABLED]{Colors.END}" if cmd in disabled_commands else f"{Colors.GREEN}[ENABLED] {Colors.END}"
            custom_badge = f"{Colors.PURPLE}[CUSTOM]{Colors.END} " if registry.is_custom_command(cmd) else ""

            print(f"  {Colors.GREEN}{i:2}.{Colors.END} {status} {custom_badge}{cmd:12} - {desc[:50]}")

        print()
        print(f"  {Colors.YELLOW}0. Save and exit{Colors.END}")
        print()
        sys.stdout.flush()

        # Get selection
        selection = safe_input(f"{Colors.CYAN}Enter command number to toggle (0 to exit): {Colors.END}").strip()

        if selection == '0':
            break

        try:
            idx = int(selection) - 1
            if 0 <= idx < len(all_commands):
                cmd = all_commands[idx]
                # Toggle command
                if cmd in disabled_commands:
                    disabled_commands.remove(cmd)
                    print(f"{Colors.GREEN}✓ Enabled: {cmd}{Colors.END}")
                else:
                    disabled_commands.add(cmd)
                    print(f"{Colors.YELLOW}→ Disabled: {cmd}{Colors.END}")
            else:
                print(f"{Colors.RED}✗ Invalid number{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}✗ Invalid input{Colors.END}")

    # Save disabled commands
    with open(disabled_config_path, 'w') as f:
        for cmd in sorted(disabled_commands):
            f.write(f"{cmd}\n")

    print(f"{Colors.GREEN}✓ Configuration saved!{Colors.END}")
    print(f"{Colors.CYAN}→ Run 'update' to apply changes to shell integration{Colors.END}\n")

    return 0


def interactive_add_command():
    """Interactive custom command creator"""
    import os
    from pathlib import Path
    from ccmd.core.registry import CommandRegistry

    print()
    print(f"{Colors.BOLD}{Colors.CYAN}=== Add Custom Command ==={Colors.END}")
    print()
    print(f"{Colors.YELLOW}Custom commands are stored in ~/.ccmd/custom_commands.yaml{Colors.END}")
    print(f"{Colors.YELLOW}They persist even when CCMD is updated!{Colors.END}")
    print()
    sys.stdout.flush()

    # Get CCMD_HOME
    ccmd_home = os.environ.get('CCMD_HOME')
    if not ccmd_home:
        print(f"{Colors.RED}✗ CCMD_HOME not set{Colors.END}")
        return 1

    config_path = Path(ccmd_home) / 'commands.yaml'
    if not config_path.exists():
        print(f"{Colors.RED}✗ commands.yaml not found{Colors.END}")
        return 1

    registry = CommandRegistry(config_path)

    # Get command name
    while True:
        cmd_name = safe_input(f"{Colors.CYAN}Enter command name (e.g., 'mycommand'): {Colors.END}").strip()

        if not cmd_name:
            print(f"{Colors.RED}✗ Command name cannot be empty{Colors.END}")
            continue

        # Check if name contains spaces or special characters
        if not cmd_name.replace('_', '').replace('-', '').isalnum():
            print(f"{Colors.RED}✗ Command name can only contain letters, numbers, hyphens, and underscores{Colors.END}")
            continue

        # Check if command already exists
        if registry.command_exists(cmd_name):
            if registry.is_custom_command(cmd_name):
                overwrite = safe_input(f"{Colors.YELLOW}⚠ Custom command '{cmd_name}' already exists. Overwrite? (y/N): {Colors.END}").strip().lower()
                if overwrite not in ['y', 'yes']:
                    continue
            else:
                print(f"{Colors.RED}✗ '{cmd_name}' is a built-in command. Choose a different name.{Colors.END}")
                continue

        break

    # Get description
    description = safe_input(f"{Colors.CYAN}Enter command description: {Colors.END}").strip()
    if not description:
        description = f"Custom command: {cmd_name}"

    # Get action/command
    print()
    print("Enter the command to run (examples):")
    print(f"  {Colors.GREEN}•{Colors.END} Simple: ls -la")
    print(f"  {Colors.GREEN}•{Colors.END} Python: python3 /path/to/script.py")
    print(f"  {Colors.GREEN}•{Colors.END} Multiple: cd ~ && ls")
    print(f"  {Colors.GREEN}•{Colors.END} Navigation: cd /path/to/directory")
    print()
    sys.stdout.flush()

    action = safe_input(f"{Colors.CYAN}Enter command: {Colors.END}").strip()

    if not action:
        print(f"{Colors.RED}✗ Command action cannot be empty{Colors.END}")
        return 1

    # Determine if it's interactive
    print()
    print(f"Is this command interactive (requires user input)?")
    print(f"  {Colors.GREEN}1.{Colors.END} No (default)")
    print(f"  {Colors.GREEN}2.{Colors.END} Yes (interactive)")
    print()
    sys.stdout.flush()

    interactive_choice = safe_input(f"{Colors.CYAN}Enter choice (1-2) [1]: {Colors.END}").strip()
    is_interactive = interactive_choice == '2'

    # Create command definition
    command_def = {
        'description': description,
        'action': action,
        'type': 'custom'
    }

    if is_interactive:
        command_def['interactive'] = True

    # Add command
    try:
        registry.add_command(cmd_name, command_def, is_custom=True)
        registry.save_custom_commands()
        print()
        print(f"{Colors.GREEN}✓ Custom command '{cmd_name}' added successfully!{Colors.END}")
        print()

        # Automatically reinstall to update shell integration
        print(f"{Colors.CYAN}→ Updating shell integration...{Colors.END}")
        from ccmd.cli.install import install_ccmd
        success, message = install_ccmd()

        if success:
            print(f"{Colors.GREEN}✓ Shell integration updated!{Colors.END}")
            print()
            # Show appropriate reload command based on platform
            if sys.platform == 'win32':
                print(f"{Colors.BOLD}→ Run: . $PROFILE{Colors.END}")
            else:
                print(f"{Colors.BOLD}→ Run: source ~/.bashrc{Colors.END}")
            print(f"{Colors.CYAN}→ Then use your new command: {cmd_name}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
            print(f"{Colors.CYAN}→ You may need to run 'reload' manually{Colors.END}")
        print()
    except Exception as e:
        print(f"{Colors.RED}✗ Failed to add command: {e}{Colors.END}")
        return 1

    return 0


def interactive_remove_command():
    """Interactive custom command remover"""
    import os
    from pathlib import Path
    from ccmd.core.registry import CommandRegistry

    print()
    print(f"{Colors.BOLD}{Colors.CYAN}=== Remove Custom Command ==={Colors.END}")
    print()

    # Get CCMD_HOME
    ccmd_home = os.environ.get('CCMD_HOME')
    if not ccmd_home:
        print(f"{Colors.RED}✗ CCMD_HOME not set{Colors.END}")
        return 1

    config_path = Path(ccmd_home) / 'commands.yaml'
    if not config_path.exists():
        print(f"{Colors.RED}✗ commands.yaml not found{Colors.END}")
        return 1

    registry = CommandRegistry(config_path)
    custom_commands = registry.list_custom_commands()

    if not custom_commands:
        print(f"{Colors.YELLOW}No custom commands found{Colors.END}")
        print(f"{Colors.CYAN}→ Use 'add' to create custom commands{Colors.END}")
        print()
        return 0

    # Show custom commands
    print(f"{Colors.BOLD}Your custom commands:{Colors.END}")
    print()

    for i, cmd in enumerate(sorted(custom_commands), 1):
        cmd_def = registry.get_command(cmd)
        desc = cmd_def.get('description', 'No description')
        action = cmd_def.get('action', '')
        print(f"  {Colors.GREEN}{i}.{Colors.END} {Colors.BOLD}{cmd}{Colors.END} - {desc}")
        print(f"     {Colors.YELLOW}→{Colors.END} {action[:60]}{'...' if len(action) > 60 else ''}")
        print()

    print(f"  {Colors.YELLOW}0. Cancel{Colors.END}")
    print()
    sys.stdout.flush()

    # Get selection
    selection = safe_input(f"{Colors.CYAN}Enter command number to remove (0 to cancel): {Colors.END}").strip()

    if selection == '0':
        print(f"{Colors.YELLOW}→ Cancelled{Colors.END}")
        return 0

    try:
        idx = int(selection) - 1
        sorted_commands = sorted(custom_commands)

        if 0 <= idx < len(sorted_commands):
            cmd_name = sorted_commands[idx]

            # Confirm deletion
            confirm = safe_input(f"{Colors.YELLOW}⚠ Remove '{cmd_name}'? (y/N): {Colors.END}").strip().lower()

            if confirm in ['y', 'yes']:
                registry.remove_command(cmd_name)
                registry.save_custom_commands()
                print(f"{Colors.GREEN}✓ Removed custom command: {cmd_name}{Colors.END}")
                print()

                # Automatically reinstall to update shell integration
                print(f"{Colors.CYAN}→ Updating shell integration...{Colors.END}")
                from ccmd.cli.install import install_ccmd
                success, message = install_ccmd()

                if success:
                    print(f"{Colors.GREEN}✓ Shell integration updated!{Colors.END}")
                    print()
                    # Show appropriate reload command based on platform
                    if sys.platform == 'win32':
                        print(f"{Colors.BOLD}→ Run: . $PROFILE{Colors.END}")
                    else:
                        print(f"{Colors.BOLD}→ Run: source ~/.bashrc{Colors.END}")
                    print(f"{Colors.CYAN}→ Command '{cmd_name}' is now removed{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
                    print(f"{Colors.CYAN}→ You may need to run 'reload' manually{Colors.END}")
                print()
            else:
                print(f"{Colors.YELLOW}→ Cancelled{Colors.END}")
        else:
            print(f"{Colors.RED}✗ Invalid number{Colors.END}")
            return 1

    except ValueError:
        print(f"{Colors.RED}✗ Invalid input{Colors.END}")
        return 1

    return 0
