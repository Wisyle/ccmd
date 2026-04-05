# ccmd

**Stop memorizing commands. Start commanding naturally.**

[![PyPI](https://img.shields.io/pypi/v/ccmd.svg?label=PyPI&color=black)](https://pypi.org/project/ccmd/)
[![Downloads](https://img.shields.io/pypi/dm/ccmd.svg?color=black)](https://pypi.org/project/ccmd/)
[![License](https://img.shields.io/badge/license-MIT-black.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-black.svg)](https://www.python.org/)
[![Security](https://img.shields.io/badge/security-audited-black.svg)](security/)

ccmd is a cross-platform terminal command manager. Define short, intuitive aliases for the commands you type every day — then just type them.

Works on **Linux**, **Windows PowerShell**, and **WSL**.

---

## Install

```bash
pip install ccmd
ccmd --install   # one-time shell integration
```

---

## The idea

Instead of this:

```bash
cd ~/projects/myapp && git add . && git commit -m "update" && git push
```

You write this:

```bash
push
```

ccmd replaces long, forgettable terminal syntax with commands you define yourself — stored in YAML, backed up automatically, and safe to roll back.

---

## What you get out of the box

| Command | What it does |
|---------|-------------|
| `go <dir>` | Jump to any directory by name — searches your entire system |
| `push` | Interactive git add, commit, and push in one command |
| `cpu` | Live CPU usage |
| `mem` | Memory usage |
| `proc` | Running processes |
| `add` | Create a custom command interactively |
| `remove` | Remove a custom command |
| `list` | View and toggle commands on/off |
| `reload` | Reload config without reinstalling |
| `restore` | Roll back shell changes |

---

## Custom commands

```bash
ccmd add
```

You'll be prompted for a name, a shell command, and whether it needs a password. That's it. Your custom commands live in `~/.ccmd/custom_commands.yaml` and survive all future updates.

**Command chaining** — use `>>>` to chain multiple commands under one name:

```bash
# Define once
ccmd add
> name: devstart
> command: go projects >>> ls >>> echo "ready"

# Then just type:
devstart
```

---

## Real-world example

```bash
# Instead of this every morning:
cd ~/work/api && git pull && docker compose up -d && echo "Running"

# Define it once:
ccmd add
> name: work
> command: go api >>> git pull >>> docker compose up -d

# Then just type:
work
```

---

## Security

ccmd sits between you and your shell. It was built with that in mind.

- Atomic shell config writes — no corruption on crash
- 40+ command injection patterns blocked automatically
- Optional master password (bcrypt) for sensitive commands
- Automatic backup before every shell modification
- Full rollback with `ccmd --restore` at any time
- Audited with Bandit, Safety, and CodeQL — **0 HIGH severity issues**

Full threat model: [THREAT_MODEL.md](security/THREAT_MODEL.md)

---

## Update

```bash
pip install --upgrade ccmd
```

## Uninstall

```bash
ccmd --restore   # removes shell integration
pip uninstall ccmd
```

---

## License

MIT — free to use, fork, and modify.

---

Built by [De Catalyst](https://decatalyst.com) · [@iamdecatalyst](https://x.com/iamdecatalyst)
