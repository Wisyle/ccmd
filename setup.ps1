# CCMD Installation Script for Windows PowerShell

Write-Host "======================================"
Write-Host "CCMD Installation Script"
Write-Host "======================================"
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found $pythonVersion"
} catch {
    Write-Host "Error: Python is not installed or not in PATH."
    Write-Host "Please install Python 3 and add it to PATH, then try again."
    exit 1
}

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Installation directory: $scriptDir"
Write-Host ""

# Install Python dependencies
Write-Host "Installing Python dependencies..."
$requirementsFile = Join-Path $scriptDir "requirements.txt"
if (Test-Path $requirementsFile) {
    pip install -r $requirementsFile --quiet
} else {
    Write-Host "Warning: requirements.txt not found. Skipping dependency installation."
}

# Run installation
Write-Host ""
Write-Host "Installing CCMD commands..."
$runPy = Join-Path $scriptDir "run.py"
python $runPy --install

Write-Host ""
Write-Host "======================================"
Write-Host "Installation Complete!"
Write-Host "======================================"
Write-Host ""
Write-Host "To start using CCMD:"
Write-Host "1. Restart your PowerShell terminal, OR"
Write-Host "2. Run: . `$PROFILE"
Write-Host ""
Write-Host "Available commands:"
Write-Host "  go <target>      - Navigate to directories (e.g., 'go downloads')"
Write-Host "  push [message]   - Git add, commit, and push"
Write-Host "  cpu              - Show CPU usage"
Write-Host "  mem              - Show memory usage"
Write-Host "  proc             - Show running processes"
Write-Host "  kap <pid>        - Kill a process by PID"
Write-Host ""
Write-Host "For more commands, run: python $runPy --list"
Write-Host "To edit commands, run: python $runPy --edit"
Write-Host ""
