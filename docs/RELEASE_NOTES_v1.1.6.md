# CCMD v1.1.6 Release Notes

**Release Date:** November 20, 2025
**Type:** Bug Fix Release

---

## Summary

This release fixes critical bugs in argument passing and command chaining security that affected password-protected commands.

---

## Bug Fixes

### 1. Argument Passing Bug (Critical)
**Issue:** Commands with placeholders only received the first argument, ignoring the rest.

**Example:**
```bash
# Before: sudo apt update → Only "apt" was passed, "update" lost
# Result: sudo apt (missing update argument)

# After: sudo apt update → All arguments passed correctly
# Result: sudo apt update
```

**Files Changed:** `ccmd/core/parser.py:148`

### 2. Command Chaining Password Bypass (Security)
**Issue:** Password-protected commands in chains bypassed authentication.

**Example:**
```bash
# Chain with sudo: go home >>> sudo apt update >>> echo done
# Before: sudo executed WITHOUT asking for CCMD password
# After: Properly asks for CCMD master password
```

**Files Changed:** `ccmd/core/executor.py:292`

---

## Technical Details

### Parser Fix
```python
# Before (only first arg)
parameters[param_name] = args[0]

# After (all args)
parameters[param_name] = ' '.join(args)
```

### Executor Fix
```python
# Before (bypassed security)
return self.execute(formatted_action, ...)

# After (proper security checks)
return self.execute_with_security(formatted_action, command_def=cmd_def, ...)
```

---

## Upgrade Instructions

### From PyPI
```bash
pip install --upgrade ccmd
```

### From Source
```bash
git pull origin ccmd
python3 run.py --install
source ~/.bashrc
```

---

## Verification

After upgrading, verify the fixes:

```bash
# Check version
ccmd version

# Test argument passing (should run full update)
sudo apt update

# Test chaining with password-protected command
# Should ask for CCMD password before executing sudo
```

---

## Breaking Changes

None. This is a backward-compatible bug fix release.

---

## Credits

- **Developer:** De Catalyst (@Wisyle)
- **License:** MIT

---

## Links

- **GitHub:** https://github.com/Wisyle/ccmd/releases/tag/v1.1.6
- **PyPI:** https://pypi.org/project/ccmd/
- **Security Policy:** https://github.com/Wisyle/ccmd/security
