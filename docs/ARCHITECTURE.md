# Architecture & Technical Documentation

## Project Overview

CCMD (Cross-platform Command Manager) is a Python-based command aliasing system that provides secure, cross-platform command shortcuts for terminal operations.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       User Terminal                         │
│  (Bash / Zsh / Fish / PowerShell / CMD)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Shell Function Call
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      run.py (Entry)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    ccmd.cli.main                            │
│                  (Argument Parser)                          │
└─────┬──────────────┬──────────────┬────────────────┬────────┘
      │              │              │                │
      ↓              ↓              ↓                ↓
 ┌─────────┐  ┌──────────┐  ┌──────────┐     ┌──────────┐
 │ install │  │  editor  │  │   ssh    │     │  Command │
 │         │  │          │  │ manager  │     │ Execution│
 └─────────┘  └──────────┘  └──────────┘     └────┬─────┘
                                                   │
                    ┌──────────────────────────────┘
                    │
      ┌─────────────┴──────────────┬──────────────┐
      ↓                            ↓              ↓
┌──────────┐              ┌─────────────┐  ┌──────────┐
│ registry │              │   parser    │  │ executor │
│          │──────────────→             │──→          │
└──────────┘              └─────────────┘  └──────────┘
      ↑                                          │
      │                                          ↓
┌──────────┐                              ┌──────────┐
│ rollback │                              │  System  │
│          │                              │  Shell   │
└──────────┘                              └──────────┘
      ↑
      │
┌──────────────┐
│ Backups Dir  │
└──────────────┘
```

## Project Structure

```
ccmd/
├── ccmd/                       # Main package
│   ├── __init__.py            # Package initialization
│   │
│   ├── core/                   # Core functionality modules
│   │   ├── __init__.py
│   │   ├── system_check.py    # OS and shell detection (197 lines)
│   │   ├── registry.py        # Command storage and loading (213 lines)
│   │   ├── parser.py          # Command parsing and routing (217 lines)
│   │   ├── executor.py        # Safe command execution (204 lines)
│   │   └── rollback.py        # Backup and restore (257 lines)
│   │
│   └── cli/                    # CLI interface modules
│       ├── __init__.py
│       ├── main.py            # CLI entry point (242 lines)
│       ├── install.py         # Installation logic (203 lines)
│       ├── editor.py          # Interactive editor (213 lines)
│       └── ssh_manager.py     # SSH management (310 lines)
│
├── commands.yaml              # Command definitions
├── run.py                     # Main entry point
├── setup.sh                   # Unix installation script
├── setup.ps1                  # Windows installation script
├── requirements.txt           # Python dependencies
│
└── Documentation/
    ├── README.md              # Main documentation
    ├── INSTALLATION.md        # Installation guide
    ├── USAGE.md               # Usage guide
    ├── CONFIGURATION.md       # Configuration guide
    ├── TROUBLESHOOTING.md     # Troubleshooting guide
    └── ARCHITECTURE.md        # This file
