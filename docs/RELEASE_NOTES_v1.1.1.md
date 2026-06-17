# CCMD v1.1.1 Release Notes

**Release Date:** October 27, 2025

## 🔐 Security-Enhanced Release

CCMD v1.1.1 is a **major security update** that transforms CCMD into a production-ready command manager with enterprise-level security features. This release focuses on protecting users while maintaining the simplicity and power that makes CCMD great.

---

## 🆕 New Features

### 🔒 Master Password System

CCMD now includes a **bcrypt-based master password system** for protecting sensitive commands:

- **`init`** - Initialize your master password (one-time setup)
- **`change-password`** - Change your master password securely
- **`reset-password`** - Reset password if forgotten (deletes stored password)
- **5-minute authentication cache** - Enter password once, valid for 5 minutes per session
- **Audit logging** - All authentication attempts logged to `~/.ccmd/ccmd_auth.log`
- **Password-protected commands** - Mark any command as requiring authentication

**Usage:**
```bash
# First time setup
ccmd init

# Now protected commands will prompt for password
ccmd sudo apt update

# Add password protection to custom commands
ccmd add  # Choose "Yes" when asked about password protection
```

### 🛡️ Command Injection Prevention

Automatic detection and blocking of dangerous command patterns:

- **Fork bombs** - `:(){ :|:& };:`
- **Recursive deletion** - `rm -rf /`
- **Direct disk writes** - `> /dev/sda`
- **Pipe to shell** - `curl malicious.com | bash`
- **Null byte injection** - Commands with `\0` characters
- **Path traversal** - `../../../etc/passwd`

Commands are validated **before execution**, preventing accidental system damage.

### 🔐 SSH Key Validation

Automatic security checks for SSH keys:

- Verifies **0600 permissions** (owner read/write only)
- Checks **file ownership** (must be owned by current user)
- Validates **key file exists** before attempting connection
- **Clear error messages** if validation fails

### 🔍 Sensitive Command Auto-Detection

CCMD automatically detects sensitive commands and requires password authentication:

- Commands with `sudo`
- Commands with `ssh -i` (SSH key usage)
- Commands with `sshpass`
- Commands with AWS credentials (`AWS_SECRET_ACCESS_KEY`)
- Commands with database credentials
- Commands with API keys or tokens

No manual configuration needed - protection is automatic!

### 🔐 Secure Subprocess Execution

Enhanced security in command execution:

- **`shell=False` by default** - Prevents command injection via shell metacharacters
- **Selective shell usage** - Only system commands use `shell=True` when necessary
- **Safe argument parsing** - Uses `shlex.split()` for proper quote handling
- **Timeout protection** - Commands have 30-second default timeout

### 📁 Atomic File Operations

Safe file operations prevent data corruption:

- **Write to temp file first** - Uses `tempfile.mkstemp()`
- **Atomic move** - Uses `os.replace()` for POSIX atomicity
- **Secure permissions** - Files created with `0o600` (owner-only access)
- **Automatic cleanup** - Temp files removed even on failure

### 🎯 Intelligent Auto-Locator

CCMD now intelligently finds its installation directory:

- **No more path issues** - Works regardless of where CCMD is installed
- **Multi-method detection**:
  1. Checks `CCMD_HOME` environment variable
  2. Calculates from current file location
  3. Validates `run.py` exists
- **Cross-platform paths** - Handles Windows/Unix path separators automatically
- **Perfect for global releases** - Users won't encounter path errors

---

## 🐛 Bug Fixes

### Windows/PowerShell Fixes

✅ **Fixed: PowerShell UTF-8 encoding issues**
- Unicode characters (✓, ⚠, █) now display correctly
- Reconfigured stdout/stderr with UTF-8 encoding
- Added error handling with 'replace' mode for unsupported characters

✅ **Fixed: Internal commands trying to spawn Python twice**
- Commands like `init`, `debug`, `version` now call handlers directly
- Eliminated double-process spawning that caused path issues
- Improved performance by avoiding unnecessary subprocess calls

