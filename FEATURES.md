# CCMD Features

## Core Features

### ✨ Custom Command Management (v1.1.0+)

Create and manage your own custom commands that persist across CCMD updates!

**Commands:**
- `add` - Create a new custom command interactively
- `remove` - Delete a custom command
- `reload` - Reload configuration and update shell integration

**Features:**
- Commands stored in `~/.ccmd/custom_commands.yaml` (separate from CCMD defaults)
- Survives CCMD updates - your custom commands never get overwritten
- Interactive creation with helpful prompts
- Auto-updates shell integration after adding/removing commands
- Platform-aware reload instructions

**Example:**
```bash
# Create a custom command
add
> Enter command name: myls
> Enter description: My custom ls with colors
> Enter command: ls -la --color=auto
> Interactive? No

# Use it immediately after reloading
. $PROFILE  # or source ~/.bashrc
myls

# Remove it when no longer needed
remove
```

### 🔄 Configuration Reload

Instantly reload your CCMD configuration without manual reinstall:

```bash
reload
```

This command:
- Reloads all commands from `commands.yaml`
- Includes custom commands from `~/.ccmd/custom_commands.yaml`
- Updates shell integration automatically
- Shows platform-specific reload instructions
- No need to manually run `--install` anymore!

### 🎯 Interactive Push (v1.1.0+)

Enhanced git workflow with interactive prompts:

```bash
push
```

**Features:**
- Select which directory to push from
- Git repository validation
- File selection (add all or select specific files)
- Auto-generated commit messages based on changes
- Option to write custom commit message
- Push confirmation
- Full error handling and helpful messages

### 📋 Command List Editor (v1.1.0+)

Manage which commands are available in your shell:

```bash
list
```

**Features:**
- Interactive command list with enable/disable toggle
- Shows command descriptions
- Marks custom commands with `[CUSTOM]` badge
- Marks disabled commands with `[DISABLED]` badge
- Auto-updates shell integration after changes

### 🛡️ Graceful Cancellation (v1.1.0+)

All interactive commands now handle Ctrl+C gracefully:

- Shows "→ Action cancelled" instead of ugly stack traces
- Exits cleanly without errors
- Works across all platforms (Linux, WSL, Windows, macOS)

### 🌍 Cross-Platform Support

CCMD works on:
- ✅ **Linux** (Ubuntu, Debian, Fedora, Arch, etc.)
- ✅ **WSL** (Windows Subsystem for Linux) - Tested on WSL 2
- ✅ **Windows PowerShell** - Fully tested
- ⚠️ **macOS** - Code supports it, but untested (we need your feedback!)

**Shells Supported:**
- Bash
- Zsh
- Fish
- PowerShell

### 📁 Smart Directory Navigation

Navigate to common directories with shortcuts and search:

```bash
# Predefined locations
go downloads   # → ~/Downloads
go documents   # → ~/Documents
go desktop     # → ~/Desktop
go home        # → ~
go ccmd        # → $CCMD_HOME

# Smart search (finds directories in common locations)
go myproject   # Searches and navigates to "myproject"
go lha         # Finds and navigates to LHA directory
```

**Features (v1.1.0+):**
- Cross-platform search (works on Windows, Linux, WSL)
- Searches up to 3 levels deep in common locations
- Case-insensitive matching
- Optimized for performance

### ⚙️ Built-in System Commands

**System Monitoring:**
```bash
cpu   # Show CPU usage
mem   # Show memory usage
proc  # Show running processes
```

**Process Management:**
```bash
kap <pid>   # Kill a process by PID
```

**Git Operations:**
```bash
push   # Interactive git add, commit, and push
```

**CCMD Management:**
```bash
update     # Update CCMD from GitHub
version    # Show current and latest version
restore    # Restore shell config from backup
uninstall  # Remove CCMD
reload     # Reload configuration (v1.1.0+)
list       # Manage commands (v1.1.0+)
add        # Add custom command (v1.1.0+)
remove     # Remove custom command (v1.1.0+)
```