```

## Core Modules

### 1. system_check.py

**Purpose:** Detects operating system and shell type

**Key Functions:**
- `detect_os()` - Identifies Linux, macOS, Windows, or WSL
- `detect_shell()` - Identifies Bash, Zsh, Fish, PowerShell, or CMD
- `get_shell_rc_file()` - Returns appropriate RC file path

**Technologies:**
- `platform` module for OS detection
- Environment variable inspection
- Process name checking

**Code Reference:** `ccmd/core/system_check.py:1`

### 2. registry.py

**Purpose:** Manages command storage and loading from YAML

**Key Functions:**
- `load_commands()` - Loads commands from commands.yaml
- `save_commands()` - Saves commands to YAML
- `get_command()` - Retrieves specific command
- `add_command()` - Adds new command
- `delete_command()` - Removes command

**Technologies:**
- PyYAML for YAML parsing
- File I/O operations
- Data validation

**Code Reference:** `ccmd/core/registry.py:1`

### 3. parser.py

**Purpose:** Parses command-line arguments and routes to appropriate actions

**Key Functions:**
- `parse_args()` - Parses command-line arguments
- `route_command()` - Routes to appropriate handler
- `validate_syntax()` - Validates command syntax

**Technologies:**
- argparse for argument parsing
- Pattern matching for command routing

**Code Reference:** `ccmd/core/parser.py:1`

### 4. executor.py

**Purpose:** Safely executes commands with validation and security checks

**Key Functions:**
- `execute_command()` - Executes validated commands
- `sanitize_input()` - Sanitizes user input
- `validate_command()` - Validates command safety
- `substitute_params()` - Substitutes parameters safely

**Security Features:**
- Input sanitization
- Command validation
- Dangerous pattern blocking
- No eval() usage

**Code Reference:** `ccmd/core/executor.py:1`

### 5. rollback.py

**Purpose:** Creates backups and restores shell configurations

**Key Functions:**
- `create_backup()` - Creates timestamped backup
- `restore_backup()` - Restores from backup
- `list_backups()` - Lists available backups
- `clean_old_backups()` - Removes old backups

**Technologies:**
- File I/O operations
- Timestamp management
- Backup rotation

**Code Reference:** `ccmd/core/rollback.py:1`

## CLI Modules

### 1. main.py

**Purpose:** Main CLI entry point and argument parser

**Key Functions:**
- `main()` - Main entry point
- `handle_command()` - Routes to appropriate handler
- `print_help()` - Displays help information

**Code Reference:** `ccmd/cli/main.py:1`

### 2. install.py

**Purpose:** Handles installation and shell integration

**Key Functions:**
- `install()` - Installs CCMD to shell
- `add_shell_functions()` - Adds functions to RC file
- `create_aliases()` - Creates command aliases
- `verify_installation()` - Verifies successful installation

**Installation Process:**
1. Detects OS and shell
2. Creates ~/.ccmd directory
3. Backs up shell RC file
4. Adds CCMD integration block to RC file
5. Creates shell functions for each command

**Code Reference:** `ccmd/cli/install.py:1`

### 3. editor.py

**Purpose:** Interactive command editor

**Key Functions:**
- `run_editor()` - Main editor loop
- `add_command()` - Interactive command addition
- `edit_command()` - Interactive command editing
- `delete_command()` - Interactive command deletion
- `view_command()` - Display command details

**User Interface:**
- Menu-based interaction
- Input validation
- Command preview
- Confirmation prompts

**Code Reference:** `ccmd/cli/editor.py:1`

### 4. ssh_manager.py

**Purpose:** Manages SSH connection aliases

**Key Functions:**
- `add_ssh_alias()` - Adds SSH connection
- `edit_ssh_alias()` - Edits SSH connection
- `delete_ssh_alias()` - Removes SSH connection
- `list_ssh_aliases()` - Lists all SSH connections

**Features:**
- Host/user/port configuration
- SSH key management
- Connection testing
- Alias generation

**Code Reference:** `ccmd/cli/ssh_manager.py:1`

## Data Flow

### Command Execution Flow

1. **User Input**
   ```bash
   go downloads
   ```

2. **Shell Function** (in ~/.bashrc)
   ```bash
   go() {
       python3 /path/to/ccmd/run.py go "$@"
   }
   ```

3. **run.py Entry Point**
   - Receives: `['go', 'downloads']`
   - Calls: `ccmd.cli.main.main()`

4. **Argument Parser** (parser.py)
   - Identifies command: `go`
   - Identifies option: `downloads`

5. **Registry Lookup** (registry.py)
   - Loads commands.yaml
   - Retrieves `go` command definition
   - Finds `downloads` option

6. **Executor** (executor.py)
   - Validates command
   - Sanitizes input
   - Executes: `cd ~/Downloads`

7. **Output to Shell**
   - Returns: `cd ~/Downloads`
   - Shell evaluates output

### Installation Flow

1. **User runs setup.sh**
   ```bash
   bash setup.sh
   ```

2. **Setup Script**
   - Installs PyYAML
   - Calls `python3 run.py --install`

3. **install.py**
   - Detects OS/shell (system_check.py)
   - Creates backup (rollback.py)
   - Reads commands (registry.py)
   - Generates shell functions
   - Writes to RC file

4. **Shell Reload**
   ```bash
   source ~/.bashrc
   ```

5. **Commands Available**
   - All commands now work as shell functions

## Security Architecture

### Input Sanitization

**Level 1: Command Validation**
- Validates command exists in registry
- Checks command structure

**Level 2: Parameter Sanitization**
```python
def sanitize_input(user_input):
    # Remove dangerous characters
    # Escape special characters
    # Validate against whitelist
    return sanitized_input
