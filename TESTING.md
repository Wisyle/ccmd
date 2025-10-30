# CCMD Testing Guide

## Quick Test Commands

### Built-in Test Mode
```bash
ccmd --test
```
Tests: System detection, command registry, parser, executor

### Comprehensive Test Suite
```bash
# Run full test suite (18 tests)
/tmp/test_ccmd_v1.1.5.sh
```

---

## Manual Testing Checklist

### 1. Security Features (v1.1.5)

**Test --exec Flag Protection:**
```bash
# Should NOT show --exec in help
ccmd --help | grep exec

# Should block external calls
ccmd --exec "echo test"
# Expected: Error: --exec is for internal use only

# Should work internally (command chaining)
ccmd testchain
# Expected: Steps execute successfully
```

**Test Path Diagnostics:**
```bash
ccmd --check-paths
```
Expected output:
- ✓ CCMD_HOME validated
- ✓ Directory structure checked
- ✓ Files verified (run.py, commands.yaml)
- ✓ Shell integration confirmed
- ✓ Backup system checked

---

### 2. Basic Commands

**System Check:**
```bash
ccmd --check
```

**Version Info:**
```bash
ccmd --version
```

**List Commands:**
```bash
ccmd --list
```

**Debug Mode:**
```bash
ccmd --debug
```

---

### 3. Installation Tests

**Fresh Install:**
```bash
# Uninstall first
ccmd --uninstall

# Reinstall
python3 run.py --install

# Reload shell
source ~/.bashrc

# Test a command
ccmd hi
```

**Update Test:**
```bash
ccmd --update
```

---

### 4. Rollback/Recovery Tests

**Backup System:**
```bash
# Check backups exist
ls ~/.ccmd/backups/

# View backup manifest
cat ~/.ccmd/backups/manifest.json

# Restore from backup
ccmd --restore
```

---

### 5. Command Execution Tests

**Simple Commands:**
```bash
ccmd cpu      # CPU usage
ccmd mem      # Memory usage
ccmd proc     # Process list
```

**Directory Navigation:**
```bash
ccmd go home      # Go to home directory
ccmd go downloads # Go to downloads
```

**Command Chaining:**
```bash
ccmd testchain    # Test multi-step commands
```

---

### 6. Interactive Commands

**Command Editor:**
```bash
ccmd --edit
```

**Add Custom Command:**
```bash
ccmd add
```

**List with Details:**
```bash
ccmd list
```

---

### 7. Security/Auth Tests

**Master Password:**
```bash
# Initialize password
ccmd --init

# Change password
ccmd --change-password

# Reset password
ccmd --reset-password
```

**Protected Commands:**
```bash
# Should prompt for password
ccmd kap    # Kill all processes
ccmd sudo   # Superuser command
```

---

### 8. Development Testing

**From Dev Path:**
```bash
# Uninstall PyPI version
pip uninstall ccmd

# Install dev version (editable)
pip install -e /path/to/ccmd-dev

# Test
ccmd --version
ccmd --check-paths
```

**Test Atomic Writes (Python):**
```python
from ccmd.core.rollback import atomic_write_shell_config, validate_shell_syntax
from pathlib import Path

# Test atomic write
success, msg = atomic_write_shell_config(
    Path("/tmp/test.sh"),
    "echo 'test'\n"
)
print(f"Success: {success}, Message: {msg}")

# Test shell validation
is_valid, error = validate_shell_syntax("echo 'test'\n", "bash")
print(f"Valid: {is_valid}, Error: {error}")
```

---

### 9. Security Scanning

**Bandit (Static Analysis):**
```bash
# Install bandit
pip install bandit

# Scan for security issues
bandit -r ccmd/ -ll

# Expected: 0 HIGH severity
```

**Safety (Dependency Scan):**
```bash
# Install safety
pip install safety

# Check dependencies
safety check --file requirements.txt

# Expected: 0 vulnerabilities
```

---

### 10. Git/CI Tests

**Pre-commit Checks:**
```bash
# Verify git status
git status

# Verify remote
git remote -v

# Verify branch
git branch
```

**CI Workflow Tests:**
```bash
# Test security workflow locally
grep -r "subprocess.run.*shell=True" --include="*.py" ccmd/ | grep -v "executor.py" | grep -v "security.py"
# Expected: No output (or only whitelisted files)

# Test for hardcoded secrets
grep -r -E "(api_key|secret|password|token)\s*=\s*['\"][^'\"]+['\"]" --include="*.py" ccmd/
# Expected: Only test/config files
```

