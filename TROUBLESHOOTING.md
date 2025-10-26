# Troubleshooting Guide

## Installation Issues

### Permission Denied on setup.sh

**Problem:** Can't execute setup.sh script

**Solution:**
```bash
chmod +x setup.sh
./setup.sh
```

### Python Not Found

**Problem:** `python3: command not found`

**Solution:**

Check Python installation:
```bash
# Try different python commands
python --version
python3 --version
python3.9 --version

# If not installed, install Python 3.7+
# Ubuntu/Debian
sudo apt install python3 python3-pip

# macOS
brew install python3

# Windows
# Download from python.org
```

### pip/pip3 Not Found

**Problem:** `pip3: command not found`

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install python3-pip

# macOS
python3 -m ensurepip

# Use python module instead
python3 -m pip install PyYAML
```

### PyYAML Installation Failed

**Problem:** Cannot install PyYAML dependency

**Solution:**
```bash
# Try different methods
pip3 install PyYAML
python3 -m pip install PyYAML
pip install PyYAML

# If still failing, check permissions
sudo pip3 install PyYAML

# Or install for user only
pip3 install --user PyYAML
```

## Command Not Working

### Commands Not Available After Installation

**Problem:** After running setup.sh, commands like `go` or `push` don't work

**Solution:**

Reload your shell configuration:
```bash
# For Bash
source ~/.bashrc

# For Zsh
source ~/.zshrc

# For Fish
source ~/.config/fish/config.fish

# For PowerShell
. $PROFILE

# Or simply restart your terminal
```

### Command Not Found: ccmd

**Problem:** `ccmd: command not found`

**Solution:**

1. Check if CCMD was installed:
   ```bash
   grep -A 5 "CCMD Integration" ~/.bashrc   # or ~/.zshrc
   ```

2. If not found, reinstall:
   ```bash
   cd /path/to/ccmd
   python3 run.py --install
   ```

3. Reload shell:
   ```bash
   source ~/.bashrc  # or ~/.zshrc
   ```

### commands.yaml Not Found

**Problem:** `Error: commands.yaml not found`

**Solution:**

1. Check if file exists:
   ```bash
   ls -la ~/ccmd/commands.yaml
   ```

2. If missing, copy from repository:
   ```bash
   cd ~/ccmd
   git pull
   # or manually create from template
   ```

3. Reinstall:
   ```bash
   python3 run.py --install
   ```

## Execution Issues

### Command Executes But Doesn't Work

**Problem:** Command runs but doesn't do what it should

**Examples:**
- `go downloads` shows `cd ~/Downloads` but doesn't change directory
- Commands output text instead of executing

**Solution:**

This is expected behavior for navigation commands. The output needs to be evaluated by the shell:

```bash
# Wrong (just shows the command)
python3 run.py go downloads

# Correct (actually changes directory)
go downloads
```

After installation, use the command directly without `python3 run.py`.

### Git Commands Failing

**Problem:** `push` command fails with git errors

**Solutions:**

1. Not in a git repository:
   ```bash
   cd /path/to/git/repo
   git status
   # If not a repo, initialize:
   git init
   git remote add origin <url>
   ```

2. No files to commit:
   ```bash
   # Check status
   git status
   # Add files first
   git add .
   # Then push
   push "commit message"
   ```

3. No remote configured:
   ```bash
   git remote add origin <your-repo-url>
   ```

4. Authentication issues:
   ```bash
   # Set up SSH key or use HTTPS with credentials
   git remote -v
   ```

### Permission Denied Errors

**Problem:** `Permission denied` when running commands

**Solutions:**

1. File permissions:
   ```bash
   chmod +x /path/to/ccmd/run.py
   ```

2. Shell config permissions:
   ```bash
   chmod 644 ~/.bashrc  # or ~/.zshrc
   ```

3. Python module permissions:
   ```bash
   # Reinstall PyYAML for user
   pip3 install --user PyYAML
   ```

## Configuration Issues

### Changes to commands.yaml Not Taking Effect

**Problem:** Edited commands.yaml but changes don't apply

**Solution:**

Reload commands:
```bash
# Option 1
python3 run.py --reload

# Option 2
update

