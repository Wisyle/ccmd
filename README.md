# 🧠 CCMD — Custom Command Manager

[![Latest Release](https://img.shields.io/github/v/release/Wisyle/ccmd?label=Download&color=brightgreen)](https://github.com/Wisyle/ccmd/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Security](https://img.shields.io/badge/security-enhanced-green.svg)](SECURITY_DISCLAIMER.md)

> **Cross-platform command enhancer for humans.**
> Replace long, repetitive terminal syntax with short, intuitive commands.
> Works on **Linux**, **Windows PowerShell**, and **WSL** — safe, rollback-ready, and open source.

> **🔐 New in v1.1.1:** Enterprise-grade security! Master password protection, command injection prevention, SSH key validation, and intelligent auto-locator.

> **⚠️ Important:** CCMD is a powerful tool that sits between your shell and you. Like electricity or any powerful tool, **it can be dangerous if used wrongly**. Please read the [Security Disclaimer](SECURITY_DISCLAIMER.md) before using CCMD. Use carefully, cautiously, and responsibly.

> **📌 Version Notice:** We **strongly recommend using v1.1.1 or later**. Older versions (v1.0.x, v1.1.0) lack critical security features and bug fixes. They will continue to work but are no longer supported with security updates. [Upgrade now](https://github.com/Wisyle/ccmd/releases/latest) — it's safe, fast, and backward compatible!

---

## 🧩 Overview

**CCMD** is an open-source project developed by **De Catalyst (Wisyle)**.  
It lets you define simple, natural shortcuts for everyday shell operations — no more typing endless flags or remembering weird syntax.

Instead of typing:
```bash
cd ~/Downloads
git add .
git commit -m "update"
git push
````

You can just write:

```bash
go downloads
push
```

CCMD handles the rest. It safely installs into your shell profile, manages custom commands through YAML, and supports plugins, system monitoring, and SSH management.

---

## ✨ Features

### 🔐 v1.1.1 Security Features (NEW!)
* **🔒 Master Password System** — Protect sensitive commands with bcrypt-hashed passwords
* **🛡️ Command Injection Prevention** — Automatic blocking of dangerous command patterns
* **🔐 SSH Key Validation** — Verify key permissions (0600) before use
* **🔍 Sensitive Command Detection** — Auto-detect and protect sudo, ssh, AWS commands
* **📁 Atomic File Operations** — Safe, corruption-proof file writes
* **🎯 Intelligent Auto-Locator** — No more path issues, works anywhere
* **📊 Audit Logging** — Track all authentication attempts
* **⚡ Security Cache** — 5-minute authentication window for convenience

**New Commands:** `init`, `debug`, `sudo`, `change-password`, `reset-password`

### 🆕 v1.1.0 Features
* **✨ Custom Commands** — Create your own commands with `add`, manage with `remove`
* **🔄 Instant Reload** — `reload` command updates config without manual reinstall
* **🎯 Interactive Push** — Full git workflow with file selection and auto-commit messages
* **📋 Command Manager** — Enable/disable commands with `list`
* **🛡️ Graceful Cancellation** — Press Ctrl+C anytime without ugly errors
* **🌍 Better Windows Support** — Fully tested on PowerShell with proper encoding

### Core Features
* **Cross-Platform Support** — Linux, WSL, Windows PowerShell (macOS code exists but untested*)
* **Natural Commands** — No prefixes; just type `go`, `push`, `cpu`, etc.
* **Smart Directory Navigation** — Search and jump to directories anywhere
* **Auto Git Integration** — Interactive add, commit, and push workflow
* **System Insights** — Monitor CPU, memory, and processes
* **Safe Rollback** — Backs up your shell configuration before any changes
* **Persistent Customization** — Your custom commands survive CCMD updates
* **Password Protection** — Mark custom commands as requiring authentication

*_macOS users: We need your feedback! Please test and report issues._

---

## 📚 Documentation

For detailed guides and technical documentation, see:

* **[🔐 Security Disclaimer](SECURITY_DISCLAIMER.md)** — **READ THIS FIRST!** Important security information and responsible use guidelines
* **[📋 Release Notes v1.1.1](RELEASE_NOTES_v1.1.1.md)** — Complete changelog and upgrade guide
* **[Features](FEATURES.md)** — Complete feature list including security features
* **[Installation Guide](INSTALLATION.md)** — Step-by-step installation for all platforms
* **[Usage Guide](USAGE.md)** — Complete command reference and usage examples
* **[Configuration Guide](CONFIGURATION.md)** — Customize and create your own commands
* **[Troubleshooting](TROUBLESHOOTING.md)** — Common issues and solutions
* **[Architecture](ARCHITECTURE.md)** — Technical architecture and development guide

---

## 🧱 Project Structure

```
ccmd/
 ├── cli/
 │   ├── main.py           # CLI entrypoint
 │   ├── install.py        # Installation and PATH setup
 │   ├── editor.py         # Interactive command editor
 │   └── ssh_manager.py    # Manage SSH aliases and keys
 ├── core/
 │   ├── parser.py         # Parse and map custom commands
 │   ├── executor.py       # Execute commands securely
 │   ├── registry.py       # Manage alias storage
 │   ├── rollback.py       # Backup & restore shell configs
 │   └── system_check.py   # Detect OS and compatibility
 ├── commands.yaml         # Default command definitions
 ├── run.py                # Master entrypoint
 ├── setup.sh              # Unix installer
 ├── setup.ps1             # Windows installer
 ├── LICENSE
 └── README.md
```

---

## 🚀 Installation

### Prerequisites

* Python **3.7+**

### Method 1: Using Git (Recommended)

For users comfortable with Git:

```bash
# Clone the repository (ccmd branch)
git clone -b ccmd https://github.com/Wisyle/ccmd.git
cd ccmd

# Run the installer for your platform
# Linux/macOS/WSL:
bash setup.sh

# Windows PowerShell:
.\setup.ps1

# Reload your shell
source ~/.bashrc  # or ~/.zshrc for Zsh, or restart terminal
```

### Method 2: Download ZIP (For non-Git users)

If you're not familiar with Git, download the official release:

1. **Download the latest release:**
   - Visit: https://github.com/Wisyle/ccmd/releases/latest
   - Download **Source code (zip)** under Assets
   - Or direct download: https://github.com/Wisyle/ccmd/archive/refs/tags/v1.1.0.zip

2. **Extract the files:**
   - Extract the downloaded ZIP file
   - Rename the folder to `ccmd` (remove any version suffix)

3. **Install CCMD:**

   **On Linux/macOS/WSL:**
   ```bash
   cd /path/to/ccmd
   bash setup.sh
   source ~/.bashrc  # or ~/.zshrc
   ```

   **On Windows PowerShell:**
   ```powershell
   cd C:\path\to\ccmd
   .\setup.ps1
   . $PROFILE
   ```

4. **Test installation:**
   ```bash
   python3 run.py --check
   go home
   ```

### Verify Installation

After installation, test that CCMD is working:

```bash
# Check system status
python3 run.py --check

# List available commands
python3 run.py --list

# Test a command
go home
```

### Uninstall / Rollback

```bash
python3 run.py --restore
```

### Update CCMD

**If installed via Git:**
```bash
cd /path/to/ccmd
git pull origin ccmd
python3 run.py --install
```

**If installed via ZIP:**
- Download the latest ZIP
- Extract and replace your existing ccmd folder
- Run the installer again (`bash setup.sh` or `.\setup.ps1`)

---

## 🧠 Default Commands

### Navigation
| Command      | Description                      | Example           |
| ------------ | -------------------------------- | ----------------- |
| `go <dir>`   | Navigate to directory or search  | `go downloads`    |

### Git Operations
| Command | Description                           | Notes                             |
| ------- | ------------------------------------- | --------------------------------- |
| `push`  | Interactive git add, commit, and push | Auto-generates commit messages 🆕 |

### System Monitoring
| Command | Description           | Platform Support   |
| ------- | --------------------- | ------------------ |
| `cpu`   | Show CPU usage        | Linux, macOS, Windows |
| `mem`   | Show memory usage     | Linux, macOS, Windows |
| `proc`  | List running processes| Linux, macOS, Windows |
| `kap`   | Kill process by PID   | Linux, macOS, Windows |

### Custom Commands 🆕 v1.1.0
| Command  | Description                    | Notes                               |
| -------- | ------------------------------ | ----------------------------------- |
| `add`    | Create a custom command        | Interactive prompts                 |
| `remove` | Delete a custom command        | Shows list to select from           |
| `list`   | Manage commands (enable/disable)| Toggle commands on/off             |

### CCMD Management
| Command     | Description                       | Notes                    |
| ----------- | --------------------------------- | ------------------------ |
| `reload`    | Reload config and update shell 🆕 | No manual reinstall needed |
| `update`    | Update CCMD from GitHub           | Downloads latest version |
| `version`   | Show current and latest version   | Checks GitHub releases   |
| `restore`   | Restore shell config from backup  | Rollback changes         |
| `uninstall` | Remove CCMD completely            | Cleans everything        |
| `hi`        | Show system dashboard             | System overview          |

---

## ⚙️ Configuration

### Default Commands

CCMD default commands are defined in `$CCMD_HOME/commands.yaml`. These are managed by CCMD and updated when you upgrade.

### Custom Commands (v1.1.0+)

Your custom commands are stored separately in:

```
~/.ccmd/custom_commands.yaml
```

**Why separate?** Your custom commands survive CCMD updates and never get overwritten.

**Create custom commands:**
```bash
add                    # Interactive command creation
```

**Remove custom commands:**
```bash
remove                 # Interactive command removal
```

**Reload after manual edits:**
```bash
reload                 # Reloads config and updates shell
```

Each command follows this format:

```yaml
mycommand:
  description: "What this command does"
  action: "the shell command to execute"
  type: custom
  interactive: false   # Set to true for commands needing user input
```

---

## 🔐 Security & Safety

* Backups created automatically before modifying any shell files.
* Rollback available anytime with `--restore`.
* SSH keys are never stored or transmitted.
* Commands executed via safe subprocess calls, never `eval`.

---

## 🧪 Testing Locally

Before global install, run:

```bash
python run.py --test
```

This simulates:

* Shell detection and rc edits
* Git and system command execution
* Rollback and uninstall checks

---

## 🧰 Example Usage

```bash
# Navigate fast
go downloads

# Push Git changes instantly
push

# Check system load
cpu

# Connect to your default server
ssh
```

---

## 🌍 Contributing

Contributions are welcome!
Fork the repo, create a branch, make your edits, and open a pull request.
A contribution guide will soon be added in `/docs/CONTRIBUTING.md`.

---

## 📜 License

Released under the **MIT License**.
Free to use, modify, and distribute.

---

## 🧑‍💻 Developed By

**De Catalyst**
**GitHub:** [@Wisyle](https://github.com/Wisyle)
**Email:** [Robert5560newton@gmail.com](mailto:Robert5560newton@gmail.com)
**X (Twitter):** [@iamdecatalyst](https://x.com/iamdecatalyst)
**Instagram:** [@iamdecatalyst](https://instagram.com/iamdecatalyst)
**Telegram:** [@iamdecatalyst](https://t.me/iamdecatalyst)

> For bug reports, updates, or collaboration inquiries, feel free to reach out.

---

## 🪄 Tagline

> “Stop remembering commands. Start commanding naturally.”

---


## Always check new releases before downloading 

