#!/bin/bash
# CCMD Installation Script for Unix-like systems (Linux, macOS, WSL)

set -e

echo "======================================"
echo "CCMD Installation Script"
echo "======================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Found Python $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Warning: pip3 is not installed. Installing dependencies may fail."
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Installation directory: $SCRIPT_DIR"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet || true
else
    echo "Warning: requirements.txt not found. Skipping dependency installation."
fi

# Make run.py executable
chmod +x "$SCRIPT_DIR/run.py"

# Run installation
echo ""
echo "Installing CCMD commands..."
python3 "$SCRIPT_DIR/run.py" --install

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "To start using CCMD:"
echo "1. Restart your terminal, OR"
echo "2. Run: source ~/.bashrc (or ~/.zshrc for Zsh)"
echo ""
echo "Available commands:"
echo "  go <target>      - Navigate to directories (e.g., 'go downloads')"
echo "  push [message]   - Git add, commit, and push"
echo "  cpu              - Show CPU usage"
echo "  mem              - Show memory usage"
echo "  proc             - Show running processes"
echo "  kap <pid>        - Kill a process by PID"
echo ""
echo "For more commands, run: python3 $SCRIPT_DIR/run.py --list"
echo "To edit commands, run: python3 $SCRIPT_DIR/run.py --edit"
echo ""
