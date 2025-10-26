# Installation Guide

## Prerequisites

- Python 3.7 or higher
- Git (for cloning the repository)

## Linux / macOS / WSL

### Step 1: Clone the Repository

```bash
git clone https://github.com/Wisyle/ccmd.git
cd ccmd
```

### Step 2: Run Installation Script

```bash
bash setup.sh
```

The installation script will:
- Install PyYAML dependency
- Create ~/.ccmd directory
- Add shell functions to your RC file (~/.bashrc or ~/.zshrc)
- Create backups of your shell configuration

### Step 3: Reload Shell Configuration

```bash
# For Bash users
source ~/.bashrc

# For Zsh users
source ~/.zshrc

# Or simply restart your terminal
```

## Windows PowerShell

### Step 1: Clone the Repository

```powershell
git clone https://github.com/Wisyle/ccmd.git
cd ccmd
```

### Step 2: Run Installation Script

```powershell
.\setup.ps1
```

The installation script will:
- Install PyYAML dependency
- Create PowerShell profile if it doesn't exist
- Add CCMD functions to your PowerShell profile
- Create backups of your profile

### Step 3: Reload PowerShell Profile

```powershell
. $PROFILE

# Or simply restart PowerShell
```

## Verifying Installation

After installation, test that CCMD is working:

```bash
# List all available commands
python3 run.py --list

# Check system configuration
python3 run.py --check

# Test a simple command
go home
```

## Manual Installation

If you prefer to install manually:

1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Add to your shell RC file (~/.bashrc, ~/.zshrc, or $PROFILE):
   ```bash
   # CCMD Integration - Start
   export CCMD_DIR="/path/to/ccmd"

   # CCMD command function
   ccmd() {
       python3 "$CCMD_DIR/run.py" "$@"
   }

   # Individual command aliases will be added here by CCMD
   # CCMD Integration - End
   ```

3. Run the installation to generate command aliases:
   ```bash
   python3 run.py --install
   ```

## Uninstallation

To remove CCMD:

### Option 1: Use Restore Command

```bash
python3 run.py --restore
```

This will restore your shell configuration from the last backup.

### Option 2: Manual Removal

1. Edit your shell RC file (~/.bashrc, ~/.zshrc, or $PROFILE)
2. Remove the section between `# CCMD Integration - Start` and `# CCMD Integration - End`
3. Restart your terminal or source your shell config

## Troubleshooting Installation

### Permission Denied on setup.sh

```bash
chmod +x setup.sh
./setup.sh
```

### Python Not Found

Make sure Python 3.7+ is installed:

```bash
python3 --version  # Should show Python 3.7 or higher
```

### Commands Not Working After Installation

Reload your shell configuration:

```bash
source ~/.bashrc   # Bash
source ~/.zshrc    # Zsh
. $PROFILE         # PowerShell
```

Or simply restart your terminal.

### PyYAML Installation Failed

Install manually:

```bash
pip3 install PyYAML
# or
python3 -m pip install PyYAML
```
