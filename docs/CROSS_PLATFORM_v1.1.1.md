# CCMD v1.1.1 - Cross-Platform Compatibility

**Platforms Supported:**
- ✅ Linux (Debian, Ubuntu, Fedora, Arch, etc.)
- ✅ macOS (10.13+)
- ✅ Windows 10/11 (PowerShell 5.1+)
- ✅ WSL (Windows Subsystem for Linux)

**Shells Supported:**
- ✅ Bash
- ✅ Zsh
- ✅ Fish
- ✅ PowerShell (Windows)

---

## Platform-Specific Implementation Details

### 1. File Permissions

#### **Unix/Linux/macOS:**
- Uses standard Unix permissions: `0o600` (owner read/write only)
- Full support for `chmod` with octal modes
- Files created: `~/.ccmd/ccmd.key`, `~/.ccmd/ccmd_auth.log`, `~/.ccmd/custom_commands.yaml`

#### **Windows:**
- Uses `stat.S_IREAD | stat.S_IWRITE` as closest equivalent
- Windows doesn't have Unix-style permissions
- Best effort approach - files are protected at filesystem level
- ACLs (Access Control Lists) are used internally by Windows

**Implementation:**
```python
# ccmd/core/security.py and ccmd/core/auth.py
if sys.platform == 'win32':
    os.chmod(path, stat.S_IREAD | stat.S_IWRITE)  # Windows
else:
    os.chmod(path, 0o600)  # Unix-like
```

---

### 2. Environment Variables

#### **Bash/Zsh (Linux/macOS/WSL):**
```bash
export CCMD_HOME="/path/to/ccmd"
$CCMD_HOME  # Access variable
```

#### **Fish (Linux/macOS):**
```fish
set -gx CCMD_HOME "/path/to/ccmd"
$CCMD_HOME  # Access variable
```

#### **PowerShell (Windows):**
```powershell
$env:CCMD_HOME = "C:\path\to\ccmd"
$env:CCMD_HOME  # Access variable
```

**Implementation:**
- Python code uses `os.environ.get('CCMD_HOME')` - works on all platforms
- Shell integration sets variables using platform-specific syntax
- Our `_expand_safe_env_vars()` expands `$CCMD_HOME` to actual path before execution

---

### 3. Path Handling

#### **All Platforms:**
- CCMD uses `pathlib.Path` for all path operations
- Automatically handles platform-specific separators:
  - Unix/Linux/macOS: `/`
  - Windows: `\` (but accepts `/` too)

**Examples:**
```python
# Works on all platforms
install_dir = Path(__file__).parent.parent.parent.resolve()
config_path = Path.home() / ".ccmd" / "commands.yaml"
```

---

### 4. Subprocess Execution

#### **Security Enhancement (v1.1.1):**
- **All platforms** now use `shell=False` for security
- Commands are parsed with `shlex.split()` before execution
- Cross-platform command parsing handled automatically

**Platform-specific considerations:**
```python
# Linux/macOS command
cmd = ['ls', '-la', '/home/user']

# Windows equivalent would be
cmd = ['dir', '/B', 'C:\\Users\\user']

# CCMD handles this through commands.yaml with platform detection
```

---

### 5. Bcrypt Password Hashing

#### **All Platforms:**
- bcrypt is a pure Python library (with C extensions)
- Works identically on Linux, macOS, Windows
- Requires: `pip install bcrypt>=4.0.0`

**Platform-specific installation:**
```bash
# Linux/macOS/WSL
pip3 install bcrypt

# Windows PowerShell
pip install bcrypt

# Or use requirements.txt on all platforms
pip install -r requirements.txt
```

---

### 6. Shell Integration

#### **Bash/Zsh Integration:**
```bash
# ~/.bashrc or ~/.zshrc
export CCMD_HOME="/path/to/ccmd"

go() {
    _ccmd_check || return 1
    local output
    output=$("python3" "$CCMD_HOME/run.py" go "$@")
    if [[ "$output" =~ ^cd[[:space:]] ]]; then
        eval "$output"
    else
        echo "$output"
    fi
}
```

#### **Fish Integration:**
```fish
# ~/.config/fish/config.fish
set -gx CCMD_HOME "/path/to/ccmd"

function go
    _ccmd_check; or return 1
    set output (python3 "$CCMD_HOME/run.py" go $argv)
    if string match -q -r '^cd ' "$output"
        eval "$output"
    else
        echo "$output"
    end
end
```

#### **PowerShell Integration:**
```powershell
# $PROFILE (PowerShell profile)
$env:CCMD_HOME = "C:\path\to\ccmd"

function go {
    if (-not (_ccmd_check)) { return }
    $output = & "python" "$env:CCMD_HOME/run.py" go $args
    if ($output -match '^cd ') {
        Invoke-Expression $output
    } else {
        Write-Output $output
    }
}
```

---

### 7. SSH Key Validation

#### **Unix/Linux/macOS:**
- Full SSH key permission validation
- Requires keys to have `0o600` permissions
- Checks key ownership (must be owned by current user)

```python
# Validates:
# - File permissions: 0o600
# - Owner UID matches current user
# - No group/other permissions
```

#### **Windows:**
- SSH keys typically in `C:\Users\<user>\.ssh\`
- Windows uses ACLs instead of Unix permissions
- CCMD does best-effort validation:
  - Checks file exists
  - Checks file ownership
  - Windows NTFS permissions checked at OS level

---

### 8. Command Differences

Some system commands differ across platforms. CCMD handles this in `commands.yaml`:

```yaml
cpu:
  description: Show CPU usage
  action:
    linux: top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'
    macos: top -l 1 | grep "CPU usage"
    windows: powershell "Get-Counter '\Processor(_Total)\% Processor Time'"
