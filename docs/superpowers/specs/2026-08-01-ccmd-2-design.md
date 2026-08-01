# ccmd 2.0 — Agentic Project Hub (design)

**Status:** draft for user review  
**Date:** 2026-08-01  
**Package:** `ccmd` (PyPI name kept)  
**Approach:** greenfield rewrite inside the same repo (Approach A)

---

## 1. Product

ccmd 2.0 is a local **control plane** for coding agents.

You open a project, pick an agent (Claude, Grok, Codex, Cursor, Goose, Aider, ChatGPT browser), apply PATH / aliases / env / SSH profile, and launch. Agents can drive the same actions through an MCP server.

It is not a coding agent. It is not a full terminal. It does not replace Claude Code, Codex, or Grok Build. It prepares the room and opens the door.

### Locked decisions

| Decision | Choice |
|----------|--------|
| Empty `ccmd` | Project hub TUI |
| Brand | Keep `ccmd`, version 2.0 |
| Legacy | Migrate `~/.ccmd` customs + shortcuts into hub |
| Agents (v1) | Claude, Grok, Codex, Cursor Agent, Goose, Aider, ChatGPT (browser) |
| v1 extras | MCP + sessions + CLI + SSH profiles + alias/PATH manager |
| Build | Greenfield Python package; Textual TUI |

### Non-goals (v1)

- Built-in coding agent / LLM chat loop
- Replacing Warp / full terminal emulator
- Multi-agent arena / cost analytics
- Cloud sync of projects
- Per-command shell functions + `eval cd` protocol (deleted by design)
- Web search inside the hub (v1.1+)
- Windows CMD.exe integration (PowerShell later; Linux/macOS/WSL first)

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Surfaces                                                      │
│  Textual TUI  ·  CLI (ccmd open …)  ·  MCP server (stdio)    │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
                  Hub Core (asyncio)
                  ProjectRegistry · AgentCatalog · ProfileEngine
                  SessionManager · AliasStore · PathEnv · SSH
                  Policy · AuditLog · Migrator
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
    Env / dotenv       Agent adapters       SSH (system ssh)
    PATH / aliases     launch + detect      host profiles
```

### Package layout (target)

```
ccmd/
  __init__.py              # version 2.0.0
  __main__.py              # python -m ccmd
  cli.py                   # argparse: open, list, mcp, migrate, …
  tui/
    app.py                 # Textual App root
    screens/
      hub.py               # project picker (default)
      agents.py            # agent picker with logos
      sessions.py          # live/session history
      ssh.py               # SSH host manager
      aliases.py           # alias + PATH manager
      project_edit.py      # create/edit project
    widgets/
      logo_grid.py
      spinner.py
      ascii_banner.py
      project_list.py
    theme.py               # CSS + color tokens
    ascii.py               # banners, frames, agent glyphs
  core/
    projects.py
    agents/
      base.py              # AgentAdapter protocol
      claude.py
      grok.py
      codex.py
      cursor.py
      goose.py
      aider.py
      chatgpt.py
    profiles.py            # env, PATH, aliases, dotenv
    sessions.py
    ssh.py
    launcher.py
    migrate.py             # 1.x → 2.0
    policy.py
    audit.py
  mcp/
    server.py              # stdio MCP tools
  config/
    schema.py
    paths.py               # ~/.ccmd layout
