# 🚀 CCMD v1.0.0 - Initial Release

**The beginning of the Lazy journey**

CCMD (Cross-platform Command Manager) is a powerful command enhancer that replaces repetitive terminal commands with simple, human-readable shortcuts.

## ✨ What's Included

### Core Features
- **Cross-platform Support** - Works on Linux, macOS, Windows, and WSL
- **Multiple Shell Support** - Bash, Zsh, Fish, PowerShell, CMD
- **Safe Installation** - Automatic backups before any shell configuration changes
- **Rollback Support** - Restore previous configurations anytime
- **Security First** - Input sanitization, command validation, no eval() usage

### Default Commands
- `go` - Quick navigation to common directories (downloads, documents, desktop, home)
- `push` - Git add, commit, and push in one command
- `cpu` - Show CPU usage (cross-platform)
- `mem` - Show memory usage (cross-platform)
- `proc` - Show running processes
- `kap` - Kill process by PID
- `update` - Reload commands from configuration
- `restore` - Restore shell configuration from backup

### Management Tools
- **Interactive Editor** - Add, edit, and delete commands through CLI
- **SSH Manager** - Manage SSH connection aliases
- **Command Registry** - YAML-based command configuration
- **System Check** - Verify OS and shell compatibility

### Documentation
- Complete installation guide
- Usage guide with examples
- Configuration guide for custom commands
- Troubleshooting guide
- Technical architecture documentation

## 📥 Installation

### Method 1: Download Release ZIP
1. Download `ccmd-v1.0.0.zip` from this release
2. Extract to a folder named `ccmd`
3. Open terminal in the ccmd folder
4. Run the installer:
   - Linux/macOS/WSL: `bash setup.sh`
   - Windows PowerShell: `.\setup.ps1`
5. Restart your terminal or source your shell config

### Method 2: Git Clone
```bash
git clone -b ccmd https://github.com/Wisyle/ccmd.git
cd ccmd
bash setup.sh  # Linux/macOS/WSL
# or
.\setup.ps1    # Windows PowerShell
```

## 📚 Documentation

- [Installation Guide](https://github.com/Wisyle/ccmd/blob/ccmd/INSTALLATION.md)
- [Usage Guide](https://github.com/Wisyle/ccmd/blob/ccmd/USAGE.md)
- [Configuration Guide](https://github.com/Wisyle/ccmd/blob/ccmd/CONFIGURATION.md)
- [Troubleshooting](https://github.com/Wisyle/ccmd/blob/ccmd/TROUBLESHOOTING.md)
- [Architecture](https://github.com/Wisyle/ccmd/blob/ccmd/ARCHITECTURE.md)

## 🔒 Security

- No `eval()` usage
- Input sanitization for all user inputs
- Command validation blocks dangerous patterns
- Automatic backups before configuration changes
- Safe subprocess execution only

## 📊 Requirements

- Python 3.7 or higher
- No additional dependencies except PyYAML (auto-installed)

## 🙏 Credits

Developed by **De Catalyst (Wisyle)**
- GitHub: [@Wisyle](https://github.com/Wisyle)
- Email: Robert5560newton@gmail.com
- Twitter: [@iamdecatalyst](https://x.com/iamdecatalyst)
- Instagram: [@iamdecatalyst](https://instagram.com/iamdecatalyst)
- Telegram: [@iamdecatalyst](https://t.me/iamdecatalyst)

---

**"Stop remembering commands. Start commanding naturally."**