# Option 3
python3 run.py --install
source ~/.bashrc  # or ~/.zshrc
```

### YAML Syntax Errors

**Problem:** `YAML parsing error` or `invalid syntax`

**Common Issues:**

1. Incorrect indentation:
   ```yaml
   # Wrong
   commands:
   mycommand:
     description: Test

   # Correct (2-space indentation)
   commands:
     mycommand:
       description: Test
   ```

2. Missing quotes:
   ```yaml
   # Wrong
   description: It's a test

   # Correct
   description: "It's a test"
   ```

3. Special characters:
   ```yaml
   # Wrong
   action: echo Hello: World

   # Correct
   action: "echo Hello: World"
   ```

**Solution:**

Use YAML validator:
```bash
python3 -c "import yaml; yaml.safe_load(open('commands.yaml'))"
```

### Backup/Restore Issues

**Problem:** Can't restore previous configuration

**Solution:**

1. Check backups:
   ```bash
   ls -la ~/.ccmd/backups/
   ```

2. Manually restore:
   ```bash
   cp ~/.ccmd/backups/bashrc_backup_YYYYMMDD ~/.bashrc
   source ~/.bashrc
   ```

3. Or use restore command:
   ```bash
   python3 run.py --restore
   ```

## OS-Specific Issues

### Windows PowerShell Issues

**Problem:** Commands not working in PowerShell

**Solutions:**

1. Execution policy:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. Profile not loaded:
   ```powershell
   Test-Path $PROFILE
   # If False, create it:
   New-Item -Path $PROFILE -Type File -Force
   ```

3. Reload profile:
   ```powershell
   . $PROFILE
   ```

### WSL-Specific Issues

**Problem:** Commands work in Windows but not WSL (or vice versa)

**Solution:**

WSL and Windows have separate installations. Install separately:

```bash
# In WSL
cd /path/to/ccmd
bash setup.sh
source ~/.bashrc

# In PowerShell (Windows)
cd C:\path\to\ccmd
.\setup.ps1
. $PROFILE
```

### macOS Issues

**Problem:** Commands not working on macOS

**Solutions:**

1. Use correct shell:
   ```bash
   echo $SHELL
   # If zsh:
   source ~/.zshrc
   # If bash:
   source ~/.bashrc
   ```

2. Check installation:
   ```bash
   cat ~/.zshrc | grep CCMD  # or ~/.bashrc
   ```

## Performance Issues

### Slow Command Execution

**Problem:** Commands take long time to execute

**Solutions:**

1. Check command complexity:
   ```bash
   # See what the command does
   python3 run.py --list
   ```

2. Optimize complex commands in commands.yaml

3. Check system resources:
   ```bash
   cpu
   mem
   ```

### Shell Startup Slow

**Problem:** Terminal takes long to start after CCMD installation

**Solution:**

This is usually not CCMD-related, but if suspected:

1. Check RC file size:
   ```bash
   wc -l ~/.bashrc  # or ~/.zshrc
   ```

2. CCMD adds minimal overhead (just function definitions)

3. To test, temporarily disable:
   ```bash
   # Comment out CCMD section
   nano ~/.bashrc
   # Comment lines between "# CCMD Integration - Start" and "End"
   source ~/.bashrc
   ```

## Getting Help

### Enable Debug Mode

Run commands directly with Python to see errors:

```bash
python3 run.py --check
python3 run.py --list
python3 run.py yourcommand
```

### Check System Status

```bash
python3 run.py --check
```

This shows:
- Operating system
- Shell type
- Number of commands loaded
- Any errors

### Reset Everything

If all else fails, complete reset:

```bash
# 1. Restore shell config
python3 run.py --restore

# 2. Remove CCMD directory
rm -rf ~/.ccmd

# 3. Reinstall
cd /path/to/ccmd
bash setup.sh
source ~/.bashrc
```

### Still Having Issues?

1. Check the [USAGE.md](USAGE.md) guide
2. Review [CONFIGURATION.md](CONFIGURATION.md) for proper syntax
3. Open an issue on GitHub with:
   - Your OS and shell type
   - Output of `python3 run.py --check`
   - The command you're trying to run
   - Any error messages

## Common Error Messages

### "Error: Command not found in registry"

**Cause:** Command doesn't exist in commands.yaml

**Solution:**
```bash
# List available commands
python3 run.py --list

# Or add the command
python3 run.py --edit
```

### "Error: Invalid command syntax"

**Cause:** Malformed command in commands.yaml

**Solution:**
Check YAML syntax in commands.yaml

### "Error: No shell configuration file found"

**Cause:** No ~/.bashrc, ~/.zshrc, or $PROFILE found

**Solution:**
```bash
# Create one
touch ~/.bashrc  # or ~/.zshrc
python3 run.py --install
```

### "Warning: Backup failed"

**Cause:** Cannot write to ~/.ccmd/backups/

**Solution:**
```bash
# Create backup directory
mkdir -p ~/.ccmd/backups
chmod 755 ~/.ccmd/backups
```
