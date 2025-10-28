# CCMD v1.1.2 — Command Chaining & Security Hardening Release

**Release Date:** October 28, 2025

---

## 🔗 Command Chaining & Composability

The most requested feature is here! v1.1.2 introduces **command chaining** with the `>>>` operator, allowing you to combine multiple commands into powerful workflows.

### What You Can Do Now

**Chain CCMD commands together:**
```bash
go downloads >>> ls >>> echo "Files listed!"
```

**Mix CCMD and shell commands:**
```bash
go projects >>> pwd >>> echo "Current project directory"
```

**Create powerful custom commands:**
```bash
ccmd add
name: devsetup
command: go projects >>> ls >>> echo "Ready to code!"
```

**Multi-step workflows:**
```bash
go home >>> go downloads >>> ls
```

### How It Works

- **`>>>` separator** — Clear, intuitive chaining operator
- **Command composability** — CCMD commands can call other CCMD commands
- **Smart directory handling** — Directory changes persist through the chain
- **Error handling** — Chain stops on first failure
- **Recursion guard** — Maximum depth of 10 prevents infinite loops
- **Step feedback** — See each step execute in real-time

### Example Use Cases

**Developer workflow:**
```bash
ccmd add
name: start-work
command: go projects >>> go myapp >>> ls
```

**System admin:**
```bash
ccmd add
name: check-system
command: cpu >>> mem >>> proc
```

**Quick navigation:**
```bash
go downloads >>> ls >>> echo "Done!"
```

---

## 🛡️ Security Hardening

v1.1.2 fixes **4 critical security vulnerabilities** discovered in v1.1.1:

### 1. bcrypt Bypass Vulnerability (FIXED)
**Issue:** If bcrypt wasn't installed, authentication was bypassed entirely.

**Fix:** Added PBKDF2-HMAC-SHA256 fallback with 100,000 iterations (OWASP standard)
- Industry-standard key derivation function
- Constant-time comparison prevents timing attacks
- Auto-detects hash format (bcrypt vs PBKDF2)
- Never bypasses authentication

### 2. Custom Command Type Abuse (FIXED)
**Issue:** Users could mark custom commands as `type: system` to get `shell=True` execution.

**Fix:** Force all custom commands to `type='custom'`
- Registry automatically overrides type for custom commands
- Prevents bypass of safe execution path
- Custom commands always use `shell=False`

### 3. Incomplete Sensitive Pattern Detection (FIXED)
**Issue:** Only 17 patterns detected, missing many credential types.

**Fix:** Expanded to 40+ sensitive patterns
- SSH options (`-oIdentityFile`, `-oProxyCommand`)
- Cloud credentials (AWS, Azure, GCP)
- Database environment variables (PGPASSWORD, MYSQL_PWD)
- API keys and tokens (20+ character patterns)
- Certificate paths and passwords
- Container registry credentials

### 4. Command Chaining Bypass (FIXED)
**Issue:** Only 6 dangerous patterns detected, missing command chaining operators.

**Fix:** Expanded to 35+ dangerous patterns
- Shell operators: `&&`, `||`, `;`
- Command substitution: backticks, `$()`
- Pipes to interpreters: `| bash`, `| sh`, `| python`
- Context-aware validation (allows operators in custom commands since they use `shell=False`)

---

## 💀 Process Management Commands

Two new commands for process control:

### `kap` — Kill All Processes
Kills ALL processes owned by the current user.

**Features:**
- Password protection (requires master password)
- Red warning confirmation
- Must type "yes" to confirm
- Safe abort with Ctrl+C

**Usage:**
```bash
kap
```

**Output:**
```
⚠️  WARNING: DANGEROUS OPERATION
This will kill ALL processes owned by you!
This may cause data loss and unsaved work.

Type 'yes' to confirm:
```

### `kp` — Kill Process by Name
Kills a specific process by name.

**Usage:**
```bash
kp bash
kp python3
kp node
```

**Cross-platform:**
- Linux/macOS: Uses `pkill -9`
- Windows: Uses `taskkill /F /IM`

---

## 🔧 Technical Improvements

### Context-Aware Validation

Commands are now validated based on execution context:

**System commands (shell=True):**
- Strict validation, blocks all dangerous patterns
- Used for: `cpu`, `mem`, `proc`, built-in system commands

**Custom commands (shell=False):**
- Relaxed validation, allows shell operators
- Operators are harmless with `shell=False` (treated as literal text)
- Used for: All user-defined custom commands

This prevents false positives while maintaining security.

### Enhanced Security Patterns

**Dangerous patterns now detected (35+):**
- Fork bombs: `:(){ :|:& };:`
- Recursive deletion: `rm -rf /`
- Direct disk writes: `> /dev/sda`, `dd of=/dev/`
- Piped execution: `curl | bash`, `wget | sh`
- Command chaining: `&&`, `||`, `;`
- Command substitution: backticks, `$()`
- System writes: `> /etc/`, `> /boot/`

**Sensitive patterns now detected (40+):**
- SSH: `-i key.pem`, `-oIdentityFile`, `-oProxyCommand`
- AWS: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Azure: `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`
- GCP: `GOOGLE_APPLICATION_CREDENTIALS`
- Databases: `PGPASSWORD`, `MYSQL_PWD`, `REDIS_PASSWORD`
- API keys: 20+ character tokens
- Certificates: `.pem`, `.key`, `.crt` with passwords

### Command Chaining Implementation

**Architecture:**
- `execute_chained_commands()` in `executor.py`
- `has_command()` in `registry.py` for command lookup
- `_execute_ccmd_command()` for programmatic execution
- Recursion depth guard (max 10 levels)
- Directory state management (save/restore)
- Step-by-step execution with feedback

