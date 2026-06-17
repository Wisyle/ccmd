# CCMD v1.0.3 Release Notes

**Release Date:** 2025-10-26

## Overview

Version 1.0.3 is a patch release that adds uninstall functionality and graceful error handling for missing CCMD installations. This release improves the user experience when CCMD is moved or deleted without proper cleanup.

## New Features

### 1. Uninstall Command
- **Added `--uninstall` flag** to cleanly remove CCMD shell integration
- **Added `uninstall` command** to commands.yaml for easy access
- Usage:
  ```bash
  python3 run.py --uninstall
  # or after installation:
  uninstall
  ```
- Automatically removes all CCMD functions from shell configuration
- Creates backup before uninstalling (can be restored with `--restore`)

### 2. Graceful Error Handling
- **Smart path validation** - Commands now check if CCMD exists before executing
- **One-time error notification** - Shows helpful error message only once per shell session
- **No shell breakage** - Missing CCMD installation no longer blocks shell startup
- **Cross-platform support** - Error handling works on Bash, Zsh, Fish, and PowerShell

**Error Message Example:**
```
⚠ CCMD not found at /path/to/ccmd
→ Please reinstall CCMD or run: python3 /path/to/ccmd/run.py --uninstall
→ To silence this message, remove CCMD integration from your shell config
```

## Bug Fixes

- Fixed issue where deleted CCMD directory caused all commands to fail
- Fixed issue where shell startup was blocked by missing CCMD paths
- Improved shell integration to handle edge cases gracefully

## Technical Changes

### Shell Integration Updates

**Bash/Zsh:**
- Added `_ccmd_check()` helper function for path validation
- Added `_CCMD_ERROR_SHOWN` flag to prevent repeated error messages
- Commands now use `$CCMD_HOME` variable instead of hardcoded paths

**Fish Shell:**
- Added `_ccmd_check` function with Fish-compatible syntax
- Proper error handling with `test -f` command
- Updated all command functions to check availability first

**PowerShell:**
- Added `_ccmd_check` function with PowerShell syntax
- Uses `Test-Path` for path validation
- Proper color-coded warning messages

### CLI Updates

- Added `--uninstall` argument to main CLI parser
- Added `handle_uninstall()` function in main.py
- Exposed existing `uninstall_ccmd()` function from install.py
- Updated help text to include uninstall option

## Version Updates

- Updated `__version__` to "1.0.3" in ccmd/__init__.py
- Updated README.md download link to v1.0.3
- Updated commands.yaml with uninstall command

## Compatibility

- **Operating Systems:** Linux, macOS, Windows, WSL
- **Shells:** Bash, Zsh, Fish, PowerShell
- **Python:** 3.7+
- **Dependencies:** PyYAML >= 6.0

## Upgrade Instructions

### Method 1: Git Users

```bash
cd /path/to/ccmd
git pull origin ccmd
python3 run.py --install
source ~/.bashrc  # or ~/.zshrc
```

### Method 2: ZIP Download

1. Download v1.0.3 from: https://github.com/Wisyle/ccmd/releases/latest
2. Extract and replace your existing ccmd folder
3. Run: `python3 run.py --install`
4. Reload your shell

## Usage Examples

### Uninstall CCMD
```bash
# Method 1: Using the command
uninstall

# Method 2: Using the flag
python3 run.py --uninstall

# Restart your shell after uninstalling
source ~/.bashrc
```

### Reinstall after moving CCMD
```bash
# If you moved CCMD to a new location
cd /new/path/to/ccmd
python3 run.py --install  # This will update shell integration
source ~/.bashrc
```

## Breaking Changes

None. This release is fully backward compatible with v1.0.2 and v1.0.1.

## Known Issues

None reported.

## Contributors

- **De Catalyst** (@Wisyle) - Lead Developer

## Support

- **GitHub Issues:** https://github.com/Wisyle/ccmd/issues
- **Email:** Robert5560newton@gmail.com
- **X (Twitter):** [@iamdecatalyst](https://x.com/iamdecatalyst)

---

**Full Changelog:** v1.0.2...v1.0.3

Previous releases:
- [v1.0.2](RELEASE_NOTES_v1.0.2.md) - Global path support
- [v1.0.1](RELEASE_NOTES_v1.0.1.md) - Update/restore command fixes
- [v1.0.0](RELEASE_NOTES_v1.0.0.md) - Initial release
