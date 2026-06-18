"""First-run setup wizard for CCMD.

Lets users register their own `go` directory shortcuts (written to
~/.ccmd/shortcuts.yaml) and optionally set a master password. Triggered
automatically on first install when stdout is a TTY, and manually via
`ccmd setup`.

Visual idiom (Colors banners + safe_input + numbered menus) matches
interactive_add_command in interactive.py.
"""

import os
import re
import sys
from pathlib import Path
from typing import Tuple

from ccmd.cli.interactive import Colors, safe_input
from ccmd.core.registry import CommandRegistry
from ccmd.core.auth import initialize_password_interactive, HAS_BCRYPT, AUTH_FILE


# Sentinel file written on completion so the wizard doesn't re-trigger
# automatically on every install.
SETUP_SENTINEL = Path.home() / ".ccmd" / ".setup_done"

# Shortcut names must be valid shell identifiers (alnum + dash/underscore)
_SHORTCUT_NAME_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_-]*$')


def setup_is_done() -> bool:
    """True if the first-run wizard has already been completed."""
    return SETUP_SENTINEL.exists()


def _mark_setup_done():
    """Write the sentinel so the wizard won't auto-trigger again."""
    try:
        SETUP_SENTINEL.parent.mkdir(parents=True, exist_ok=True)
        SETUP_SENTINEL.touch()
    except OSError:
        # Non-fatal: worst case the wizard re-runs on next install.
        pass


def _expand_path(raw: str) -> str:
    """Expand ~ and env vars in a user-entered path."""
    return os.path.expanduser(os.path.expandvars(raw.strip()))


def _read_shortcut(registry: CommandRegistry, existing: dict) -> Tuple[str, str]:
    """Prompt for a single shortcut (name, path). Returns ('', '') to stop.

    `existing` is the current shortcuts dict (used to offer overwrite).
    """
    # Name
    while True:
        name = safe_input(
            f"{Colors.CYAN}Shortcut name (blank to finish): {Colors.END}"
        ).strip()
        if not name:
            return '', ''
        if not _SHORTCUT_NAME_RE.match(name):
            print(f"{Colors.RED}✗ Name must start with a letter and contain only "
                  f"letters, numbers, '-' or '_'{Colors.END}")
            continue
        if name in existing:
            overwrite = safe_input(
                f"{Colors.YELLOW}⚠ '{name}' already exists. Overwrite? (y/N): {Colors.END}"
            ).strip().lower()
            if overwrite not in ('y', 'yes'):
                continue
        break

    # Path
    while True:
        raw_path = safe_input(
            f"{Colors.CYAN}Directory path for '{name}' (e.g. ~/projects/myapp): {Colors.END}"
        ).strip()
        if not raw_path:
            print(f"{Colors.YELLOW}→ Skipped '{name}' (no path given){Colors.END}")
            return '', ''
        path = _expand_path(raw_path)
        if not os.path.isdir(path):
            print(f"{Colors.YELLOW}⚠ '{path}' does not exist. Add anyway? (y/N): {Colors.END}",
                  end='')
            confirm = safe_input("").strip().lower()
            if confirm not in ('y', 'yes'):
                continue
        break

    return name, path


def _collect_shortcuts(registry: CommandRegistry) -> dict:
    """Run the shortcut-entry loop. Returns the new shortcuts map."""
    print()
    print(f"{Colors.BOLD}Register your directory shortcuts{Colors.END}")
    print(f"These power the {Colors.GREEN}go{Colors.END} command — e.g. "
          f"{Colors.GREEN}go projects{Colors.END} jumps to that folder.")
    print(f"Stored in {Colors.CYAN}~/.ccmd/shortcuts.yaml{Colors.END} "
          f"(survives updates).")
    print()

    existing = registry.list_user_shortcuts()
    if existing:
        print(f"{Colors.YELLOW}Current shortcuts:{Colors.END}")
        for k, v in existing.items():
            print(f"  {Colors.GREEN}{k}{Colors.END} → {v}")
        print()

    added = dict(existing)
    count = 0
    while True:
        name, path = _read_shortcut(registry, added)
        if not name:
            break
        added[name] = path
        try:
            registry.add_shortcut(name, path)
            count += 1
            print(f"{Colors.GREEN}✓ Added '{name}' → {path}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to save '{name}': {e}{Colors.END}")
        print()

    if count:
        print(f"{Colors.GREEN}✓ {count} shortcut(s) saved.{Colors.END}")
    else:
        print(f"{Colors.YELLOW}→ No new shortcuts added.{Colors.END}")
    print()
    return added


