# CCMD v1.1.3 Release Notes

**Release Date:** October 29, 2025
**Type:** Bug Fix Release
**Status:** Production Ready

---

## Overview

Version 1.1.3 is a critical bug fix release that resolves issues with command chaining directory persistence, interactive command timeouts, and installation warnings. **All users on v1.1.2 should upgrade immediately** to ensure command chaining works correctly.

---

## Bug Fixes

### 🔧 Fixed Directory Persistence in Command Chains

**Problem:** When using command chains with the `>>>` operator, directory changes made by commands like `go` were not persisting through the chain. After the chain completed, the user would be returned to the original directory.

**Example of Bug:**
```bash
cd /tmp
go home >>> pwd
# Output showed /home/decatalyst, but user was still in /tmp
```

**Root Cause:** The executor had a `finally` block that always restored the original working directory after command chain execution.

**Fix:** Removed the directory restoration logic in `ccmd/core/executor.py`. Directory changes now persist naturally through command chains.

**Impact:** Command chaining now works as expected. Custom commands like `go myproject >>> claude` correctly navigate and stay in the target directory.

**Files Modified:** `ccmd/core/executor.py` (lines 168-218)

---

### ⏱️ Fixed Interactive Command Timeouts

**Problem:** Interactive commands (like `claude`, custom shells, or long-running processes) were timing out after 180 seconds, interrupting legitimate user sessions.

**Example of Bug:**
```bash
myinteractive  # Custom command: go myproject >>> claude
# Claude starts successfully but times out after 3 minutes
```

**Root Cause:** All commands were subject to a fixed 180-second timeout, regardless of whether they needed user interaction.

**Fix:** Added conditional timeout logic that detects commands marked as `interactive: true` and sets `timeout=None` for them, allowing indefinite runtime. Non-interactive commands still timeout after 180 seconds to prevent hangs.

**Impact:** Interactive commands can now run as long as needed. Users can work in `claude`, Python REPL, or any interactive session without unexpected timeouts.

**Files Modified:** `ccmd/core/executor.py` (lines 211-213, line 447)

---

### 📦 Fixed Pip Install Warnings on Ubuntu 24.04+

**Problem:** During CCMD installation, pip would fail with errors about "externally-managed-environment" on Ubuntu 24.04 and newer systems that implement PEP 668.

**Error Message:**
```
⚠ Warning: Failed to install dependencies: Command '['/usr/bin/python3', '-m', 'pip', 'install', '-q', '-r', '/path/to/requirements.txt']' returned non-zero exit status 1.
```

**Root Cause:** Ubuntu 24.04+ restricts system-wide pip installs to prevent conflicts with system packages. Regular `pip install` fails without the `--break-system-packages` flag.

**Fix:** Added automatic fallback logic in `ccmd/cli/install.py`:
1. First attempts regular `pip install`
2. If that fails, retries with `--break-system-packages` flag
3. If both fail, shows clear instructions to user

**Impact:** Silent, automatic installation of dependencies on all systems. Users no longer see confusing pip errors during setup.

**Files Modified:** `ccmd/cli/install.py` (lines 46-67)

---

### ➕ Enhanced Navigation System

**Enhancement:** Added support for custom project directory paths in the `go` command, allowing users to define frequently-accessed locations.

**Example Usage:**
```bash
# Users can add custom paths to commands.yaml
go myproject   # Navigate to /path/to/your/project
go workspace   # Navigate to /path/to/workspace
```

**Impact:** Faster navigation to frequently-used directories. Enables powerful custom commands like `go myproject >>> claude`.

**Files Modified:** `commands.yaml` (navigation paths section)

---

### 🎯 Standardized Timeout for Non-Interactive Commands

**Enhancement:** Increased timeout for non-interactive commands from 30 seconds to 180 seconds (3 minutes).

**Rationale:** Some legitimate commands (like large git operations, system scans, or builds) need more than 30 seconds but shouldn't run indefinitely.

**Impact:**
- Non-interactive commands have 3 minutes to complete before timing out
- Interactive commands have no timeout (can run indefinitely)
- Prevents system hangs from runaway processes while allowing slower operations to complete