```

### Data homes

| Path | Role |
|------|------|
| `~/.ccmd/config.toml` | Global settings, theme, scan roots |
| `~/.ccmd/projects/*.yaml` | Project registry |
| `~/.ccmd/ssh/hosts.yaml` | SSH host profiles (no private key material) |
| `~/.ccmd/aliases.yaml` | Managed aliases + PATH prepends |
| `~/.ccmd/sessions.jsonl` | Append-only launch log |
| `~/.ccmd/audit.jsonl` | Sensitive actions |
| `~/.ccmd/legacy/` | Backed-up 1.x files after migration |
| `<project>/.ccmd.yaml` | Optional project-local overrides |
| `<project>/AGENTS.md` / `CLAUDE.md` | Unchanged; agents read these |

Legacy still read once: `custom_commands.yaml`, `shortcuts.yaml`, `ccmd.key` (optional re-bind).

---

## 3. Visual design — vibrant ASCII TUI

Premium does not mean muted gray. The default theme is **high-chroma terminal**: cyan / magenta / green on near-black, with agent brand accents on logos only. Reduced-motion and monochrome themes exist as overrides.

### 3.1 Design principles

1. **ASCII + Unicode box drawing first** — works in plain xterm; Nerd Font glyphs are progressive enhancement.
2. **Loaders everywhere async happens** — never a frozen blank screen.
3. **Keyboard-first** — lazygit density; mouse optional.
4. **Frames and banners** — every major screen has a short ASCII header so the product feels owned, not generic Textual demo.
5. **Agent logos** as colored ASCII blocks (fallback) or Nerd Font / kitty image when available.

### 3.2 Color tokens (`theme.py`)

| Token | Default (truecolor) | Use |
|-------|---------------------|-----|
| `bg` | `#0a0a0f` | App background |
| `panel` | `#12121a` | Cards / lists |
| `border` | `#2a2a40` | Idle borders |
| `border_focus` | `#00ffc8` | Focused panel |
| `text` | `#e8e8f0` | Body |
| `muted` | `#6a6a80` | Hints, meta |
| `accent` | `#00ffc8` | Primary accent (cyan) |
| `accent_2` | `#c84bff` | Magenta secondary |
| `accent_3` | `#39ff14` | Success / ready |
| `warn` | `#ffcc00` | Missing agent / caution |
| `danger` | `#ff3355` | Destructive |
| `claude` | `#d97757` | Agent accent |
| `grok` | `#ffffff` | Agent accent |
| `codex` | `#10a37f` | Agent accent |
| `cursor` | `#7c3aed` | Agent accent |
| `goose` | `#f59e0b` | Agent accent |
| `aider` | `#38bdf8` | Agent accent |
| `chatgpt` | `#74aa9c` | Agent accent |

CSS lives in Textual `CSS` classes; no external stylesheet file required for v1 (inline module CSS is fine).

### 3.3 ASCII banner (hub)

```
   ██████╗ ██████╗███╗   ███╗██████╗
  ██╔════╝██╔════╝████╗ ████║██╔══██╗
  ██║     ██║     ██╔████╔██║██║  ██║
  ██║     ██║     ██║╚██╔╝██║██║  ██║
  ╚██████╗╚██████╗██║ ╚═╝ ██║██████╔╝
   ╚═════╝ ╚═════╝╚═╝     ╚═╝╚═════╝
        project hub  ·  v2.0
```

Compact mode (narrow terminals): single-line `◇ ccmd · project hub` with cyan diamond.

### 3.4 Loaders (required)

Async work always shows a named spinner state. Implement as Textual widgets on top of Rich spinners / custom frames.

| Context | Loader | Notes |
|---------|--------|-------|
| App boot / migrate | orbit ring style multi-dot | “loading registry…” |
| Project scan | bar + path tick | cancelable |
| Agent detect | per-logo pulse | gray → color when found |
| Launch handoff | full-width status line | “handing off to claude…” then exit or detach |
| SSH connect | dots + host | timeout message |
| MCP cold start | small corner spinner | non-blocking |

Custom spinner frames (example):

```
⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏     # braille (default)
◐ ◓ ◑ ◒                     # reduced
[■□□□□] … [■■■■■]           # bar for scans
```

Respect `prefers-reduced-motion` / config `ui.motion = minimal|full`.

### 3.5 Screens (chrome)

**Hub (default)**

```
┌─ ccmd ────────────────────────────────────────── sessions 3 ─┐
│  ██████╗ … banner …                                          │
│  filter: ▌flow_                                              │
│  ┌ projects ──────────────┐  ┌ detail ─────────────────────┐ │
│  │ › vylth-flow     ★ claude│  │ path  /mnt/vylth/vylth-flow│ │
│  │   decatalyst       grok │  │ agent claude (default)     │ │
│  │   northstar      codex  │  │ ssh   —                    │ │
│  │   beacon         cursor │  │ env   .env.local           │ │
│  └────────────────────────┘  └─────────────────────────────┘ │
│  ↵ open · a agents · n new · s sessions · h ssh · / aliases  │
└──────────────────────────────────────────────────────────────┘
```

**Agent picker**

Grid of ASCII/logo tiles. Installed = brand color + check. Missing = muted + “install hint” on focus. Keys: arrows, enter, `i` show install command.

**Sessions**

Table: time · project · agent · pid/status · attach/kill.

**SSH / aliases**

Form-style panels with focused borders; confirm dialogs for destructive ops use danger color + typed confirm for host delete.

### 3.6 Sound / emoji

No emoji in chrome. Nerd Font optional. No sound.

---

## 4. Project model

```yaml
# ~/.ccmd/projects/vylth-flow.yaml
id: vylth-flow
name: Vylth Flow
path: /mnt/vylth/vylth-flow
default_agent: claude
tags: [vylth, prod]
env_files: [.env, .env.local]
path_prepend: []
aliases: []          # names from aliases.yaml to apply on launch
ssh_host: null       # optional host id
mcp_packs: []        # v1.1
created_at: …
updated_at: …
last_opened_at: …
```

### Discovery

1. Migration of 1.x `go` shortcuts + custom `go X >>> agent` macros  
2. Manual create in TUI / `ccmd project add`  
3. Scan roots from config (default: `~/`, `/mnt/vylth`, common dev dirs) depth-limited  
4. Optional import of zoxide database if present  

### Migration rules (1.x → 2.0)

| 1.x source | 2.0 result |
|------------|------------|
| `shortcuts.yaml` go map | projects with path + id |
| `go name >>> claude` customs | project + `default_agent: claude` |
| `go name >>> cursor-agent` | `default_agent: cursor` |
| bare shell customs | `aliases.yaml` entries (managed) |
| `require_password` flags | policy notes; master password optional re-init |
| shell RC ccmd functions | **removed** on `ccmd migrate --apply`; backup RC first |

First run: detect 1.x files → spinner → preview plan → user confirms → write new registry → backup legacy to `~/.ccmd/legacy/`.

---

## 5. Agents

### Adapter protocol

```python
class AgentAdapter(Protocol):
    id: str
    display_name: str
    brand_color: str
    ascii_logo: str          # small multi-line glyph
    binaries: list[str]      # which() candidates

    def is_installed(self) -> bool: ...
    def version(self) -> str | None: ...
    def install_hint(self) -> str: ...
    def build_command(self, ctx: LaunchContext) -> list[str]: ...
```

### LaunchContext

- `cwd`, `env` (merged), `extra_args`, `initial_prompt`, `session_label`
- `permission_mode` / sandbox hints when agent supports them
- `detach` (tmux if available, else background process)

### v1 adapters

| id | Binary | Notes |
|----|--------|-------|
| `claude` | `claude` | Primary; pass through argv |
| `grok` | `grok` | Grok Build |
| `codex` | `codex` | OpenAI Codex CLI |
| `cursor` | `cursor-agent` | Cursor agent CLI |
| `goose` | `goose` | Block Goose |
| `aider` | `aider` | pip tool |
| `chatgpt` | n/a | Open browser URL / profile; no cwd agent |

Missing agents stay visible, muted, with copyable install hint.

### Launch path

1. Resolve project path (canonicalize; must exist)  
2. Load env files (no secret echo to TUI logs)  
3. Apply PATH prepends + aliases as env for child only (not global shell)  
4. Optional SSH pre-step if profile requires tunnel  
5. Build argv via adapter  
6. Write session jsonl row  
7. `os.execvpe` when replacing TTY, or subprocess + tmux when detach  

Default: replace current TUI process so the agent owns the terminal (clean handoff). Detach mode is opt-in (`d` key or `--detach`).

---

## 6. SSH

Profiles in `~/.ccmd/ssh/hosts.yaml`:

```yaml
hosts:
  sage:
    host: 89.117.52.141
    user: decatalyst
    port: 22
    identity_file: ~/.ssh/id_ed25519   # path only
    jump: null
    tags: [prod]
```

Features v1:

- List / add / edit / delete hosts in TUI  
- Connect: spawn `ssh user@host` (arg list, never shell-interpolated string)  
- Import from `~/.ssh/config` Host entries (read-only parse)  
- Import known bash aliases that match `ssh user@host` patterns (user confirms)  
- Optional “before launch” tunnel: local port forward defined on project  

Never store private key contents. Never print key material in MCP responses.

---

## 7. Alias and PATH manager

`~/.ccmd/aliases.yaml`:

```yaml
aliases:
  ll: "ls -alF"
  sage: "ssh decatalyst@89.117.52.141"   # prefer SSH profile link instead
path_prepend:
  - ~/.local/bin
  - ~/.npm-global/bin
```

Behavior:

- TUI editor for aliases and PATH entries  
- Import from `~/.bashrc` / `~/.zshrc` alias lines (parse, preview, multi-select)  
- On project launch: apply selected aliases as shell functions **only in the child environment** via a generated ephemeral wrapper script with mode `0700`, or export equivalent env for tools that don't need aliases  
- Optional: write a single managed block to shell RC:

  ```bash
  # >>> ccmd 2.0 >>>
  # managed — do not edit; use `ccmd` aliases screen
  # <<< ccmd 2.0 <<<
  ```

  Atomic write + backup (reuse the good idea from 1.x rollback). One block, not N functions.

---

## 8. CLI surface

```
ccmd                     # TUI hub
ccmd open <project> [--agent NAME] [--prompt TEXT] [--detach]
ccmd list                # projects
ccmd agents              # detect installed
ccmd sessions            # list / attach / kill
ccmd ssh [list|add|connect]
ccmd aliases [list|import]
ccmd migrate [--apply]   # 1.x → 2.0
ccmd mcp                 # stdio MCP server
ccmd doctor              # paths, agents, theme, legacy leftover
ccmd version
```

Scriptable: exit codes 0 ok, 1 user error, 2 system error. JSON optional via `--json` on list/doctor.

---

## 9. MCP server

Transport: **stdio only** in v1 (no remote HTTP).

Tools:

| Tool | Purpose |
|------|---------|
| `projects.list` | id, name, path, default_agent (no secrets) |
| `projects.get` | one project metadata |
| `projects.open` | resolve + return launch plan summary |
| `agents.list` | installed + version |
| `agents.launch` | start agent on project; returns session_id |
| `sessions.list` | ccmd-owned sessions |
| `sessions.kill` | terminate by id |
| `ssh.list` | host ids + hostnames (no keys) |
| `env.describe` | non-secret env plan for a project |

Auth: local process only. Refuse binding TCP in v1.

Generate paste-ready MCP config snippets:

```
~/.ccmd/generated/claude.mcp.json
~/.ccmd/generated/codex.mcp.toml
```

`ccmd doctor` prints how to wire each agent.

---

## 10. Security

### Hard rules

1. No `shell=True` with user/agent-controlled strings.  
2. No `eval` of command stdout for `cd`. Navigation is in-process `os.chdir` or launch `cwd=`.  
3. Subprocess always argv lists.  
4. Project paths resolved with `.resolve()`; optional allowlist roots in config.  
5. Secrets from env files never written to audit/MCP payloads (redact `*_KEY`, `*_TOKEN`, `PASSWORD`).  
6. SSH: IdentityFile paths only; use system `ssh`.  
7. Destructive TUI actions need confirm; host delete needs re-type id.  
8. Atomic writes + backups for any RC mutation.  
9. Drop 1.x auth bypass (`return True` if bcrypt missing). If password gate enabled, missing crypto lib is hard fail.  
10. Drop nuclear `kap` default.  

### Trust model (honest)

ccmd runs as the user. It is not a sandbox. It reduces accidents and centralizes launch policy; it does not stop a determined local attacker with your uid.

### Optional master password (v1.1 if time-boxed out of v1)

Gate: export aliases to RC, delete SSH host, apply migrate. Prefer OS keyring over home-rolled hash file.

---

## 11. Tech stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.11+ (drop 3.7) |
| TUI | Textual |
| Markup / non-TUI output | Rich |
| Config | TOML + YAML (PyYAML) |
| MCP | official MCP Python SDK |
| Fuzzy | rapidfuzz (optional fzf shell-out) |
| HTTP | httpx only if needed later (not v1 core) |
| Packaging | pyproject / hatchling or setuptools; entry `ccmd` |
| Tests | pytest + pytest-asyncio; Textual pilot tests for critical screens |
| Lint | ruff |
| Security scan | bandit in CI; no blanket skip of shell rules without comment |

### Dependencies (v1 intent)

- textual, rich, pyyaml, rapidfuzz, mcp, tomli/tomllib  
- Remove: GitPython pin for push (revisit as optional recipe later), questionary  

---

## 12. Sessions

Each launch appends:

```json
{"ts":"...","id":"...","project":"vylth-flow","agent":"claude","pid":1234,"cwd":"...","detach":false}
```

TUI sessions screen:

- List recent  
- Kill process group if still alive  
- Attach only if detach used tmux (`tmux attach -t ccmd-<id>`)  

---

## 13. v1 ship checklist (feature freeze)

Must ship:

- [ ] Greenfield package layout + `ccmd` entry  
- [ ] Vibrant Textual theme + ASCII banners + loaders  
- [ ] Project registry CRUD + fuzzy filter  
- [ ] Agent grid (7) detect + launch handoff  
- [ ] Migrate 1.x config  
- [ ] Profile: env files + PATH prepend + alias apply on launch  
- [ ] SSH host manager + connect + ssh-config import  
- [ ] Alias/PATH manager + bashrc alias import  
- [ ] Sessions list/kill  
- [ ] CLI parity for open/list/agents/migrate/doctor  
- [ ] MCP stdio server (list/open/launch/sessions/ssh.list)  
- [ ] Atomic RC managed block (optional export)  
- [ ] Tests: registry, migrate, launcher argv, security (no shell inject), MCP tool smoke  
- [ ] `ccmd doctor`  
- [ ] README rewrite for 2.0  

Explicitly later (v1.1+):

- Web search tool  
- MCP packs marketplace  
- Multi-agent parallel arena  
- Recovery keys / full keyring password UX  
- Windows native polish  
- Single-binary packaging  

---

## 14. Kill list from 1.x

| Kill | Why |
|------|-----|
| Per-command shell functions + eval cd | Injection + maintenance |
| `CCMD_HOME` + run.py install model | Fights pip |
| Regex denylist as primary security | False safety |
| `shell=True` system types for cpu/mem | Use psutil or drop |
| God `main.py` | Split modules |
| Orphan ssh_manager not wired | Replaced by first-class SSH screen |
| `kap` kill-all default | Dangerous |
| Auth bypass without bcrypt | Fail closed |
| GitHub tarball self-update | Use pip/uv |
| Stale docs pile | One README + CHANGELOG + this spec |

Keep: layered config idea, backup/atomic write patterns, `>>>` composition as **recipes** (project launch recipes in v1.1; migrate macros into default_agent + notes for now).

---

## 15. Implementation order

1. Scaffold package + config paths + theme tokens + ASCII banner screen shell  
2. Project registry + migrate importer + hub list/filter  
3. Agent adapters + detect + launch handoff (claude first, then rest)  
4. Loaders + agent logo grid polish  
5. Profiles (env/PATH/aliases) on launch  
6. SSH screen + import  
7. Alias/PATH screen + bashrc import  
8. Sessions  
9. CLI  
10. MCP server  
11. doctor + security tests + README  
12. Local dogfood on real `/mnt/vylth/*` projects  

---

## 16. Success criteria

A stranger can:

1. `pip install ccmd && ccmd`  
2. See a colorful hub, not a blank prompt  
3. Add or import a project in under a minute  
4. Launch Claude (or any installed agent) into that project with one enter  
5. Wire `ccmd mcp` into an agent and list projects from that agent  

You personally can:

1. Run `ccmd migrate --apply` and recover every `go X >>> claude` habit as projects  
2. Drop muscle-memory shell functions without losing sage/SSH shortcuts  
3. Work for hours: hub → agent → return → sessions → next project  

---

## 17. Open points (resolve during build if needed)

- Tmux required for detach, or raw background pid only? **Default: tmux if present, else foreground-only.**  
- Should `push` survive as a built-in recipe? **Optional v1.1; not blocking.**  
- ChatGPT tile: system browser vs printed URL only? **`webbrowser.open` with project path in query if useful; else open chat.openai.com.**  

---

*End of design. Approve or annotate before implementation plan.*
