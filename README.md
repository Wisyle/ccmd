# CCMD - Cross-platform Command Manager

CCMD is a powerful command initiator that replaces repetitive terminal commands with simple, human-readable shortcuts. It works seamlessly across Bash, Zsh, PowerShell, CMD, and WSL.

## Features

- **Cross-platform**: Works on Linux, macOS, Windows, and WSL
- **Simple syntax**: Use natural commands like `go downloads` or `push`
- **Customizable**: Add, edit, and remove commands via YAML configuration
- **Safe**: Input sanitization, command validation, and automatic backups
- **Interactive editor**: Manage commands with built-in CLI editor
- **SSH management**: Store and manage SSH connection aliases

## Quick Start

```bash
# Navigate to common directories
go downloads    # cd ~/Downloads

# Git operations
push "initial commit"    # git add . && commit && push

# System monitoring
cpu             # Show CPU usage
mem             # Show memory usage
```

## Documentation

- **[Installation Guide](INSTALLATION.md)** - Complete installation instructions for all platforms
- **[Usage Guide](USAGE.md)** - How to use CCMD commands and features
- **[Configuration Guide](CONFIGURATION.md)** - Command configuration and customization
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions
- **[Architecture](ARCHITECTURE.md)** - Technical documentation and architecture

## Quick Installation

### Linux / macOS / WSL

```bash
git clone https://github.com/Wisyle/ccmd.git
cd ccmd
bash setup.sh
source ~/.bashrc
```

### Windows PowerShell

```powershell
git clone https://github.com/Wisyle/ccmd.git
cd ccmd
.\setup.ps1
. $PROFILE
```

## License

MIT License

## Support

For issues, questions, or suggestions, please open an issue on the repository.
