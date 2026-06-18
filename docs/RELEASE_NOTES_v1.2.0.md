# CCMD v1.2.0 Release Notes

**Release Date:** June 2026
**Type:** Feature Release — "Open-Source Ready"

---

## Summary

v1.2.0 makes CCMD genuinely shareable. Every hardcoded personal path is gone, users register their own directory shortcuts through a first-run wizard, and the project ships its first test suite. This is the release to build a community on.

---

## ✨ New Features

### 1. First-Run Setup Wizard

Installing CCMD now drops you into an interactive setup wizard (only when stdout is a TTY — scripted/CI installs are left alone):

```bash
$ ccmd --install
# ... shell integration written ...

=== CCMD Setup ===
Welcome to CCMD! Let's get you set up.

Register your directory shortcuts
These power the go command — e.g. go projects jumps to that folder.
Shortcut name (blank to finish): projects
Directory path for 'projects' (e.g. ~/projects/myapp): ~/code/projects
✓ Added 'projects' → /home/user/code/projects

Set a master password now? (y/N): y
...
✓ Setup complete!
```

Re-run it anytime with **`ccmd setup`** or **`ccmd --setup`**.

### 2. User-Defined `go` Shortcuts (`~/.ccmd/shortcuts.yaml`)

A new user-owned config layer — your shortcuts live separately from the shipped defaults and survive every `ccmd update`:

```yaml
# ~/.ccmd/shortcuts.yaml
projects: /home/user/code/projects
work: /home/user/work
docs:   /home/user/Documents/writing
```

Then:

```bash
$ go projects     # → cd /home/user/code/projects
$ go work         # → cd /home/user/work
```

User shortcuts merge with the built-in ones (`downloads`, `documents`, `desktop`, `home`). On a name collision, **your shortcut wins**.

### 3. Test Suite

The project's first committed tests — 50 of them, all passing:

```bash
pip install -e ".[dev]"
pytest -q          # 50 passed
```

Covers security validation (13 injection payloads blocked), the command registry's three-layer merge, and the parser's `go` resolution.

---

## 🔧 Changes & Fixes

### De-personalization (the big OSS blocker — fixed)

Before v1.2.0, CCMD shipped with the maintainer's personal directory paths baked in:

- `commands.yaml` had `lhs`, `lha` shortcuts pointing at `/mnt/c/Users/rober/targlobal/...`
- `search_directory()` hard-coded `C:\Users\rober\...` and `/mnt/c/Users/rober/...` paths

**Now:** directory search derives standard user folders (`~/Downloads`, `~/Documents`, `~/Desktop`, `~/Projects`, `~/Code`, `~/Developer`) from `$HOME`. Zero personal paths remain anywhere in the codebase.

### Repo Hygiene

- **Untracked `__pycache__/`** — the compiled `.pyc` files that were committed in early history are removed from tracking (`.gitignore` already covered them; they were just never `git rm`'d).
- **`.gitattributes`** added with `* text=auto eol=lf` to normalize line endings across Windows/Unix contributors.

### Command Consistency

- The `sudo` command's `require_password` flag is back to `true`, matching its "password protected" description. *(Note: this was never a security hole — CCMD's auto-detector independently flags any command containing `sudo` for password gating. This is a documentation-consistency fix only.)*

### New `setup` Command

Added to the command registry and dispatch:

```bash
ccmd setup     # interactive wizard
ccmd --setup   # same, via flag
```

---

## 📦 Upgrade Instructions

### From PyPI
```bash
pip install --upgrade ccmd
ccmd --install          # re-run to trigger the setup wizard
```

### From Source
```bash
git pull origin ccmd
python run.py --install
source ~/.bashrc        # or . $PROFILE on Windows
```

---

## ⚠️ Breaking Changes

**None for existing users.** Behavior notes:

- If you previously hand-edited `commands.yaml` to add personal `go` shortcuts, they still work — but the recommended path is now `~/.ccmd/shortcuts.yaml` (or `ccmd setup`), so they survive updates.
- The built-in `go` shortcuts `lhs` and `lha` (which pointed at the maintainer's machine) are removed. No real user had working versions of these anyway.

---

## 🗂 Files Changed

| Area | Files |
|------|-------|
| Setup wizard | `ccmd/cli/setup.py` (new), `ccmd/cli/install.py`, `ccmd/cli/main.py` |
| User shortcuts | `ccmd/core/registry.py`, `commands.yaml` |
| De-personalization | `ccmd/cli/main.py`, `ccmd/core/executor.py`, `commands.yaml` |
| Tests (new) | `tests/conftest.py`, `tests/test_security.py`, `tests/test_registry.py`, `tests/test_parser.py` |
| Hygiene | `.gitattributes` (new), `.gitignore`, `docs/` reorg |

---

## Credits

- **Developer:** De Catalyst (@Wisyle)
- **License:** MIT

---

## Links

- **GitHub:** https://github.com/Wisyle/ccmd/releases/tag/v1.2.0
- **PyPI:** https://pypi.org/project/ccmd/
- **Security Policy:** https://github.com/Wisyle/ccmd/security
