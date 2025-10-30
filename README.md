# 🧠 CCMD — Custom Command Manager

[![PyPI version](https://img.shields.io/pypi/v/ccmd.svg?label=PyPI&color=blue)](https://pypi.org/project/ccmd/)
[![Latest Release](https://img.shields.io/github/v/release/Wisyle/ccmd?label=GitHub&color=brightgreen)](https://github.com/Wisyle/ccmd/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Security](https://img.shields.io/badge/security-hardened-green.svg)](SECURITY.md)
[![Downloads](https://img.shields.io/pypi/dm/ccmd.svg)](https://pypi.org/project/ccmd/)

> **Cross-platform command enhancer for humans.**
> Replace long, repetitive terminal syntax with short, intuitive commands.
> Works on **Linux**, **Windows PowerShell**, and **WSL** — safe, rollback-ready, and open source.

> **🔒 New in v1.1.5:** Advanced Security Release! Internal flag protection, atomic shell writes, path diagnostics, threat model documentation, and automated dependency scanning. [See Security Report](SECURITY_CHANGELOG.md)

> **🛡️ v1.1.4:** Security Hardening Release! 0 HIGH vulnerabilities, comprehensive security audit, automated scanning, and professional security documentation.

> **✨ v1.1.3:** Bug Fix Release! Fixed command chaining directory persistence, interactive timeout issues, and pip install warnings.

> **⚠️ Important:** CCMD is a powerful tool that sits between your shell and you. Like electricity or any powerful tool, **it can be dangerous if used wrongly**. Please read the [Security Policy](SECURITY.md) and [Threat Model](THREAT_MODEL.md) before using CCMD. Use carefully, cautiously, and responsibly.

> **📌 Version Notice:** We **strongly recommend using v1.1.5 or later**. This version includes critical security enhancements and passes all automated security scans with comprehensive threat model documentation. [Upgrade now](https://github.com/Wisyle/ccmd/releases/latest) — it's safe, fast, and backward compatible!

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

### 🔒 v1.1.5 Advanced Security (LATEST!)
* **🔐 Internal Flag Protection** — `--exec` hidden from help, environment-gated for internal use only
* **⚛️ Atomic Shell Config Writes** — Prevents corruption with temp file + atomic rename pattern
* **🩺 Path Diagnostics Command** — `--check-paths` validates installation, environment, and backups
* **🛡️ Threat Model Documentation** — Complete attack scenarios, mitigations, and security boundaries ([THREAT_MODEL.md](THREAT_MODEL.md))
* **🚑 Recovery Guide** — Emergency procedures for all failure scenarios ([RECOVERY.md](RECOVERY.md))
* **📦 Dependabot Integration** — Weekly automated dependency vulnerability scanning
* **🔍 Enhanced CI Scanning** — Safety dependency scanner added to security workflow
* **📊 Security Metrics** — 0 HIGH severity issues maintained, all 7 audit items addressed

**Security Achievement:** Comprehensive threat model, automated scanning, and emergency recovery procedures!

### 🛡️ v1.1.4 Security Hardening
* **🛡️ Tarfile Path Traversal Fixed** — Prevents malicious archives from writing outside target directory (CVE-2007-4559)
* **🔐 URL Scheme Validation** — Restricts all URL operations to HTTPS only, prevents downgrade attacks
* **📦 Dependency Security** — GitPython pinned to v3.1.43, eliminates 6 known vulnerabilities
* **🤖 Automated Security Scanning** — Bandit and Safety integrated with GitHub Actions
* **📋 Security Policy** — Professional vulnerability reporting process (48-hour response time)
* **📊 Security Metrics** — 0 HIGH severity issues, all dependencies secured
* **📝 Security Changelog** — Complete audit trail of all security improvements
* **⚙️ CodeQL Analysis** — Semantic code analysis detects vulnerabilities automatically

### 🐛 v1.1.3 Bug Fixes
* **🔧 Fixed Directory Persistence** — Chained commands now correctly persist directory changes
* **⏱️ Fixed Interactive Timeouts** — Interactive commands like `claude` no longer timeout
* **📦 Fixed Pip Install Warnings** — Automatic handling of externally-managed Python environments
* **➕ Enhanced Navigation** — Support for custom project directory paths in `go` command
* **🎯 180s Timeout for Non-Interactive** — Non-interactive commands timeout after 3 minutes (prevents hangs)

### 🔗 v1.1.2 Features
* **🔗 Command Chaining** — Chain commands with `>>>` operator: `go downloads >>> ls >>> echo "done"`
* **🔄 Command Composability** — CCMD commands can call other CCMD commands
* **🎯 Smart Directory Chaining** — Directory changes persist through command chains
* **🛡️ Enhanced Security** — Context-aware validation, expanded pattern detection (40+ patterns)
* **💀 Process Management** — `kap` kills all processes (with confirmation), `kp` kills by name
* **🔐 bcrypt Fallback** — PBKDF2-HMAC-SHA256 fallback if bcrypt unavailable
* **🔒 Type Enforcement** — Custom commands cannot abuse privileged types

**Example:** `ccmd add` → name: `devwork` → command: `go projects >>> ls >>> echo "Ready to code!"`

### 🔐 v1.1.1 Security Features
* **🔒 Master Password System** — Protect sensitive commands with bcrypt-hashed passwords
* **🛡️ Command Injection Prevention** — Automatic blocking of dangerous command patterns
* **🔐 SSH Key Validation** — Verify key permissions (0600) before use
* **🔍 Sensitive Command Detection** — Auto-detect and protect sudo, ssh, AWS commands
* **📁 Atomic File Operations** — Safe, corruption-proof file writes
* **🎯 Intelligent Auto-Locator** — No more path issues, works anywhere
* **📊 Audit Logging** — Track all authentication attempts
* **⚡ Security Cache** — 5-minute authentication window for convenience

**New Commands:** `init`, `debug`, `sudo`, `change-password`, `reset-password`, `kap`, `kp`

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

* **[🔐 Security Policy](SECURITY.md)** — **READ THIS FIRST!** Vulnerability reporting and security measures
* **[📋 Security Changelog](SECURITY_CHANGELOG.md)** — Complete audit trail of security improvements
* **[🤖 Claude AI Security Audit](SECURITY_AUDIT_CLAUDE.md)** — Professional AI security scan (Score: 7.8/10 - GOOD)
* **[🛡️ Threat Model](THREAT_MODEL.md)** — Complete attack scenarios and mitigations
* **[🚑 Recovery Guide](RECOVERY.md)** — Emergency recovery procedures for all platforms
* **[📋 Release Notes v1.1.4](RELEASE_NOTES_v1.1.4.md)** — Latest security hardening release
* **[📋 Release Notes v1.1.3](RELEASE_NOTES_v1.1.3.md)** — Bug fixes and improvements
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
* pip (usually included with Python)

### Method 1: Install from PyPI (Recommended) ⭐

**The easiest way to install CCMD:**

```bash
pip install ccmd
```

That's it! CCMD is now available as the `ccmd` command globally.

**Test installation:**
```bash
ccmd --version
ccmd --list
```

**Note:** PyPI installation provides the CCMD package but you may still need to run shell integration for full functionality:

```bash
ccmd --install  # Sets up shell integration (one-time setup)
```

### Method 2: Install from GitHub (For Development)

For users who want the latest development version or want to contribute:

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

### Method 3: Download Release ZIP (Offline Install)

If you don't have pip or git access:

1. **Download the latest release:**
   - Visit: https://github.com/Wisyle/ccmd/releases/latest
   - Download **Source code (zip)** under Assets
   - Or direct download: https://github.com/Wisyle/ccmd/archive/refs/tags/v1.1.4.zip

2. **Extract and install:**
   ```bash
   # Linux/macOS/WSL:
   cd /path/to/ccmd
   bash setup.sh
   source ~/.bashrc

   # Windows PowerShell:
   cd C:\path\to\ccmd
   .\setup.ps1
   . $PROFILE
   ```

### Verify Installation

After installation, test that CCMD is working:

```bash
# Check system status
ccmd --check

# List available commands
ccmd --list

# Test a command
go home
```

### Update CCMD

**If installed via PyPI (recommended):**
```bash
pip install --upgrade ccmd
```

**If installed via Git:**
```bash
cd /path/to/ccmd
git pull origin ccmd
python3 run.py --install
```

**If installed via ZIP:**
- Download the latest version from PyPI: `pip install --upgrade ccmd`
- Or download latest ZIP and reinstall

### Uninstall

**If installed via PyPI:**
```bash
pip uninstall ccmd
ccmd --restore  # Optional: restore shell config
```

**If installed via Git/ZIP:**
```bash
python3 run.py --restore  # Removes shell integration
```

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

### Security Score: 7.8/10 (GOOD) ✅

CCMD has been professionally audited using both **Bandit static analysis** and **Claude AI security scanning**. See [SECURITY_AUDIT_CLAUDE.md](SECURITY_AUDIT_CLAUDE.md) for the complete AI security audit report.

**Scan Results:**
* ✅ **0 HIGH severity issues** (Bandit)
* ✅ **0 critical vulnerabilities** (Claude AI)
* ✅ **All dependencies secured** (Safety + Dependabot)
* ✅ **Comprehensive threat model documented**

### Security Comparison vs Similar Tools

CCMD beats oh-my-zsh and bash-it in **ALL security categories**:

| Security Feature | CCMD | oh-my-zsh | bash-it | Verdict |
|-----------------|------|-----------|---------|---------|
| **Command Injection Protection** | ✅ Strong (40+ patterns) | ⚠️ Basic | ⚠️ Basic | **CCMD Best** |
| **Password Protection** | ✅ Yes (bcrypt) | ❌ No | ❌ No | **CCMD Best** |
| **Atomic Shell Writes** | ✅ Yes (v1.1.5) | ❌ No | ❌ No | **CCMD Best** |
| **Backup/Restore** | ✅ Built-in | ⚠️ Manual | ⚠️ Manual | **CCMD Best** |
| **Security Documentation** | ✅ Comprehensive | ⚠️ Limited | ⚠️ Limited | **CCMD Best** |
| **Dependency Scanning** | ✅ Automated (CI/CD) | ❌ No | ❌ No | **CCMD Best** |
| **Cross-Platform Support** | ✅ Win/Linux/Mac | ❌ Unix only | ❌ Unix only | **CCMD Best** |
| **Threat Model** | ✅ Documented | ❌ No | ❌ No | **CCMD Best** |

### Security Features

* ✅ **Backups** created automatically before modifying any shell files
* ✅ **Rollback** available anytime with `--restore`
* ✅ **SSH keys** are never stored or transmitted
* ✅ **Safe execution** via subprocess calls, never `eval`
* ✅ **Command validation** with 40+ dangerous pattern detection
* ✅ **Master password** protection for sensitive commands
* ✅ **Atomic writes** prevent shell config corruption
* ✅ **Automated scanning** with Bandit, Safety, and CodeQL

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