**Files Modified:** `ccmd/core/executor.py` (line 213)

---

## Technical Details

### Changes by File

**`ccmd/__init__.py`**
- Bumped version from `1.1.2` to `1.1.3`

**`commands.yaml`**
- Enhanced support for custom project directory paths in `go` command

**`ccmd/core/executor.py`**
- Removed `finally` block that restored working directory after chain execution
- Added interactive command detection: `is_interactive = command_def and command_def.get('interactive', False)`
- Set conditional timeout: `timeout_value = None if is_interactive else 180`
- Applied timeout to subprocess calls in both single command and chain execution paths

**`ccmd/cli/install.py`**
- Added try-except logic for pip installation
- First attempt: Standard `pip install -q -r requirements.txt`
- Fallback attempt: `pip install --break-system-packages -q -r requirements.txt`
- Graceful error message if both attempts fail

### Commit History

```
feeb9bc - docs: update README for v1.1.3 release
078feca - fix: handle externally-managed pip environments gracefully
e213548 - fix: remove timeout for interactive commands
64a6d6e - fix: command chaining bugs and timeout issues (v1.1.3)
```

---

## Upgrade Instructions

### For Git Users

```bash
cd /path/to/ccmd
git pull origin ccmd
python3 run.py --install
source ~/.bashrc  # or ~/.zshrc
```

### For ZIP Users

1. Download v1.1.3: https://github.com/Wisyle/ccmd/releases/tag/v1.1.3
2. Extract and replace your existing ccmd folder
3. Run installer: `bash setup.sh` (or `.\setup.ps1` on Windows)
4. Reload shell: `source ~/.bashrc` (or `. $PROFILE` on PowerShell)

### Verify Upgrade

```bash
python3 run.py --version
# Should show: CCMD v1.1.3

# Test directory persistence
cd /tmp
go home >>> pwd
pwd  # Should still be in /home/<user>, not /tmp

# Test interactive commands (if you have any)
# They should no longer timeout after 180 seconds
```

---

## Breaking Changes

**None.** This release is 100% backward compatible with v1.1.2.

---

## Known Issues

None reported.

---

## Compatibility

- **Python:** 3.7+
- **Platforms:** Linux, Windows (PowerShell), WSL
- **Shells:** Bash, Zsh, Fish, PowerShell
- **Dependencies:** PyYAML >= 6.0, bcrypt >= 4.0.0 (optional, falls back to PBKDF2)

---

## Testing

This release was thoroughly tested with:
- ✅ 52/55 test cases passed
- ✅ Command chaining with directory persistence
- ✅ Interactive commands (claude, python REPL)
- ✅ Long-running non-interactive commands
- ✅ Pip installation on Ubuntu 24.04
- ✅ Custom command creation and management
- ✅ Edge cases (empty chains, special characters, timeout limits)

See full test results: `/mnt/c/Users/rober/targlobal/ccmd-notes/v1.1.3-TEST-PLAN.md`

---

## Security

No security-related changes in this release. All security features from v1.1.1 and v1.1.2 remain active:
- ✅ Master password protection
- ✅ Command injection prevention
- ✅ SSH key validation
- ✅ Sensitive command detection

---

## Credits

**Developer:** De Catalyst (@Wisyle)
**GitHub:** https://github.com/Wisyle
**Repository:** https://github.com/Wisyle/ccmd

---

## Support

- **Issues:** https://github.com/Wisyle/ccmd/issues
- **Email:** Robert5560newton@gmail.com
- **Twitter:** @iamdecatalyst

---

## Next Steps

After upgrading, you can:

1. **Test command chaining:**
   ```bash
   go home >>> pwd >>> echo "Success!"
   ```

2. **Create custom chained commands:**
   ```bash
   add
   # name: devwork
   # command: go projects >>> ls >>> echo "Ready to code!"
   ```

3. **Use interactive commands without worry:**
   ```bash
   # Mark as interactive during creation
   add
   # name: myrepl
   # command: python3
   # interactive: Yes
   ```

---

**Enjoy CCMD v1.1.3!**
