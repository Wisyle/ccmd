"""Migrate ccmd 1.x custom_commands + shortcuts into 2.0 projects."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ccmd.config.paths import (
    ensure_dirs,
    legacy_custom_commands,
    legacy_dir,
    legacy_shortcuts,
)
from ccmd.core.agents import get_agent
from ccmd.core.projects import ProjectRegistry
from ccmd.core.profiles import AliasStore


AGENT_TOKENS = {
    "claude": "claude",
    "cursor-agent": "cursor",
    "cursor": "cursor",
    "codex": "codex",
    "grok": "grok",
    "goose": "goose",
    "aider": "aider",
}

# Roots searched when a go-name has no shortcut path
SEARCH_ROOTS = [
    Path("/mnt/vylth"),
    Path("/mnt/c/Users/rober/targlobal"),
    Path.home(),
    Path.home() / "projects",
    Path.home() / "code",
]


def resolve_named_path(name: str, shortcuts: dict[str, str] | None = None) -> str | None:
    """Resolve a go-name to a real directory path."""
    if shortcuts and name in shortcuts:
        p = Path(shortcuts[name]).expanduser()
        if p.is_dir():
            return str(p.resolve())
        return str(p)
    # exact dir name under search roots (depth 1-2)
    for root in SEARCH_ROOTS:
        if not root.is_dir():
            continue
        direct = root / name
        if direct.is_dir():
            return str(direct.resolve())
        try:
            for child in root.iterdir():
                if not child.is_dir():
                    continue
                if child.name.lower() == name.lower():
                    return str(child.resolve())
                nested = child / name
                if nested.is_dir():
                    return str(nested.resolve())
        except OSError:
            continue
    return None


@dataclass
class MigratePlan:
    projects: list[dict] = field(default_factory=list)
    aliases: list[tuple[str, str]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _parse_go_agent_chain(action: str) -> tuple[str | None, str | None, str | None]:
    """Return (go_name, agent_id, remainder) from chains like 'go lhs >>> claude'."""
    parts = [p.strip() for p in action.split(">>>")]
    go_name = None
    agent_id = None
    path_cd = None
    for p in parts:
        if p.startswith("go "):
            go_name = p[3:].strip().split()[0] if p[3:].strip() else None
        elif p.startswith("cd "):
            path_cd = p[3:].strip().strip("'\"")
        else:
            token = p.split()[0] if p.split() else ""
            if token in AGENT_TOKENS:
                agent_id = AGENT_TOKENS[token]
    return go_name, agent_id, path_cd


def build_plan() -> MigratePlan:
    plan = MigratePlan()
    shortcuts: dict[str, str] = {}
    sp = legacy_shortcuts()
    if sp.exists():
        data = yaml.safe_load(sp.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict):
            # formats: {name: path} or {shortcuts: {name: path}}
            body = data.get("shortcuts") if "shortcuts" in data else data
            if isinstance(body, dict):
                for k, v in body.items():
                    if isinstance(v, str):
                        shortcuts[str(k)] = v
                    elif isinstance(v, dict) and "path" in v:
                        shortcuts[str(k)] = str(v["path"])

    for name, path in shortcuts.items():
        resolved = resolve_named_path(name, shortcuts) or path
        plan.projects.append(
            {
                "id": name,
                "name": name,
                "path": resolved,
                "default_agent": "claude",
                "source": "shortcuts",
            }
        )

    cp = legacy_custom_commands()
    if cp.exists():
        data = yaml.safe_load(cp.read_text(encoding="utf-8")) or {}
        commands = data.get("commands") if isinstance(data, dict) else None
        if isinstance(commands, dict):
            for cname, body in commands.items():
                if not isinstance(body, dict):
                    continue
                action = str(body.get("action") or "")
                # strip weird control chars
                action = re.sub(r"[\x00-\x1f\x7f-\x9f\udc00-\udfff]", "", action)
                go_name, agent_id, path_cd = _parse_go_agent_chain(action)
                if go_name or path_cd:
                    path = path_cd or ""
                    if not path and go_name:
                        path = resolve_named_path(go_name, shortcuts) or f"~/{go_name}"
                    elif path:
                        path = str(Path(path).expanduser())
                    pid = go_name or cname
                    # merge agent into existing project entry
                    existing = next((p for p in plan.projects if p["id"] == pid), None)
                    if existing:
                        if agent_id:
                            existing["default_agent"] = agent_id
                        existing.setdefault("macros", []).append(cname)
                    else:
                        plan.projects.append(
                            {
                                "id": pid,
                                "name": pid,
                                "path": path or str(Path.home()),
                                "default_agent": agent_id or "claude",
                                "source": f"custom:{cname}",
                                "macros": [cname],
                            }
                        )
                elif action and ">>>" not in action:
                    # simple alias
                    plan.aliases.append((cname, action))
                else:
                    plan.notes.append(f"Skipped complex custom '{cname}': {action[:60]}")

    return plan


def apply_plan(plan: MigratePlan | None = None, *, backup: bool = True) -> dict:
    ensure_dirs()
    plan = plan or build_plan()
    if backup:
        leg = legacy_dir()
        for src in (legacy_custom_commands(), legacy_shortcuts()):
            if src.exists():
                dest = leg / src.name
                shutil.copy2(src, dest)

    reg = ProjectRegistry()
    created = 0
    updated = 0
    for row in plan.projects:
        path = Path(row["path"]).expanduser()
        existing = reg.get(row["id"])
        agent = row.get("default_agent") or "claude"
        if get_agent(agent) is None:
            agent = "claude"
        if existing:
            existing.default_agent = agent
            if path.exists():
                existing.path = str(path.resolve())
            reg.save(existing)
            updated += 1
        else:
            if not path.exists():
                # still register with expanded path string
                pstr = str(path)
            else:
                pstr = str(path.resolve())
            reg.add(
                name=row.get("name") or row["id"],
                path=pstr,
                default_agent=agent,
                project_id=row["id"],
                notes=f"migrated from {row.get('source', '1.x')}",
            )
            created += 1

    aliases = AliasStore()
    for name, cmd in plan.aliases:
        aliases.set_alias(name, cmd)

    return {
        "created": created,
        "updated": updated,
        "aliases": len(plan.aliases),
        "notes": plan.notes,
    }
