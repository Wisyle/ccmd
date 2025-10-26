# 🧠 CCMD — Custom Command Manager

[![Latest Release](https://img.shields.io/github/v/release/Wisyle/ccmd?label=Download&color=brightgreen)](https://github.com/Wisyle/ccmd/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

> **Cross-platform command enhancer for humans.**
> Replace long, repetitive terminal syntax with short, intuitive commands.
> Works on **Linux**, **macOS**, **Windows**, **PowerShell**, and **WSL** — safe, rollback-ready, and open source.

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

* **Cross-Platform Support** — Bash, Zsh, Fish, PowerShell, CMD, and WSL.
* **Natural Commands** — No prefixes; just type `go`, `push`, `cpu`, etc.
* **Interactive Command Editor** — Add or edit commands right from your terminal.
* **Auto Git Integration** — Add, commit, and push automatically.
* **System Insights** — Monitor CPU, memory, and processes.
* **SSH Shortcuts** — One-command access to your saved servers.
* **Safe Rollback** — Backs up your shell configuration before any changes.
* **Extensible Design** — Add plugins or Python functions as custom commands.

---

## 📚 Documentation

For detailed guides and technical documentation, see:

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
   - Or direct download: https://github.com/Wisyle/ccmd/archive/refs/tags/v1.0.3.zip

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

| Command               | Description                    | Action                               |
| --------------------- | ------------------------------ | ------------------------------------ |
| `go <dir>`            | Navigate to a directory        | `cd ~/Downloads`                     |
| `push`                | Auto git add, commit, and push | Auto commit message based on changes |
| `cpu`                 | Show CPU stats                 | Python system monitor                |
| `mem`                 | Show memory usage              | Python system monitor                |
| `proc`                | List running processes         | Safe task list                       |
| `kap`                 | Kill all user processes        | Prompts before execution             |
| `ssh`                 | Connect to default server      | Uses saved SSH key                   |
| `addssh <alias> <ip>` | Add new SSH target             | Saves to YAML                        |
| `syscheck`            | Check OS/shell compatibility   | Reports readiness                    |
| `restore`             | Rollback installation          | Restores shell rc/profile            |
| `update`              | Pull latest CCMD version       | Auto git pull                        |

---

## ⚙️ Configuration

All custom commands are stored in:

```
~/.ccmd/commands.yaml
```

Edit manually or use the interactive editor:

```bash
ccmd --edit
```

Each command follows this format:

```yaml
go:
  description: "Navigate to a directory"
  exec: "cd {arg}"

push:
  description: "Auto git add, commit, and push"
  exec: "git add . && git commit -m 'auto: {changes}' && git push"
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

```

---