def _offer_password():
    """Offer to initialize the master password (optional)."""
    if AUTH_FILE.exists():
        # Already set — don't badger the user.
        return
    print(f"{Colors.BOLD}Master password (optional){Colors.END}")
    print(f"Protects sensitive commands (SSH, sudo, etc.). You can skip this "
          f"and set it later with {Colors.GREEN}ccmd --init{Colors.END}.")
    print()
    choice = safe_input(
        f"{Colors.CYAN}Set a master password now? (y/N): {Colors.END}"
    ).strip().lower()
    if choice not in ('y', 'yes'):
        print(f"{Colors.YELLOW}→ Skipped. Run 'ccmd --init' anytime to set it.{Colors.END}")
        print()
        return

    if not HAS_BCRYPT:
        print(f"{Colors.YELLOW}⚠ bcrypt not installed — install with "
              f"'pip install bcrypt' then run 'ccmd --init'.{Colors.END}")
        print()
        return

    success, message = initialize_password_interactive()
    if success:
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    else:
        print(f"{Colors.YELLOW}→ {message}{Colors.END}")
    print()


def run_setup(skip_password: bool = False) -> int:
    """Run the first-run setup wizard.

    Args:
        skip_password: if True, don't offer master-password init
                       (used by automated/non-TTY paths).

    Returns:
        0 on success, non-zero on error.
    """
    print()
    print(f"{Colors.BOLD}{Colors.CYAN}=== CCMD Setup ==={Colors.END}")
    print()
    print(f"Welcome to CCMD! Let's get you set up.")
    print()

    # Resolve a registry so we can read/write shortcuts.
    ccmd_home = os.environ.get('CCMD_HOME')
    if ccmd_home:
        config_path = Path(ccmd_home) / 'commands.yaml'
    else:
        config_path = None  # registry falls back to default path
    try:
        registry = CommandRegistry(config_path)
    except Exception as e:
        print(f"{Colors.RED}✗ Could not load command registry: {e}{Colors.END}")
        return 1

    try:
        _collect_shortcuts(registry)
        if not skip_password:
            _offer_password()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}→ Setup cancelled.{Colors.END}")
        # Still mark done if at least the shortcuts were saved — the user
        # can always re-run 'ccmd setup'.
        _mark_setup_done()
        return 0

    _mark_setup_done()

    print(f"{Colors.BOLD}{Colors.GREEN}✓ Setup complete!{Colors.END}")
    print()
    print(f"{Colors.CYAN}Quick start:{Colors.END}")
    print(f"  • {Colors.GREEN}go <shortcut>{Colors.END}  — jump to a registered directory")
    print(f"  • {Colors.GREEN}ccmd add{Colors.END}      — create a custom command")
    print(f"  • {Colors.GREEN}ccmd list{Colors.END}     — see all commands")
    print(f"  • {Colors.GREEN}ccmd setup{Colors.END}    — re-run this wizard anytime")
    print()
    return 0


def maybe_run_setup_on_install() -> bool:
    """Auto-trigger the wizard at the end of install, if appropriate.

    Conditions: sentinel absent AND stdout is a TTY. Scripted/CI installs
    (non-TTY) are left alone.

    Returns:
        True if the wizard ran, False otherwise.
    """
    if setup_is_done():
        return False
    if not sys.stdout.isatty():
        return False
    try:
        run_setup()
        return True
    except Exception:
        # Never let the setup wizard break an otherwise-successful install.
        return False