✅ **Fixed: `python3` command not found on Windows**
- Changed all internal commands to use `python` instead of `python3`
- Works on both Windows (`python`) and Unix (`python`/`python3`)
- Cross-platform compatibility improved

✅ **Fixed: Mangled paths on Windows**
- Environment variable expansion now handles Windows paths correctly
- Path separators normalized for the platform
- Auto-locator prevents path-related errors

### Git Workflow Fixes

✅ **Fixed: Push command hanging on large repositories**
- Replaced slow GitPython calls with fast `git status --porcelain`
- Single subprocess call instead of multiple API calls
- Added 120-second timeout for safety
- Real-time progress display for user feedback

✅ **Fixed: Staged files not shown in push command**
- Push command now properly detects and displays staged files
- Skip file selection when all changes are already staged
- Handle mixed staged/unstaged files correctly
- Show clear status for each file type

✅ **Fixed: System command detection bug**
- Parser now uses regex `\{\w+\}` to match Python placeholders
- Distinguished OS-specific dicts from subcommand dicts
- Commands like `cpu`, `mem`, `proc` now work correctly

---

## 🔧 Technical Changes

### New Modules

- **`ccmd/core/security.py`** (~272 lines)
  - `CommandSecurityValidator` - Validates commands for dangerous patterns
  - `SecureSubprocess` - Safe subprocess execution without shell=True
  - `SecureFileOperations` - Atomic file writes with secure permissions
  - `VersionSecurity` - Dependency version validation

- **`ccmd/core/auth.py`** (~502 lines)
  - `initialize_password_interactive()` - Set up master password
  - `verify_password_interactive()` - Verify with caching
  - `change_password_interactive()` - Change password securely
  - `reset_password_interactive()` - Reset forgotten password
  - `detect_sensitive_command()` - Auto-detect sensitive patterns
  - `check_key_file_permissions()` - Validate SSH key security

### Modified Modules

- **`ccmd/core/executor.py`**
  - Added `execute_with_security()` method
  - Added `_get_ccmd_home()` auto-locator
  - Enhanced `_expand_safe_env_vars()` with path normalization
  - Improved KeyboardInterrupt handling

- **`ccmd/core/parser.py`**
  - Fixed `_requires_parameters()` to use regex matching
  - Better distinction between OS dicts and subcommand dicts

- **`ccmd/cli/main.py`**
  - Added UTF-8 encoding setup for Windows
  - Added handlers: `handle_init()`, `handle_change_password()`, `handle_reset_password()`
  - Updated `handle_command()` to route internal commands to handlers
  - Prevented double-spawning of Python processes

- **`ccmd/cli/interactive.py`**
  - Added password protection toggle in list editor (`p` option)
  - Added password option when adding custom commands
  - Shows 🔒 badge for password-protected commands
  - Optimized `get_git_status()` for large repositories
  - Fixed staged files handling in push workflow

### New Commands

- `init` - Initialize master password
- `debug` - Show system diagnostics
- `sudo` - Run command as superuser (password protected)
- `change-password` - Change master password
- `reset-password` - Reset master password

### Updated Dependencies

```
bcrypt>=4.0.0  # Password hashing for master password system
```

---

## 📋 Platform Testing

This release has been thoroughly tested on:

- ✅ **Linux** (Ubuntu on WSL)
- ✅ **WSL** (Windows Subsystem for Linux)
- ✅ **Windows PowerShell** (Windows 10/11)

**macOS:** Code supports macOS but remains untested. Community testing needed!

---

## 🔄 Breaking Changes

**None.** This release is **fully backward compatible** with v1.1.0 configurations.

Existing custom commands and configurations will work without modification.

---

## 📦 Upgrade Instructions

### Method 1: From Git Repository

```bash
cd /path/to/ccmd
git pull origin ccmd
python3 run.py --install  # Or: python run.py --install on Windows
```

### Method 2: From GitHub Release

