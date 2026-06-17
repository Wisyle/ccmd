# CCMD v1.1.1 Security Update - Critical

**Release Date:** 2025-10-27
**Severity:** CRITICAL - All users must upgrade immediately
**Developer:** De Catalyst (@Wisyle)

---

## Overview

**v1.1.1** is a mandatory security update that addresses multiple critical vulnerabilities discovered in CCMD v1.1.0 and earlier. This release introduces comprehensive security enhancements while maintaining full functionality.

**⚠️ IMPORTANT:** Versions prior to v1.1.1 contain security vulnerabilities and are no longer supported.

---

## Critical Security Fixes

### 1. Command Injection Prevention

**Vulnerability:** Previous versions used `subprocess.run()` with `shell=True`, allowing potential command injection attacks through user-controlled strings.

**Fix:**
- Replaced all `shell=True` calls with `shell=False`
- Implemented safe command parsing using `shlex.split()`
- Added command validation before execution
- Created `SecureSubprocess` utility class

**Impact:** Eliminates risk of arbitrary command execution via injection

**Files Modified:**
- `ccmd/core/executor.py`
- `ccmd/core/security.py` (NEW)

---

### 2. Password Protection for Sensitive Commands

**Enhancement:** NEW in v1.1.1 - Master password protection system

**Features:**
- Master password using bcrypt hashing (industry standard)
- Auto-detection of sensitive commands (SSH, sudo, credentials)
- Manual `require_password` flag support in commands.yaml
- SSH key permission validation (must be 0600)
- Authentication caching (5 minutes per session)
- Audit logging of authentication attempts

**Commands Auto-Protected:**
- SSH with embedded keys (`ssh -i`)
- SCP/SFTP with keys
- sshpass and password utilities
- sudo/reboot/shutdown commands
- Cloud credential operations (AWS, etc.)
- Database commands with passwords

**Usage:**
```bash
# Initialize master password (one-time setup)
python3 run.py --init

# Protected commands will prompt for password
ssh -i ~/.ssh/mykey user@server  # Will require master password
```

**Files Added:**
- `ccmd/core/auth.py` (NEW)

---

### 3. Secure File Operations

**Vulnerability:** Configuration files created with default permissions, potentially exposing sensitive data.

**Fix:**
- Atomic file writes using temporary files + `os.replace()`
- Secure permissions (0o600 - owner read/write only) on all config files
- Created `SecureFileOperations` utility class

**Protected Files:**
- `commands.yaml`
- `~/.ccmd/custom_commands.yaml`
- `~/.ccmd/ccmd.key` (master password hash)
- `~/.ccmd/ccmd_auth.log` (audit log)

**Files Modified:**
- `ccmd/core/registry.py`
- `ccmd/core/security.py` (NEW)

---

### 4. Enhanced Input Validation

**Vulnerability:** Insufficient input sanitization could allow injection of special characters.

**Fix:**
- Improved `sanitize_input()` using centralized security module
- Added `shlex.quote()` for shell argument escaping
- Control character filtering
- Dangerous pattern blocking (fork bombs, disk wiping, etc.)

**Blocked Patterns:**
- `rm -rf` on system directories
- Fork bombs (`:(){:|:&};:`)
- Disk wiping commands (`dd if=/dev/zero`)
- Filesystem formatting (`mkfs.*`)
- Device file writes

**Files Modified:**
- `ccmd/core/executor.py`
- `ccmd/core/security.py` (NEW)

---

### 5. YAML Loading (Already Secure)

**Status:** ✅ Verified secure in audit

- Confirmed all YAML operations use `yaml.safe_load()`
- No vulnerable `yaml.load()` calls found
- Prevents arbitrary code execution via malicious YAML

---

## New Dependencies

### Required:
- **bcrypt >= 4.0.0** - Password hashing for master password system