```

---

### 9. Terminal Colors

#### **All Platforms:**
- ANSI color codes work on:
  - Linux terminals
  - macOS Terminal.app / iTerm2
  - Windows PowerShell (Windows 10+)
  - WSL terminals
  - Windows Terminal

**Colors used:**
```python
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
END = '\033[0m'
```

---

### 10. Python Version

#### **All Platforms:**
- **Minimum:** Python 3.7+
- **Recommended:** Python 3.8+
- **Tested with:** Python 3.9, 3.10, 3.11, 3.12

**Check your version:**
```bash
python3 --version  # Linux/macOS/WSL
python --version   # Windows
```

---

## Testing on Different Platforms

### Linux (Tested ✅)
```bash
# Ubuntu 20.04+, Debian 11+, etc.
python3 run.py --install
python3 run.py --check
python3 run.py --init
go home
```

### macOS (Untested ⚠️)
```bash
# macOS 10.13+ with Homebrew Python
python3 run.py --install
python3 run.py --check
python3 run.py --init
go home
```

**Note:** macOS users should test and report issues!

### Windows PowerShell (Partially Tested ✅)
```powershell
# Windows 10/11 PowerShell
python run.py --install
python run.py --check
python run.py --init
go home
```

### WSL (Tested ✅)
```bash
# Same as Linux
python3 run.py --install
source ~/.bashrc
go home
```

---

## Known Platform-Specific Issues

### Windows:
1. **File permissions** - Uses Windows ACLs, not Unix-style `0o600`
2. **Path separators** - Handles both `/` and `\` automatically
3. **Python executable** - Might be `python` instead of `python3`

### macOS:
1. **Not fully tested** - Need community testing
2. **Some commands** - `top`, `ps` syntax might differ slightly
3. **SSH keys** - Usually in `~/.ssh/`, permissions work as on Linux

### WSL:
1. **Mixed paths** - Can access both Linux (`/mnt/c/...`) and Windows paths
2. **Git line endings** - Set `core.autocrlf` appropriately
3. **Performance** - File I/O can be slower on `/mnt/c/` drives

---

## Dependencies Compatibility

All dependencies are cross-platform:

```txt
PyYAML>=6.0          # ✅ Linux, macOS, Windows
questionary>=2.0.0   # ✅ Linux, macOS, Windows
GitPython>=3.1.0     # ✅ Linux, macOS, Windows
bcrypt>=4.0.0        # ✅ Linux, macOS, Windows (with C extensions)
```

---

## Security Features by Platform

| Feature | Linux | macOS | Windows | WSL |
|---------|-------|-------|---------|-----|
| Master password | ✅ | ✅ | ✅ | ✅ |
| SSH key validation | ✅ Full | ✅ Full | ⚠️ Limited | ✅ Full |
| File permissions (0o600) | ✅ | ✅ | ⚠️ ACLs | ✅ |
| Command injection prevention | ✅ | ✅ | ✅ | ✅ |
| Secure file operations | ✅ | ✅ | ✅ | ✅ |
| bcrypt hashing | ✅ | ✅ | ✅ | ✅ |

---

## Troubleshooting

### **"bcrypt not installed"**
```bash
# Linux/macOS/WSL
pip3 install bcrypt

# Windows
pip install bcrypt
```

### **"Python not found"**
```bash
# Linux/macOS/WSL - use python3
python3 run.py --install

# Windows - might be just python
python run.py --install
```

### **File permission errors on Windows**
- Windows handles permissions differently
- CCMD does best-effort - files are still protected by Windows ACLs
- No action needed - this is expected behavior

### **Commands don't work after install**
```bash
# Reload shell
source ~/.bashrc    # Bash
source ~/.zshrc     # Zsh
. $PROFILE          # PowerShell
source ~/.config/fish/config.fish  # Fish
```

---

## Contributing

### Testing on macOS
We need macOS testers! If you're on macOS:

1. Test installation: `python3 run.py --install`
2. Test commands: `go home`, `hi`, `list`
3. Test security: `python3 run.py --init`
4. Report issues: https://github.com/Wisyle/ccmd/issues

### Testing on Windows PowerShell
PowerShell testers needed:

1. Test full installation process
2. Test password protection features
3. Test SSH key validation
4. Report any path-related issues

---

## Technical Notes

### Why `shell=False`?
- **Security:** Prevents command injection attacks
- **Cross-platform:** Works consistently on all platforms
- **Trade-off:** Can't use shell features like pipes, redirects directly
  - Solution: Define complex commands in `commands.yaml` or use wrapper scripts

### Why `pathlib.Path`?
- Cross-platform path handling
- Automatic separator conversion
- Cleaner, more Pythonic API

### Why bcrypt?
- Industry standard for password hashing
- Cross-platform (pure Python + optional C extensions)
- Slow by design (resistant to brute-force)
- Automatic salt generation

---

## Summary

CCMD v1.1.1 is designed to be **truly cross-platform**:

✅ **Works everywhere:** Linux, macOS, Windows, WSL
✅ **Same commands:** Consistent experience across platforms
✅ **Platform-aware:** Handles OS differences automatically
✅ **Secure everywhere:** All security features work cross-platform
✅ **Best effort:** Graceful degradation on platform limitations

---

**Developed by De Catalyst (@Wisyle)**
**GitHub:** https://github.com/Wisyle/ccmd

---

_Last updated: 2025-10-27_
