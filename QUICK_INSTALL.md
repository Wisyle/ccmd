# Quick Installation Guide

## For Users Who Downloaded ZIP

If you downloaded the ZIP file and got nested folders, here's how to fix it:

### Step 1: Navigate to Downloads
```bash
cd ~/Downloads
```

### Step 2: Extract ZIP (if not already extracted)
```bash
unzip ccmd-*.zip
# This creates: ccmd-1.0.1/ folder
```

### Step 3: Navigate into the extracted folder
```bash
cd ccmd-1.0.1
# Now you're in the folder with setup.sh, run.py, etc.
```

### Step 4: Run Installation
```bash
bash setup.sh
```

### Step 5: Reload Shell
```bash
source ~/.bashrc
# or just restart your terminal
```

### Step 6: Test Commands
```bash
go home          # Navigate to home
go ccmd          # Navigate to CCMD installation
mem              # Show memory
update           # Update commands (works from anywhere!)
```

---

## Understanding the Installation

After installation, CCMD sets an environment variable `$CCMD_HOME` that points to where you installed it.

This means:
- ✅ Commands work from ANY directory
- ✅ `update` and `restore` work from anywhere
- ✅ `go ccmd` takes you to the installation folder

---

## Common Issues

### Issue: "update: command not found"
**Solution:** Run the installation:
```bash
cd ~/Downloads/ccmd-1.0.1  # or wherever you extracted
bash setup.sh
source ~/.bashrc
```

### Issue: "go ccmd" gives error
**Solution:** The installation sets `$CCMD_HOME`. After installing, run:
```bash
source ~/.bashrc
go ccmd  # Should work now
```

### Issue: Nested folders (ccmd/ccmd-1.0.1/ccmd)
**Solution:** Navigate to the folder with `setup.sh`:
```bash
cd ~/Downloads
ls
# If you see: ccmd-1.0.1/
cd ccmd-1.0.1
bash setup.sh
```

---

## Installation Locations

CCMD can be installed from anywhere. After installation:
- Your **commands work globally** (from any directory)
- The files stay where you downloaded them
- `$CCMD_HOME` environment variable points to the installation

**Recommended:** Install from home directory for easier access:
```bash
cd ~/Downloads
mv ccmd-1.0.1 ~/ccmd
cd ~/ccmd
bash setup.sh
```

Now you have:
- Installation at: `~/ccmd`
- Access from anywhere with `go ccmd`
- Global commands that work everywhere