1. Download the latest release from [github.com/Wisyle/ccmd/releases/latest](https://github.com/Wisyle/ccmd/releases/latest)
2. Extract to your preferred location
3. Run the installer:
   - **Linux/macOS/WSL:** `bash setup.sh`
   - **Windows PowerShell:** `.\setup.ps1`

**Your data is safe:**
- Custom commands in `~/.ccmd/custom_commands.yaml` are preserved
- Shell configuration backups are maintained
- No data loss during upgrade

---

## 🛡️ Security Considerations

### ⚠️ Important: Use Responsibly

CCMD is a powerful tool that sits as an **interceptor between your shell and you**. Like electricity, cars, or any powerful tool - **it can be dangerous if used wrongly**.

**Please read the [SECURITY_DISCLAIMER.md](SECURITY_DISCLAIMER.md) before using CCMD.**

### Password Storage

- Passwords are hashed with **bcrypt** (industry-standard)
- Salt is generated automatically per password
- Stored in `~/.ccmd/ccmd.key` with **0600 permissions** (owner-only access)
- No plaintext passwords stored anywhere

### Audit Logging

All authentication attempts are logged to `~/.ccmd/ccmd_auth.log`:
```
2025-10-27 14:30:15 | user: decatalyst | success: True | command: sudo
2025-10-27 14:35:20 | user: decatalyst | success: False | command: ssh
```

Monitor this file for unauthorized access attempts.

---

## 📚 Documentation

Updated documentation includes:

- **[SECURITY_DISCLAIMER.md](SECURITY_DISCLAIMER.md)** - Important security information and responsible use guidelines
- **[README.md](README.md)** - Updated with v1.1.1 features and security info
- **[FEATURES.md](FEATURES.md)** - Complete feature list including security features
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Security-related troubleshooting
- **[CONFIGURATION.md](CONFIGURATION.md)** - Password protection configuration

---

## 🐛 Known Issues

- **macOS compatibility** - Untested, community feedback needed
- **Fish shell** - Needs additional testing with security features
- **Large monorepos** - Push command may still be slow (but much improved)

---

## 🚀 What's Next?

**v1.1.2 Roadmap** (Next Release):

- **Recovery Key System** - Backup key for password recovery without reset
- **Command Encryption** - Encrypt sensitive custom commands at rest
- Additional security hardening based on community feedback

**v1.2.0 Roadmap** (Future):

- macOS testing and compatibility fixes
- Fish shell comprehensive testing
- Additional security features (2FA, hardware key support)
- Performance optimizations for very large repositories
- Plugin system for community extensions
- GUI configuration tool

---

## 🤝 Contributing

Found a bug? Have a feature request? **We need your help!**

1. **Report bugs** via [GitHub Issues](https://github.com/Wisyle/ccmd/issues)
2. **Test on macOS** and report your experience
3. **Submit pull requests** for bug fixes or features
4. **Share your feedback** on social media

---

## 👏 Credits

**Developed by De Catalyst (Wisyle)**

- **GitHub:** [@Wisyle](https://github.com/Wisyle)
- **Email:** Robert5560newton@gmail.com
- **Twitter/X:** [@iamdecatalyst](https://x.com/iamdecatalyst)

**Special Thanks:**
- The Python community for bcrypt and security best practices
- GitPython contributors for git integration
- All beta testers who provided feedback

---

## 📜 License

CCMD is open-source software. See [LICENSE](LICENSE) for details.

---

## ⚠️ Final Note

**This is the starter phase of CCMD.** While we've done our best to cover all security aspects, some features might not work perfectly across all platforms.

**Use carefully, cautiously, and responsibly.**

If you encounter any issues or have security concerns, please report them immediately via [GitHub Issues](https://github.com/Wisyle/ccmd/issues).

---

**Full Changelog:** https://github.com/Wisyle/ccmd/compare/v1.1.0...v1.1.1

**Download:** https://github.com/Wisyle/ccmd/releases/tag/v1.1.1