Install with:
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install bcrypt>=4.0.0
```

---

## Upgrading from v1.1.0 or Earlier

### Step 1: Update CCMD

**If installed via Git:**
```bash
cd /path/to/ccmd
git pull origin ccmd
pip install -r requirements.txt
python3 run.py --install
```

**If installed via ZIP:**
1. Download v1.1.1: https://github.com/Wisyle/ccmd/releases/latest
2. Extract and replace your ccmd directory
3. Run: `pip install -r requirements.txt`
4. Run: `python3 run.py --install`

### Step 2: Initialize Security (Recommended)

Set up master password protection:
```bash
python3 run.py --init
```

This is optional but HIGHLY RECOMMENDED if you use:
- SSH commands
- Sudo/system commands
- Any commands with credentials

### Step 3: Reload Shell

```bash
source ~/.bashrc  # or ~/.zshrc, or restart terminal
```

---

## Security Features Summary

| Feature | v1.1.0 | v1.1.1 |
|---------|--------|--------|
| Subprocess shell=False | ❌ | ✅ |
| Command injection protection | ⚠️ Partial | ✅ Full |
| Master password system | ❌ | ✅ NEW |
| SSH key validation | ❌ | ✅ NEW |
| Secure file permissions | ❌ | ✅ 0o600 |
| Atomic file writes | ❌ | ✅ |
| Enhanced input sanitization | ⚠️ Basic | ✅ Advanced |
| Sensitive command detection | ❌ | ✅ NEW |
| Authentication audit logging | ❌ | ✅ NEW |

---

## Breaking Changes

**None.** v1.1.1 is fully backward compatible with v1.1.0 commands.yaml files.

**Optional changes:**
- Add `require_password: true` to sensitive commands in your custom_commands.yaml
- Enable master password with `--init`

---

## New Commands & Flags

### `python3 run.py --init`
Initialize master password for sensitive command protection.

### Enhanced `--debug`
Now includes security status (password set, bcrypt availability, auth cache).

---

## Security Best Practices

### 1. Use SSH Config Instead of Embedded Keys

**Bad:**
```yaml
deploy:
  command: "ssh -i ~/.ssh/prod_key user@server"
```

**Better:**
```yaml
deploy:
  command: "ssh prod-server"  # Uses ~/.ssh/config
  require_password: true
```

Then in `~/.ssh/config`:
```
Host prod-server
  HostName 192.168.1.100
  User deploy
  IdentityFile ~/.ssh/prod_key
```

### 2. Mark Sensitive Commands

Add `require_password: true` to any command that:
- Accesses production servers
- Uses sudo/admin privileges
- Contains credentials
- Performs destructive operations

Example in `~/.ccmd/custom_commands.yaml`:
```yaml
commands:
  deploy-prod:
    description: "Deploy to production server"
    command: "ssh prod-server './deploy.sh'"
    type: custom
    require_password: true  # ← Add this
```

### 3. Secure Your SSH Keys

Ensure your SSH keys have correct permissions:
```bash
chmod 600 ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_ed25519
```

CCMD v1.1.1 will refuse to run commands with improperly secured keys.

---

## Audit & Compliance

### Authentication Logs

All password authentication attempts are logged to:
```
~/.ccmd/ccmd_auth.log
```

Log format:
```
2025-10-27 14:23:45  username  OK
2025-10-27 14:25:12  username  FAIL
```

Logs are created with 0o600 permissions (owner read/write only).

### Version Enforcement

Future CCMD updates may enforce minimum version requirements for security.

---

## Technical Details

### Password Hashing
- Algorithm: bcrypt with salt
- Rounds: 12 (bcrypt default)
- Storage: `~/.ccmd/ccmd.key` (0o600 permissions)

### Authentication Cache
- Duration: 5 minutes per shell session
- Scope: Per-process (separate shells require separate auth)
- Clear cache: Restart shell or run `python3 run.py --init`

### Sensitive Pattern Detection
Automatically detects:
- SSH with `-i` flag
- `sshpass` usage
- AWS/cloud credentials in exports
- MySQL/PostgreSQL with `-p`
- Docker login
- sudo/reboot/shutdown

---

## Credits

Security audit and fixes by De Catalyst (@Wisyle) with community feedback.

Special thanks to security researchers who responsibly disclosed vulnerabilities.

---

## Support & Reporting

### Security Issues
Email: Robert5560newton@gmail.com
Subject: [CCMD Security] Brief description

**Do not open public GitHub issues for security vulnerabilities.**

### General Support
- GitHub Issues: https://github.com/Wisyle/ccmd/issues
- Twitter: [@iamdecatalyst](https://x.com/iamdecatalyst)

---

## Changelog

**v1.1.1 (2025-10-27) - Security Update**
- **[CRITICAL]** Fixed command injection via subprocess shell=True
- **[NEW]** Master password system with bcrypt
- **[NEW]** Sensitive command auto-detection
- **[NEW]** SSH key permission validation
- **[SECURITY]** Atomic file writes with 0o600 permissions
- **[SECURITY]** Enhanced input sanitization
- **[SECURITY]** Authentication audit logging
- **[ENHANCEMENT]** Improved error messages
- **[DEPENDENCY]** Added bcrypt>=4.0.0

**v1.1.0 (Previous)**
- Custom commands
- Interactive push
- Reload command

---

## License

MIT License - See LICENSE file

---

**Thank you for using CCMD responsibly. Stay secure! 🔒**

---

_Last updated: 2025-10-27_