```

**Level 3: Execution Validation**
- No eval() usage
- No shell=True in subprocess
- Whitelist-based execution

### Dangerous Pattern Blocking

Blocked patterns:
- `rm -rf /`
- `:(){ :|:& };:` (fork bomb)
- Arbitrary code execution attempts
- Path traversal attempts
- Command injection patterns

### Backup System

**Automatic Backups:**
- Created before any shell RC modification
- Timestamped format: `bashrc_backup_20231026_143022`
- Stored in: `~/.ccmd/backups/`
- Rotation: Keeps last 10 backups

## Dependencies

### Runtime Dependencies

```
PyYAML>=5.1
```

### System Requirements

- Python 3.7+
- One of:
  - Bash (Linux/macOS/WSL)
  - Zsh (macOS/Linux)
  - Fish (Linux/macOS)
  - PowerShell (Windows)
  - CMD (Windows)

### Standard Library Usage

- `platform` - OS detection
- `subprocess` - Command execution
- `pathlib` - Path operations
- `argparse` - Argument parsing
- `sys` - System operations
- `os` - OS interface
- `shutil` - File operations
- `datetime` - Timestamp management

## Cross-Platform Compatibility

### OS Detection

```python
if platform.system() == 'Linux':
    if 'microsoft' in platform.uname().release.lower():
        return 'wsl'
    return 'linux'
elif platform.system() == 'Darwin':
    return 'macos'
elif platform.system() == 'Windows':
    return 'windows'
```

### Shell Detection

```python
shell = os.environ.get('SHELL', '')
if 'bash' in shell:
    return 'bash'
elif 'zsh' in shell:
    return 'zsh'
# ... etc
```

### OS-Specific Commands

Commands can define OS-specific actions:

```yaml
cpu:
  action:
    linux: top -bn1 | grep "Cpu(s)"
    macos: top -l 1 | grep "CPU usage"
    windows: powershell "Get-Counter '...'"
```

The executor selects the appropriate action based on detected OS.

## Performance Considerations

### Startup Time

- Shell function definition: ~1ms
- Command lookup: ~5-10ms
- Total overhead: ~10-15ms per command

### Memory Usage

- Minimal footprint: ~5-10MB Python process
- YAML parsing: ~1-2MB for typical command files
- Total: ~7-12MB per execution

### Optimization Strategies

1. **Lazy Loading:** Commands loaded only when needed
2. **Caching:** Shell functions defined once at shell startup
3. **Minimal Dependencies:** Only PyYAML required
4. **Direct Execution:** No intermediate scripts

## Testing Strategy

### System Test

```bash
python3 run.py --check
```

Tests:
- OS detection
- Shell detection
- Command loading
- Parser functionality
- Executor functionality

### Integration Testing

```bash
python3 run.py go downloads
python3 run.py push "test"
```

### Manual Testing Checklist

- [ ] Installation on Linux
- [ ] Installation on macOS
- [ ] Installation on Windows
- [ ] Installation on WSL
- [ ] Bash compatibility
- [ ] Zsh compatibility
- [ ] PowerShell compatibility
- [ ] Command execution
- [ ] Parameter substitution
- [ ] OS-specific commands
- [ ] Backup/restore
- [ ] Editor functionality
- [ ] SSH management

## Future Enhancements

### Planned Features

1. **Command History:** Track command usage
2. **Auto-completion:** Tab completion for commands
3. **Command Templates:** Predefined command templates
4. **Plugin System:** Extensible plugin architecture
5. **Cloud Sync:** Sync commands across machines
6. **GUI Editor:** Graphical command editor

### Technical Improvements

1. **Performance:** Command caching
2. **Testing:** Automated test suite
3. **Documentation:** Auto-generated docs
4. **Packaging:** PyPI distribution
5. **CI/CD:** Automated builds and releases

## Contributing

### Code Style

- PEP 8 compliance
- Type hints where appropriate
- Comprehensive docstrings
- Meaningful variable names

### Adding Features

1. Create feature branch
2. Implement in appropriate module
3. Add tests
4. Update documentation
5. Submit pull request

### Module Guidelines

- Keep modules focused (single responsibility)
- Minimize dependencies between modules
- Maintain cross-platform compatibility
- Follow security best practices

## License

MIT License - See repository for full text

## Version History

- **1.0.0** (Initial Release)
  - Core functionality
  - Cross-platform support
  - Security features
  - Interactive editor
  - SSH management

---

For more information:
- [INSTALLATION.md](INSTALLATION.md) - Installation guide
- [USAGE.md](USAGE.md) - Usage guide
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Troubleshooting guide