## Configuration

### Command Structure

Commands are defined in YAML format:

```yaml
commands:
  mycommand:
    description: What this command does
    action: the command to execute
    type: command_type
    interactive: false  # Set to true for commands needing user input
```

### Command Types

- `navigation` - Directory navigation commands
- `git` - Git-related operations
- `system` - System monitoring/management
- `internal` - CCMD management commands
- `custom` - User-defined commands (v1.1.0+)

### Platform-Specific Actions

Commands can have different actions per platform:

```yaml
mycommand:
  description: Cross-platform command
  action:
    linux: command for linux
    macos: command for macOS
    windows: command for Windows
```

### Interactive Commands

Commands marked as `interactive: true` run with direct terminal access:

```yaml
push:
  description: Git push
  interactive: true
  action: git add . && git commit -m "{message}" && git push
```

## Advanced Features

### Backup & Restore

CCMD automatically backs up your shell configuration before making changes:

- Backups stored in `~/.ccmd/backups/`
- Includes timestamp in filename
- Restore with `restore` command
- Multiple backups maintained

### Command Disabling

Disable commands without deleting them:

1. Run `list` command
2. Toggle commands on/off
3. Save and reload shell

Disabled commands are tracked in `$CCMD_HOME/.disabled_commands`

### Custom Command Persistence

Custom commands survive CCMD updates because they're stored separately:

- **CCMD defaults:** `$CCMD_HOME/commands.yaml` (overwritten on update)
- **Your customs:** `~/.ccmd/custom_commands.yaml` (never touched)

### Shell Integration

CCMD generates shell-specific integration code:

- **Bash/Zsh:** Function wrappers in `.bashrc`/`.zshrc`
- **Fish:** Function files in Fish syntax
- **PowerShell:** Function definitions in `$PROFILE`

Features:
- Automatic `cd` command detection
- Output capture for non-interactive commands
- Direct execution for interactive commands
- Error checking with helpful messages

## Platform-Specific Features

### Windows PowerShell

- UTF-8 console encoding for Unicode support
- Windows-specific system commands
- PowerShell-native implementations
- Full path resolution for Windows paths

### WSL (Windows Subsystem for Linux)

- Access to both Linux and Windows filesystems
- `/mnt/c/` path support
- Cross-platform directory search
- Works with Windows Python or WSL Python

### Linux

- Full compatibility with all distributions
- Native shell integration
- Optimal performance with `find` command
- Standard Unix tools support

### macOS (Untested)

- Code supports macOS
- Should work with both Bash and Zsh
- We need community testing and feedback!
- Please report issues on GitHub

## Version History

### v1.1.0 (Current)
- ✨ Custom commands feature
- ✨ `add` and `remove` commands
- ✨ `reload` command for quick config updates
- ✨ Interactive push with full workflow
- ✨ Command list editor with enable/disable
- ✨ Graceful Ctrl+C handling
- 🐛 Fixed PowerShell encoding issues
- 🐛 Fixed directory search on Windows
- 🐛 Fixed interactive command hanging
- 📝 Platform-aware reload instructions

### v1.0.6
- System monitoring commands
- Git integration
- Directory navigation
- Cross-platform support

### v1.0.0
- Initial release
- Basic command management
- Shell integration

## Experimental Features

These features are available but may need refinement:

- macOS support (untested)
- Fish shell integration (code exists, needs testing)
- PowerShell on macOS (untested)

## Contributing

Want to add a feature? Check out [CONTRIBUTING.md](CONTRIBUTING.md)

Found a bug? Open an issue on [GitHub](https://github.com/Wisyle/ccmd/issues)

Have feedback on macOS? We especially need testing on:
- macOS Monterey, Ventura, Sonoma
- Both Intel and Apple Silicon
- Both Bash and Zsh shells
