# CCMD v1.1.0 Release Notes

**Release Date:** October 26, 2025

## Overview

CCMD v1.1.0 brings major new features focused on customization and user experience improvements. This release introduces the ability to create your own custom commands, instant configuration reloading, enhanced git workflows, and comprehensive cross-platform testing on Windows PowerShell.

## New Features

### Custom Commands System
- **Add your own commands** with the new `add` command
- **Interactive creation** with prompts for name, description, and action
- **Persistent storage** in `~/.ccmd/custom_commands.yaml` - survives CCMD updates
- **Remove commands** easily with the `remove` command
- Custom commands override defaults if same name exists

### Instant Configuration Reload
- **New `reload` command** to update configuration without manual reinstall
- Automatically updates shell integration after adding/removing commands
- Platform-aware reload instructions (shows `. $PROFILE` on Windows, `source ~/.bashrc` on Linux)

### Enhanced Interactive Push
- **Full git workflow** with interactive file selection
- **Auto-generated commit messages** based on changed files
- **Directory selection** when multiple git repos available
- **Repository validation** with helpful error messages
- **Push confirmation** before executing

### Command List Manager
- **New `list` command** to manage available commands
- **Enable/disable commands** without deleting them
- Shows `[CUSTOM]` badge for user-created commands
- Shows `[DISABLED]` badge for disabled commands
- Auto-updates shell integration after changes

### Graceful Cancellation
- **Ctrl+C handling** across all interactive commands
- Clean "→ Action cancelled" message instead of ugly tracebacks
- Works consistently on all platforms (Linux, WSL, Windows, macOS)

### Windows PowerShell Improvements
- **Full PowerShell support** with comprehensive testing
- **UTF-8 console encoding** for proper Unicode character display
- **Interactive command support** - fixed hanging issues with input()
- **Cross-platform directory search** using Python's os.walk()
- **Platform-specific messages** showing correct reload commands

## Bug Fixes

### Windows/PowerShell
- Fixed directory search hanging on Windows by optimizing search paths and depth limits
- Fixed interactive commands (push, add, remove, list) hanging in PowerShell
- Fixed Unicode character encoding errors (✓, ✗, →) in Windows console
- Fixed reload instructions showing Linux commands in PowerShell

### General
- Fixed command registry to properly merge custom and default commands
- Fixed shell integration not updating automatically after config changes
- Improved error handling for missing dependencies

## Platform Testing

This release has been tested on:
- ✅ **Linux** (Ubuntu/Debian on WSL)
- ✅ **WSL** (Windows Subsystem for Linux)
- ✅ **Windows PowerShell**

**Note:** macOS support exists in the code but remains **untested**. We're counting on macOS users to test and provide feedback. Please report any issues on [GitHub Issues](https://github.com/Wisyle/ccmd/issues).

## Breaking Changes

None. This release is fully backward compatible with v1.0.x configurations.

## Upgrade Instructions

### If installed via Git:
```bash
cd /path/to/ccmd
git pull origin ccmd
python3 run.py --install
```

### If installed via ZIP:
1. Download the latest release from https://github.com/Wisyle/ccmd/releases/latest
2. Extract and replace your existing ccmd folder
3. Run the installer: `bash setup.sh` (Linux/macOS/WSL) or `.\setup.ps1` (PowerShell)

**Your custom commands will be preserved** - they're stored separately in `~/.ccmd/custom_commands.yaml`

## Documentation

Updated documentation includes:
- **[FEATURES.md](FEATURES.md)** - Complete feature list with v1.1.0 highlights
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Updated with reload command guidance
- **[README.md](README.md)** - Updated with new commands and features

## Technical Changes

### New Commands
- `add` - Create custom commands interactively
- `remove` - Remove custom commands
- `reload` - Reload configuration and update shell integration
- `list` - Manage command availability (enable/disable)

### New Files
- `~/.ccmd/custom_commands.yaml` - User's custom commands (auto-created)
- `$CCMD_HOME/.disabled_commands` - Tracks disabled commands

### Modified Modules
- `ccmd/cli/main.py` - Added UTF-8 encoding, cross-platform search, reload handler
- `ccmd/cli/interactive.py` - Added safe_input() wrapper, custom command functions
- `ccmd/core/registry.py` - Added custom commands support and merging
- `ccmd/cli/install.py` - Added interactive command detection for shell integration
- `ccmd/core/rollback.py` - Added UTF-8 file operations

## Known Issues

- macOS compatibility is untested - community testing needed
- Fish shell integration exists but needs additional testing

## Community

We need your help testing on macOS! If you're a macOS user:
1. Test CCMD on your system (Intel or Apple Silicon)
2. Report any issues on [GitHub Issues](https://github.com/Wisyle/ccmd/issues)
3. Share your experience with the community

## Credits

Developed by **De Catalyst (Wisyle)**
- GitHub: [@Wisyle](https://github.com/Wisyle)
- Email: Robert5560newton@gmail.com
- X (Twitter): [@iamdecatalyst](https://x.com/iamdecatalyst)

## What's Next?

v1.2.0 roadmap (tentative):
- macOS testing and fixes
- Fish shell testing
- Plugin system enhancements
- Performance optimizations
- Additional system monitoring commands

---

**Full Changelog:** https://github.com/Wisyle/ccmd/compare/v1.0.6...v1.1.0
