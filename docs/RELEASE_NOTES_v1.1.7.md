# CCMD v1.1.7 Release Notes

**Release Date:** December 5, 2025
**Type:** Bug Fix Release

---

## Summary

This release fixes a critical bug where the `go <dirname>` command would fail to search for directories when used inside command chains. Previously, `go myproject` in a chain like `go myproject >>> ls` would incorrectly navigate to `~/Downloads` instead of searching for the `myproject` directory.

---

## Bug Fixes

### 1. Directory Search in Command Chains (Critical)

**Issue:** When using `go <dirname>` inside a command chain (e.g., `go myproject >>> ls`), the directory search functionality was bypassed. Instead of searching for the directory, it would default to the first entry in the `go` command's action dict (`downloads`).

**Root Cause:** The `_execute_ccmd_command` method in `executor.py` didn't handle the `search_dir` parameter that the parser sets when a directory name isn't a known subcommand.

**Before:**
```bash
# Custom command: devwork → go myproject >>> ls
$ devwork
→ Step 1/2: go myproject
  (executing CCMD command: go)
  (changed directory to: /home/user/Downloads)  # WRONG!
```

**After:**
```bash
# Custom command: devwork → go myproject >>> ls
$ devwork
→ Step 1/2: go myproject
  (executing CCMD command: go)
  (searching for directory: myproject)
  (changed directory to: /home/user/projects/myproject)  # CORRECT!
```

**Files Changed:**
- `ccmd/core/executor.py:271-281` - Added `search_dir` parameter handling
- `ccmd/core/executor.py:439-497` - Added `_search_directory()` helper method

---

## Technical Details

### New `_search_directory` Method

Added a new helper method to `CommandExecutor` class that mirrors the `search_directory` function in `main.py`:

```python
def _search_directory(self, dir_name: str) -> Optional[str]:
    """Search for directory by name in common locations"""
    # Searches ~/, ~/Downloads, ~/Documents, ~/Desktop, and more
    # Up to 3 levels deep, case-insensitive matching
```

### Modified `_execute_ccmd_command` Method

Added check for `search_dir` parameter right after parsing:

```python
# Handle directory search for 'go' command (v1.1.7 fix)
if 'search_dir' in parameters:
    dir_name = parameters['search_dir']
    found_path = self._search_directory(dir_name)
    if found_path:
        return 0, f"cd {found_path}", ""
    else:
        return 1, "", f"Directory '{dir_name}' not found"
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

After upgrading, test the fix:

```bash
# Check version
ccmd version

# Test direct go command (should work as before)
go downloads

# Test custom command with go in chain
# Create a test command:
add
# Name: testgo
# Command: go downloads >>> ls
# Then run:
testgo
# Should show Downloads directory contents
```

---

## Breaking Changes

None. This is a backward-compatible bug fix release.

---

## Full Changelog

- **FIX:** `go <dirname>` in command chains now correctly searches for directories
- **ADD:** `_search_directory()` helper method in `CommandExecutor`
- **ADD:** `search_dir` parameter handling in `_execute_ccmd_command()`

---

## Credits

- **Developer:** De Catalyst (@Wisyle)
- **License:** MIT

---

## Links

- **GitHub:** https://github.com/Wisyle/ccmd/releases/tag/v1.1.7
- **PyPI:** https://pypi.org/project/ccmd/
- **Security Policy:** https://github.com/Wisyle/ccmd/security
