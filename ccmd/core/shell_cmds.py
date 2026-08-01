"""Generate per-project shell shortcuts (ana, anac, anag, …).

When a project is registered, users get short commands:

  ana          → ccmd open anastasis          (default agent)
  anac         → ccmd open anastasis --agent claude
  anag         → grok
  anax         → codex
  anau         → cursor
  anao         → goose
  anaa         → aider
  anap         → chatgpt

Functions live in ~/.ccmd/shell_cmds.sh and are sourced from a managed
block in ~/.bashrc / ~/.zshrc. They call `ccmd open` (no eval-cd).
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from ccmd.config.paths import ensure_dirs, generated_dir, home

# Single-letter agent suffixes (c = claude, so cursor uses u)
AGENT_SUFFIX: dict[str, str] = {
    "claude": "c",
    "grok": "g",
    "codex": "x",
    "cursor": "u",
    "goose": "o",
    "aider": "a",
    "chatgpt": "p",
}

# Names we must never generate (shell builtins / common tools)
RESERVED = frozenset(
    {
        "cd",
        "ls",
        "ll",
        "la",
        "pwd",
        "rm",
        "cp",
        "mv",
        "cat",
        "less",
        "more",
        "head",
        "tail",
        "grep",
        "find",
        "which",
        "type",
        "echo",
        "printf",
        "test",
        "true",
        "false",
        "exit",
        "export",
        "source",
        "alias",
        "unalias",
        "bg",
        "fg",
        "jobs",
        "kill",
        "ps",
        "top",
        "htop",
        "ssh",
        "scp",
        "git",
        "vim",
        "nvim",
        "nano",
        "code",
        "cursor",
        "claude",
        "grok",
        "codex",
        "go",
        "node",
        "npm",
        "npx",
        "pip",
        "python",
        "python3",
        "ccmd",
        "sudo",
        "su",
        "man",
        "help",
        "history",
        "clear",
        "reset",
        "time",
        "date",
        "whoami",
        "env",
        "set",
        "unset",
        "pushd",
        "popd",
        "dirs",
        "tmux",
        "screen",
        "docker",
        "make",
        "curl",
        "wget",
        "tar",
        "zip",
        "unzip",
    }
)

MARKER_BEGIN = "# >>> ccmd shell cmds >>>"
MARKER_END = "# <<< ccmd shell cmds <<<"


def shell_cmds_path() -> Path:
    ensure_dirs()
    return home() / "shell_cmds.sh"


def short_candidates(project_id: str, name: str) -> list[str]:
    """Generate preferred short-name candidates for a project."""
    raw = re.sub(r"[^a-z0-9]+", "", (project_id or name).lower())
    if not raw:
        raw = "proj"
    cands: list[str] = []
    # full slug if short enough
    if 2 <= len(raw) <= 12:
        cands.append(raw)
    # progressive prefixes: ana, anas, anast…
    for n in range(3, min(8, len(raw) + 1)):
        cands.append(raw[:n])
    # consonants-only compact form
    cons = re.sub(r"[aeiou]", "", raw)
    if len(cons) >= 3:
        cands.append(cons[:4])
    # first letters of hyphen/underscore parts
    parts = re.split(r"[-_\s]+", project_id or name)
    initials = "".join(p[0] for p in parts if p)[:6].lower()
    if len(initials) >= 2:
        cands.append(re.sub(r"[^a-z0-9]", "", initials))
    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for c in cands:
        if c and c not in seen and c[0].isalpha():
            seen.add(c)
            out.append(c)
    return out or [f"p{raw[:6]}"]


def allocate_shorts(projects: list) -> dict[str, str]:
    """Map project.id → unique short name."""
    used: set[str] = set(RESERVED)
    # honor existing project.short if set and unique
    mapping: dict[str, str] = {}
    for p in projects:
        existing = getattr(p, "short", None) or ""
        existing = re.sub(r"[^a-z0-9]", "", existing.lower())
        if existing and existing not in used and existing[0].isalpha():
            mapping[p.id] = existing
            used.add(existing)
            # also reserve agent variants
            for suf in AGENT_SUFFIX.values():
                used.add(existing + suf)

    for p in projects:
        if p.id in mapping:
            continue
        chosen = None
        for cand in short_candidates(p.id, p.name):
            if cand in used:
                continue
            # agent variants must also be free
            if any((cand + s) in used for s in AGENT_SUFFIX.values()):
                continue
            chosen = cand
            break
        if not chosen:
            # fallback numbered
            base = short_candidates(p.id, p.name)[0][:4]
            n = 2
            while True:
                cand = f"{base}{n}"
                if cand not in used and all(
                    (cand + s) not in used for s in AGENT_SUFFIX.values()
                ):
                    chosen = cand
                    break
                n += 1
        mapping[p.id] = chosen
        used.add(chosen)
        for suf in AGENT_SUFFIX.values():
            used.add(chosen + suf)
    return mapping


def render_shell_cmds(projects: list, shorts: dict[str, str]) -> str:
    """Bash/zsh-compatible function definitions."""
    lines = [
        "#!/usr/bin/env bash",
        "# Auto-generated by ccmd — do not edit by hand.",
        "# Regenerate: ccmd shell regen",
        "#",
        "# Usage examples:",
        "#   ana          open project with its default agent",
        "#   anac         same project + claude",
        "#   anag         + grok    anax + codex    anau + cursor",
        "#   anao + goose   anaa + aider   anap + chatgpt",
        "#",
        "",
    ]
    # stable order by short name
    rows = sorted(
        ((shorts[p.id], p) for p in projects if p.id in shorts),
        key=lambda t: t[0],
    )
    for short, p in rows:
        pid = p.id
        agent = p.default_agent or "claude"
        lines.append(f"# {p.name}  →  {p.path}  (default: {agent})")
        lines.append(
            f"{short}() {{ command ccmd open {pid} \"$@\"; }}"
        )
        for agent_id, suf in AGENT_SUFFIX.items():
            fn = f"{short}{suf}"
            lines.append(
                f"{fn}() {{ command ccmd open {pid} --agent {agent_id} \"$@\"; }}"
            )
        lines.append("")

    lines.append("# end ccmd shell cmds")
    lines.append("")
    return "\n".join(lines)


def write_shell_cmds(projects: list | None = None) -> Path:
    """Write ~/.ccmd/shell_cmds.sh and persist short names on projects."""
    from ccmd.core.projects import ProjectRegistry

    reg = ProjectRegistry()
    projects = list(projects) if projects is not None else reg.list()
    shorts = allocate_shorts(projects)

    # persist short onto each project yaml
    for p in projects:
        short = shorts.get(p.id)
        if short and getattr(p, "short", None) != short:
            p.short = short
            reg.save(p, regen_shell=False)

    path = shell_cmds_path()
    path.write_text(render_shell_cmds(projects, shorts), encoding="utf-8")
    path.chmod(0o644)

    # also drop a cheat-sheet
    sheet = generated_dir() / "cmds.txt"
    lines = ["# ccmd short commands\n"]
    for p in sorted(projects, key=lambda x: shorts.get(x.id, x.id)):
        s = shorts.get(p.id, "?")
        lines.append(
            f"{s:<10} {p.id:<20} default={p.default_agent:<8}  "
            f"+c claude +g grok +x codex +u cursor +o goose +a aider +p chatgpt\n"
        )
        lines.append(f"{'':10} {p.path}\n")
    sheet.write_text("".join(lines), encoding="utf-8")
    return path


def install_shell_hook(rc_file: Path | None = None) -> list[Path]:
    """Ensure bashrc/zshrc sources shell_cmds.sh (managed block)."""
    ensure_dirs()
    write_shell_cmds()
    block = (
        f"\n{MARKER_BEGIN}\n"
        f"# managed by ccmd — short project commands (ana/anac/anag…)\n"
        f'[ -f "$HOME/.ccmd/shell_cmds.sh" ] && . "$HOME/.ccmd/shell_cmds.sh"\n'
        f"{MARKER_END}\n"
    )
    updated: list[Path] = []
    candidates = []
    if rc_file:
        candidates = [rc_file]
    else:
        home_dir = Path.home()
        for name in (".bashrc", ".zshrc", ".bash_profile"):
            p = home_dir / name
            if p.exists() or name == ".bashrc":
                candidates.append(p)

    for rc in candidates:
        try:
            text = rc.read_text(encoding="utf-8") if rc.exists() else ""
        except OSError:
            continue
        if MARKER_BEGIN in text:
            # replace existing block
            pattern = re.compile(
                re.escape(MARKER_BEGIN) + r".*?" + re.escape(MARKER_END),
                re.DOTALL,
            )
            new_text = pattern.sub(
                block.strip(),
                text,
            )
            if not new_text.endswith("\n"):
                new_text += "\n"
        else:
            new_text = text.rstrip() + "\n" + block
        # backup once
        bak = home() / "backups" / f"{rc.name}.bak"
        bak.parent.mkdir(parents=True, exist_ok=True)
        if rc.exists():
            shutil.copy2(rc, bak)
        rc.write_text(new_text, encoding="utf-8")
        updated.append(rc)
    return updated


def list_cmd_rows(projects: list | None = None) -> list[dict]:
    from ccmd.core.projects import ProjectRegistry

    projects = list(projects) if projects is not None else ProjectRegistry().list()
    shorts = allocate_shorts(projects)
    rows = []
    for p in projects:
        s = shorts.get(p.id, "")
        rows.append(
            {
                "short": s,
                "project": p.id,
                "default_agent": p.default_agent,
                "path": p.path,
                "variants": {a: f"{s}{suf}" for a, suf in AGENT_SUFFIX.items()},
            }
        )
    rows.sort(key=lambda r: r["short"])
    return rows
