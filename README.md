# ccmd
CCMD — A universal command enhancer that replaces clunky terminal syntax with clean, human-friendly commands. Cross-platform, extensible, rollback-safe. Turn cd ~/Downloads &amp;&amp; git add . into simply go downloads and push.
Got it. Here’s your **final polished `README.md`**, branded, formatted, and ready for your GitHub repo under **Wisyle**. I’ve adjusted it so commands don’t require the `ccmd` prefix — users just type `go`, `push`, etc. The footer includes your contact and credits exactly as you requested.

---


# 🧠 CCMD — Custom Command Manager

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

* Python **3.9+**
* Git

### Quick Install

```bash
git clone https://github.com/Wisyle/ccmd.git
cd ccmd
python run.py --install
```

### Uninstall / Rollback

```bash
python run.py --restore
```

### Update

```bash
python run.py --update
```

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
