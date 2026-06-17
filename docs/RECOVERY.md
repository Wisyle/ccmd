# CCMD Recovery Guide

**Version:** 1.1.5
**Last Updated:** October 30, 2025

This guide helps you recover from CCMD installation failures, corrupted shell configs, and other issues.

---

## Table of Contents

1. [Quick Recovery Commands](#quick-recovery-commands)
2. [Installation Failed](#installation-failed)
3. [Shell Broken After Install](#shell-broken-after-install)
4. [CCMD Commands Not Working](#ccmd-commands-not-working)
5. [Forgotten Master Password](#forgotten-master-password)
6. [Corrupted commands.yaml](#corrupted-commandsyaml)
7. [Manual Removal](#manual-removal)
8. [Emergency Shell Recovery](#emergency-shell-recovery)

---

## Quick Recovery Commands

### If your shell is broken and you can still type:

```bash
# Restore from automatic backup
python3 /path/to/ccmd/run.py --restore

# Or manually remove CCMD integration
nano ~/.bashrc  # or ~/.zshrc, ~/.config/fish/config.fish
# Delete lines between "# CCMD Integration - Start" and "# CCMD Integration - End"
```

### If you can't access your shell at all:

1. **Linux/Mac:** Boot to recovery mode or use another terminal
2. **Windows:** Open PowerShell as Administrator
3. Edit shell config to remove CCMD integration (see [Emergency Shell Recovery](#emergency-shell-recovery))

---

## Installation Failed

### Symptom

```
Error: Failed to install CCMD
...
```

### Cause

- Missing dependencies (PyYAML)
- No write permissions to shell config
- Shell config file doesn't exist
- Python version too old (<3.7)

### Solution

**Step 1: Check Python version**
```bash
python3 --version
# Must be 3.7 or higher
```

**Step 2: Install dependencies**
```bash
pip3 install PyYAML bcrypt passlib
```

**Step 3: Check permissions**
```bash
# Bash/Zsh
ls -la ~/.bashrc
# Should show: -rw-r--r-- (readable/writable by you)

# Fish
ls -la ~/.config/fish/config.fish

# PowerShell
Get-Acl $PROFILE
```

**Step 4: Retry installation**
```bash
cd /path/to/ccmd
python3 run.py --install
```

**Step 5: If still fails, check automatic backup**
```bash
python3 run.py --restore
```

---

## Shell Broken After Install

### Symptom

After installing CCMD, your shell:
- Won't start
- Shows syntax errors
- Hangs on startup
- Displays error messages

### Automatic Recovery (v1.1.5+)

CCMD creates automatic backups before modifying shell configs:

```bash
# List available backups
ls -la ~/.ccmd/backups/

# Restore latest backup
python3 /path/to/ccmd/run.py --restore
```

### Manual Recovery

**If `--restore` doesn't work:**

#### For Bash/Zsh:

1. **Open a text editor** (nano, vim, or gedit)
   ```bash
   nano ~/.bashrc  # or ~/.zshrc
   ```

2. **Find CCMD integration** (between these markers):
   ```bash
   # CCMD Integration - Start
   ...
   # CCMD Integration - End
   ```

3. **Delete everything between the markers** (including the markers)

4. **Save and exit**
   - Nano: `Ctrl+O`, `Enter`, `Ctrl+X`
   - Vim: `Esc`, `:wq`, `Enter`

5. **Reload shell**
   ```bash
   source ~/.bashrc  # or source ~/.zshrc
   ```

#### For Fish:

```bash
nano ~/.config/fish/config.fish
# Delete CCMD Integration section
source ~/.config/fish/config.fish
```

#### For PowerShell:

```powershell
notepad $PROFILE
# Delete CCMD Integration section
. $PROFILE
```

### Restore from Backup Manually

If automatic backups exist but `--restore` fails:

```bash
# Find backups
ls ~/.ccmd/backups/

# Copy backup over current file
cp ~/.ccmd/backups/.bashrc.20251030_120000.bak ~/.bashrc

# Reload
source ~/.bashrc
```

---

## CCMD Commands Not Working

### Symptom

```bash
ccmd: command not found
# or
go: command not found
```

### Diagnosis

**Check if CCMD is installed:**
```bash
echo $CCMD_HOME
# Should show: /path/to/ccmd
```

**If empty:**
```bash
# CCMD is not installed
python3 /path/to/ccmd/run.py --install
```

**If shows path but commands don't work:**

1. **Reload shell:**
   ```bash
   source ~/.bashrc  # or appropriate shell config
   ```

2. **Check if CCMD files exist:**
   ```bash
   ls $CCMD_HOME/run.py
   # Should show: /path/to/ccmd/run.py
   ```

3. **If files missing:** CCMD was moved or deleted
   - Uninstall: `python3 /new/path/to/ccmd/run.py --uninstall`
   - Reinstall from new location

### CCMD Moved to Different Directory

**Symptom:**
```
⚠ CCMD not found at /old/path
→ Please reinstall CCMD
```

**Solution:**
```bash
# 1. Uninstall from shell config (use full path)
python3 /new/path/to/ccmd/run.py --uninstall

# 2. Reinstall from new location
cd /new/path/to/ccmd
python3 run.py --install

# 3. Reload shell
exec bash  # or exec zsh, etc.
```

---

## Forgotten Master Password

### Symptom

```
Master password: [wrong password]
✗ Authentication failed - command aborted
```

### Solution: Reset Password

```bash
# This will DELETE your password (you'll need to set a new one)
python3 /path/to/ccmd/run.py --reset-password
```

**Confirm:**
```
⚠ WARNING: This will DELETE your master password
Continue? (yes/no): yes
✓ Master password deleted
```

**Set new password:**
```bash
python3 /path/to/ccmd/run.py --init
# Follow prompts to set new password
```

**Note:** You CANNOT recover the old password. It's hashed with bcrypt (irreversible).

---

## Corrupted commands.yaml

### Symptom

```
Error: Failed to load commands.yaml
YAML syntax error at line X
```

### Solution 1: Restore from Backup

```bash
# Check if backup exists
ls ~/.ccmd/backups/*commands.yaml*

# Copy backup
cp ~/.ccmd/backups/commands.yaml.20251030_120000.bak ~/path/to/ccmd/commands.yaml
```

### Solution 2: Regenerate Default Config

```bash
# Rename corrupted file
cd /path/to/ccmd
mv commands.yaml commands.yaml.broken

# Reinstall to create new default
python3 run.py --install
```

### Solution 3: Manually Fix YAML

```bash
# Open in editor
nano commands.yaml

# Common YAML errors:
# - Missing colon: action "ls" → action: "ls"
# - Wrong indentation: must use spaces (not tabs)
# - Unclosed quotes: description: "go home → description: "go home"
# - Invalid characters: avoid special chars outside quotes
```

**Validate YAML syntax:**
```python
# In Python
import yaml
with open('commands.yaml') as f:
    yaml.safe_load(f)  # Should not raise exception
```

---

## Manual Removal

### Complete Uninstallation

**Step 1: Remove shell integration**
```bash
python3 /path/to/ccmd/run.py --uninstall
```

**Step 2: Remove CCMD files**
```bash
# Remove installation directory
rm -rf /path/to/ccmd

# Remove user data (optional - this deletes backups and passwords)
rm -rf ~/.ccmd
```

**Step 3: Verify removal**
```bash
# Open new shell
exec bash

# Try CCMD command (should fail)
ccmd --version
# Expected: command not found
```

### If --uninstall Doesn't Work

**Manual shell config cleanup:**

#### Bash:
```bash
nano ~/.bashrc
# Delete CCMD Integration section
source ~/.bashrc
```

#### Zsh:
```bash
nano ~/.zshrc
# Delete CCMD Integration section
source ~/.zshrc
```

#### Fish:
```bash
nano ~/.config/fish/config.fish
# Delete CCMD Integration section
source ~/.config/fish/config.fish
```

#### PowerShell:
```powershell
notepad $PROFILE
# Delete CCMD Integration section
. $PROFILE
```

---

## Emergency Shell Recovery

### If You Can't Start a Shell at All

#### Linux:

1. **Boot to recovery mode:**
   - Reboot system
   - Hold `Shift` during boot (GRUB menu)
   - Select "Advanced Options" → "Recovery Mode"
   - Select "Drop to root shell prompt"

2. **Mount filesystem as writable:**
   ```bash
   mount -o remount,rw /
   ```

3. **Edit shell config:**
   ```bash
   nano /home/USERNAME/.bashrc
   # Delete CCMD Integration section
   ```

4. **Reboot:**
   ```bash
   reboot
   ```

#### Mac:

1. **Boot to Single User Mode:**
   - Reboot Mac
   - Hold `Cmd+S` during boot

2. **Mount filesystem:**
   ```bash
   /sbin/mount -uw /
   ```

3. **Edit shell config:**
   ```bash
   nano /Users/USERNAME/.zshrc
   # Delete CCMD Integration section
   ```

4. **Reboot:**
   ```bash
   reboot
   ```

#### Windows:

1. **Access PowerShell as Admin** (Windows boots normally)

2. **Edit PowerShell profile:**
   ```powershell
   notepad C:\Users\USERNAME\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
   # Delete CCMD Integration section
   ```

3. **Or rename profile temporarily:**
   ```powershell
   Rename-Item $PROFILE "$PROFILE.bak"
   # Open new PowerShell (CCMD won't load)
   ```

#### WSL:

1. **Open PowerShell (Windows side)**

2. **Edit WSL shell config:**
   ```powershell
   notepad \\wsl$\Ubuntu\home\USERNAME\.bashrc
   # Delete CCMD Integration section
   ```

3. **Or launch WSL without .bashrc:**
   ```powershell
   wsl bash --norc
   nano ~/.bashrc  # Now you can edit
   ```

---

## Diagnostic Tools

### Check CCMD Status

```bash
# System check
python3 /path/to/ccmd/run.py --check

# Path diagnostics (v1.1.5+)
python3 /path/to/ccmd/run.py --check-paths

# List installed commands
python3 /path/to/ccmd/run.py --list

# Version info
python3 /path/to/ccmd/run.py --version
```

### Check Backups

```bash
# List all backups
ls -la ~/.ccmd/backups/

# View manifest
cat ~/.ccmd/backups/manifest.json
```

### Debug Mode (v1.1.3+)

```bash
# Enable verbose output
python3 /path/to/ccmd/run.py --debug

# Combine with other commands
python3 /path/to/ccmd/run.py --debug go home
```

---

## Prevention Tips

1. **Before updates:** Shell configs are automatically backed up (v1.1.5+)
2. **After install:** Test in new shell before closing current one
3. **Keep backups:** `cp ~/.bashrc ~/.bashrc.manual_backup`
4. **Test changes:** Use `--test` flag before deployment
5. **Use version control:** Track your commands.yaml in git

---

## Still Need Help?

### Community Support

- **GitHub Issues:** https://github.com/Wisyle/ccmd/issues
- **GitHub Discussions:** https://github.com/Wisyle/ccmd/discussions

### Direct Contact

- **Email:** Robert5560newton@gmail.com
- **Twitter:** @iamdecatalyst

### When Reporting Issues

Include:
1. OS and shell type (`echo $SHELL`)
2. CCMD version (`python3 /path/to/ccmd/run.py --version`)
3. Error message (full output)
4. Steps to reproduce
5. Output of `python3 /path/to/ccmd/run.py --check`

---

## Recovery Checklist

Use this when troubleshooting:

- [ ] Can you open a shell at all?
  - No → See [Emergency Shell Recovery](#emergency-shell-recovery)
  - Yes → Continue

- [ ] Can you run Python?
  - Test: `python3 --version`
  - No → Install Python 3.7+

- [ ] Does `CCMD_HOME` exist?
  - Test: `echo $CCMD_HOME`
  - Empty → CCMD not installed

- [ ] Do CCMD files exist?
  - Test: `ls $CCMD_HOME/run.py`
  - No → Reinstall or update path

- [ ] Can you run `--restore`?
  - Test: `python3 $CCMD_HOME/run.py --restore`
  - Yes → Try restoring

- [ ] Do backups exist?
  - Test: `ls ~/.ccmd/backups/`
  - Yes → Manual restore

- [ ] All else fails?
  - → Manual removal and clean reinstall

---

**Remember:** CCMD creates automatic backups before every modification (v1.1.5+). Recovery is usually just one command away!

For security issues, see [SECURITY.md](SECURITY.md).