---

## Test Coverage by Feature

### v1.1.5 Security Features

| Feature | Test Command | Expected Result |
|---------|-------------|-----------------|
| --exec hidden | `ccmd --help \| grep exec` | No --exec shown |
| --exec blocked | `ccmd --exec "cmd"` | Error message |
| Path diagnostics | `ccmd --check-paths` | 7 checks pass |
| Atomic writes | Python unit test | Success |
| Shell validation | Python unit test | Valid/invalid detected |
| Dependabot | Check `.github/dependabot.yml` | File exists |
| Safety scanning | Check CI workflow | Safety step exists |
| THREAT_MODEL | Check file exists | File present |
| RECOVERY | Check file exists | File present |

### v1.1.4 Security Features

| Feature | Test Command | Expected Result |
|---------|-------------|-----------------|
| Tarfile validation | `ccmd --update` | No path traversal |
| HTTPS-only URLs | `ccmd --version` | Only HTTPS used |
| GitPython pinned | Check requirements.txt | Version 3.1.43 |

---

## Automated Test Suite

The comprehensive test suite (`/tmp/test_ccmd_v1.1.5.sh`) includes:

1. ✅ Built-in test mode
2. ✅ --exec flag hidden
3. ✅ --exec external blocking
4. ✅ --check-paths (4 sub-tests)
5. ✅ Command chaining (internal --exec)
6. ✅ System check (2 sub-tests)
7. ✅ Version check
8. ✅ Documentation files (3 files)
9. ✅ CI/CD configuration (2 files)
10. ✅ Python imports (2 modules)
11. ✅ Atomic write function
12. ✅ Shell syntax validation (2 cases)

**Total: 18 automated tests**

---

## Testing Before Release

**Pre-release checklist:**
```bash
# 1. Run all tests
/tmp/test_ccmd_v1.1.5.sh

# 2. Run security scans
bandit -r ccmd/ -ll
safety check --file requirements.txt

# 3. Test fresh install
ccmd --uninstall
python3 run.py --install
source ~/.bashrc

# 4. Test key features
ccmd --check-paths
ccmd --exec "echo test"  # Should fail
ccmd testchain           # Should work
ccmd --version

# 5. Verify git state
git status
git log --oneline -5
```

---

## Troubleshooting Tests

**If tests fail:**

1. **Check CCMD_HOME:**
   ```bash
   echo $CCMD_HOME
   ```

2. **Verify installation:**
   ```bash
   ccmd --check-paths
   ```

3. **Check Python version:**
   ```bash
   python3 --version  # Must be 3.7+
   ```

4. **Verify dependencies:**
   ```bash
   pip list | grep -E "(PyYAML|bcrypt|questionary|GitPython)"
   ```

5. **Check file permissions:**
   ```bash
   ls -la $CCMD_HOME/run.py
   ls -la ~/.bashrc
   ```

---

## Test Environment Setup

**Create test venv:**
```bash
python3 -m venv /tmp/test_ccmd
source /tmp/test_ccmd/bin/activate
pip install -e /path/to/ccmd-dev
```

**Clean test environment:**
```bash
# Remove test venv
rm -rf /tmp/test_ccmd

# Uninstall CCMD
ccmd --uninstall

# Remove user data
rm -rf ~/.ccmd
```

---

## Continuous Testing

**During development:**
```bash
# After code changes
python3 run.py --test

# After security changes
bandit -r ccmd/ -ll

# Before commit
/tmp/test_ccmd_v1.1.5.sh
```

**After each commit:**
```bash
git log -1 --stat
ccmd --check-paths
```

---

## Test Results Interpretation

**All tests passed (18/18):** ✅ Ready to push

**Some tests failed:** ⚠️ Review failures
- Check error messages
- Verify environment (CCMD_HOME, Python version)
- Test manually
- Fix issues before pushing

**Bandit scan results:**
- 0 HIGH: ✅ Good
- 5 MEDIUM: ✅ Acceptable (documented)
- X LOW: ✅ Normal (informational)

---

For more testing help, see:
- **RECOVERY.md** - Troubleshooting guide
- **THREAT_MODEL.md** - Security testing scenarios
- **SECURITY_CHANGELOG.md** - What changed per version
