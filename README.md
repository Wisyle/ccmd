# ccmd 2.0 — Agentic Project Hub

Pick a project. Pick an agent. Launch.

```
   ██████╗ ██████╗███╗   ███╗██████╗
  ██╔════╝██╔════╝████╗ ████║██╔══██╗
  ██║     ██║     ██╔████╔██║██║  ██║
  ██║     ██║     ██║╚██╔╝██║██║  ██║
  ╚██████╗╚██████╗██║ ╚═╝ ██║██████╔╝
   ╚═════╝ ╚═════╝╚═╝     ╚═╝╚═════╝
        project hub  ·  v2.0
```

ccmd is a local control plane for coding agents — Claude Code, Grok Build, Codex, Cursor Agent, Goose, Aider, and ChatGPT (browser). It is not another coding agent. It prepares the room and opens the door.

## Install

```bash
pip install -e .
# or: pip install ccmd  (when published)
ccmd doctor
ccmd migrate --apply   # import 1.x shortcuts + custom commands
ccmd                   # vibrant TUI
```

Python 3.11+.

## Daily use

| Command | What |
|---------|------|
| `ccmd` | Project hub TUI |
| `ccmd open flow --agent claude` | Headless launch |
| `ccmd list` | Projects |
| `ccmd agents` | Detect installed agents |
| `ccmd sessions` | Launch history / kill |
| `ccmd ssh import` | Pull hosts from `~/.ssh/config` |
| `ccmd aliases import` | Pull aliases from `~/.bashrc` |
| `ccmd mcp` | Stdio MCP tool server |
| `ccmd doctor` | Paths + agent diagnostics |

### TUI keys

`↵` open · `a` agents · `n` new project · `s` sessions · `h` ssh · `/` filter · `q` quit

## Config

| Path | Role |
|------|------|
| `~/.ccmd/config.toml` | Global |
| `~/.ccmd/projects/*.yaml` | Registry |
| `~/.ccmd/ssh/hosts.yaml` | SSH profiles |
| `~/.ccmd/aliases.yaml` | Aliases + PATH |
| `~/.ccmd/sessions.jsonl` | Sessions |

Override home with `CCMD_HOME`.

## MCP

```bash
ccmd mcp
```

Tools: `projects.list`, `projects.get`, `agents.list`, `agents.launch`, `sessions.list`, `sessions.kill`, `ssh.list`.

NDJSON on stdio (works without the optional `mcp` package).

## Security

- No shell-function-per-command / `eval cd` (removed from 1.x)
- Subprocess argv lists only
- SSH IdentityFile paths only — never private key contents
- Env file secrets redacted from MCP payloads
- Atomic config writes mode `0600`

## Migrate from 1.x

```bash
ccmd migrate          # dry-run
ccmd migrate --apply  # write projects + aliases, backup to ~/.ccmd/legacy/
```

Your `go X >>> claude` customs become projects with `default_agent: claude`.

## Dev

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
ccmd doctor
```

## License

MIT