**Special Handling:**
- Navigation commands (`go`) actually change directory in chains
- Path expansion (`~` → home directory, `$VAR` → value)
- Error propagation (stops on first failure)
- Output accumulation (all stdout/stderr collected)

---

## 📋 Complete Changelog

### Added
- ✅ `>>>` command chaining operator
- ✅ Command composability (CCMD commands can call other CCMD commands)
- ✅ `kap` command (kill all processes with password protection)
- ✅ `kp` command (kill process by name)
- ✅ PBKDF2-HMAC-SHA256 fallback for password hashing
- ✅ Context-aware command validation
- ✅ Recursion depth guard for chaining
- ✅ 23+ new dangerous pattern detections
- ✅ 23+ new sensitive pattern detections

### Fixed
- 🔒 **SECURITY:** bcrypt bypass vulnerability
- 🔒 **SECURITY:** Custom command type abuse
- 🔒 **SECURITY:** Incomplete sensitive pattern detection
- 🔒 **SECURITY:** Command chaining bypass
- 🐛 Action formatting bug in command execution
- 🐛 Path expansion for `~` and environment variables
- 🐛 Navigation command handling in chains

### Changed
- 📝 Custom commands forced to `type='custom'` for safety
- 📝 Validation now context-aware (system vs custom commands)
- 📝 Expanded security pattern detection from 23 to 75+ patterns

### Security
- 🛡️ No authentication bypass possible
- 🛡️ All custom commands use `shell=False`
- 🛡️ Comprehensive pattern detection
- 🛡️ Type enforcement prevents privilege escalation

---

## 🔄 Breaking Changes

**None.** This release is **fully backward compatible** with v1.1.1 and v1.1.0.

- Existing custom commands work without modification
- Shell integration unchanged
- Configuration format unchanged
- Master password system unchanged

---

## 📦 Upgrade Instructions

### From v1.1.1 or v1.1.0

**Option 1: Git Repository**
```bash
cd /path/to/ccmd
git pull origin ccmd
python3 run.py --install
```

**Option 2: GitHub Release**
```bash
# Download release from GitHub
cd ~/Downloads
tar -xzf ccmd-v1.1.2.tar.gz
cd ccmd
python3 run.py --install
```

**Option 3: Direct Download**
```bash
curl -L https://github.com/Wisyle/ccmd/archive/refs/tags/v1.1.2.tar.gz -o ccmd.tar.gz
tar -xzf ccmd.tar.gz
cd ccmd-1.1.2
python3 run.py --install
```

### Your Data is Safe
✅ Custom commands preserved
✅ Master password unchanged
✅ Shell config backed up automatically
✅ Rollback available with `restore` command

---

## 🧪 Testing

This release has been thoroughly tested with:

**Test Coverage:**
- ✅ 8 automated chaining tests (all passed)
- ✅ 3 real-world scenario tests (all passed)
- ✅ Security validation tests (all passed)
- ✅ Cross-platform compatibility tests

**Platforms:**
- ✅ Linux (Ubuntu 22.04 on WSL)
- ✅ Windows PowerShell (Windows 10/11)
- ✅ WSL (Windows Subsystem for Linux)
- ⚠️ macOS (code supports it, community testing needed)

**Shells:**
- ✅ Bash
- ✅ Zsh
- ✅ PowerShell
- ⚠️ Fish (needs additional testing)

---

## 🐛 Known Issues

**None reported.** All known issues from v1.1.1 have been resolved.

If you encounter any issues, please report them at:
https://github.com/Wisyle/ccmd/issues

---

## 🚀 What's Next?

**v1.2.0 Roadmap:**
- 🔑 **Recovery Key System** — Single-use backup codes for password recovery
- 🔐 **Command Encryption** — Encrypt sensitive custom commands at rest
- 🍎 **macOS Testing** — Comprehensive macOS compatibility testing
- 🐟 **Fish Shell** — Full Fish shell support and testing
- ⚡ **Performance** — Optimizations for very large repositories
- 🔌 **Plugin System** — Community extensions and plugins

---

## 📚 Documentation

**Updated for v1.1.2:**
- ✅ [README.md](README.md) — Updated with v1.1.2 features
- ✅ [SECURITY_CHANGELOG.md](SECURITY_CHANGELOG_v1.1.1.md) — Security fixes documented
- ✅ This release note

**Still Relevant:**
- 📖 [Security Disclaimer](SECURITY_DISCLAIMER.md) — Important security information
- 📖 [Features](FEATURES.md) — Complete feature list
- 📖 [Installation Guide](INSTALLATION.md) — Step-by-step installation
- 📖 [Usage Guide](USAGE.md) — Complete command reference
- 📖 [Configuration Guide](CONFIGURATION.md) — Customize commands
- 📖 [Troubleshooting](TROUBLESHOOTING.md) — Common issues

---

## 🙏 Credits

**Developed by:**
**De Catalyst (@Wisyle)**

📧 Robert5560newton@gmail.com
🐦 [@iamdecatalyst](https://x.com/iamdecatalyst)
💻 [github.com/Wisyle](https://github.com/Wisyle)

**Special Thanks:**
- Security researchers for vulnerability reports
- Beta testers for v1.1.2 testing
- Community for feature requests
- Python community for security best practices

---

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.

---

## ⚠️ Security Notice

**Found a security vulnerability?**

Please report it privately to: Robert5560newton@gmail.com

Do NOT open a public GitHub issue for security vulnerabilities.

We'll respond within 48 hours and work with you to resolve the issue.

---

**Full Changelog:** https://github.com/Wisyle/ccmd/compare/v1.1.1...v1.1.2
**Download:** https://github.com/Wisyle/ccmd/releases/tag/v1.1.2

**Thank you for using CCMD! Use carefully, cautiously, and responsibly.**
