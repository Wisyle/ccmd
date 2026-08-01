"""Project registry — YAML files under ~/.ccmd/projects/."""

from __future__ import annotations

import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from rapidfuzz import fuzz, process

from ccmd.config.paths import ensure_dirs, projects_dir


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "-", name.strip().lower()).strip("-")
    return s or f"project-{uuid.uuid4().hex[:8]}"


@dataclass
class Project:
    id: str
    name: str
    path: str
    default_agent: str = "claude"
    short: str = ""  # shell shortcut base, e.g. "ana" → ana/anac/anag…
    tags: list[str] = field(default_factory=list)
    env_files: list[str] = field(default_factory=lambda: [".env"])
    path_prepend: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    ssh_host: str | None = None
    mcp_packs: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    last_opened_at: str | None = None
    notes: str = ""

    def resolved_path(self) -> Path:
        return Path(self.path).expanduser().resolve()

    def exists(self) -> bool:
        try:
            return self.resolved_path().is_dir()
        except OSError:
            return False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Project:
        return cls(
            id=str(data["id"]),
            name=str(data.get("name") or data["id"]),
            path=str(data["path"]),
            default_agent=str(data.get("default_agent") or "claude"),
            short=str(data.get("short") or ""),
            tags=list(data.get("tags") or []),
            env_files=list(data.get("env_files") or [".env"]),
            path_prepend=list(data.get("path_prepend") or []),
            aliases=list(data.get("aliases") or []),
            ssh_host=data.get("ssh_host"),
            mcp_packs=list(data.get("mcp_packs") or []),
            created_at=str(data.get("created_at") or _now()),
            updated_at=str(data.get("updated_at") or _now()),
            last_opened_at=data.get("last_opened_at"),
            notes=str(data.get("notes") or ""),
        )


class ProjectRegistry:
    def __init__(self, root: Path | None = None) -> None:
        ensure_dirs()
        self.root = root or projects_dir()
        self.root.mkdir(parents=True, exist_ok=True)

    def _file(self, project_id: str) -> Path:
        return self.root / f"{project_id}.yaml"

    def list(self) -> list[Project]:
        out: list[Project] = []
        for path in sorted(self.root.glob("*.yaml")):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                if isinstance(data, dict) and "id" in data and "path" in data:
                    out.append(Project.from_dict(data))
            except (OSError, yaml.YAMLError):
                continue
        out.sort(key=lambda p: (p.last_opened_at or "", p.name), reverse=True)
        return out

    def get(self, project_id: str) -> Project | None:
        path = self._file(project_id)
        if not path.exists():
            return None
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            return None
        return Project.from_dict(data)

    def save(self, project: Project, *, regen_shell: bool = True) -> Project:
        project.updated_at = _now()
        path = self._file(project.id)
        path.write_text(
            yaml.safe_dump(project.to_dict(), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        path.chmod(0o600)
        if regen_shell:
            try:
                from ccmd.core.shell_cmds import write_shell_cmds

                write_shell_cmds()
            except Exception:
                pass
        return project

    def delete(self, project_id: str) -> bool:
        path = self._file(project_id)
        if path.exists():
            path.unlink()
            try:
                from ccmd.core.shell_cmds import write_shell_cmds

                write_shell_cmds()
            except Exception:
                pass
            return True
        return False

    def add(
        self,
        name: str,
        path: str | Path,
        default_agent: str = "claude",
        project_id: str | None = None,
        **kwargs: Any,
    ) -> Project:
        pid = project_id or _slug(name)
        # avoid collisions
        base = pid
        n = 2
        while self._file(pid).exists():
            pid = f"{base}-{n}"
            n += 1
        resolved = str(Path(path).expanduser().resolve())
        project = Project(
            id=pid,
            name=name,
            path=resolved,
            default_agent=default_agent,
            **{k: v for k, v in kwargs.items() if k in Project.__dataclass_fields__},
        )
        return self.save(project)

    def touch_opened(self, project_id: str) -> None:
        p = self.get(project_id)
        if not p:
            return
        p.last_opened_at = _now()
        self.save(p, regen_shell=False)

    def fuzzy(self, query: str, limit: int = 50) -> list[Project]:
        projects = self.list()
        if not query.strip():
            return projects[:limit]
        choices = {p.id: p for p in projects}
        # search id + name + path + tags
        corpus = {
            p.id: f"{p.id} {p.name} {p.path} {' '.join(p.tags)}" for p in projects
        }
        hits = process.extract(
            query,
            corpus,
            scorer=fuzz.WRatio,
            limit=limit,
        )
        out: list[Project] = []
        for key, score, _ in hits:
            if score < 40:
                continue
            # key is the dict key (project id)
            pid = key if isinstance(key, str) else str(key)
            if pid in choices:
                out.append(choices[pid])
            else:
                # rapidfuzz may return value depending on version
                for p in projects:
                    if corpus[p.id] == key or p.id == key:
                        out.append(p)
                        break
        # dedupe
        seen: set[str] = set()
        unique: list[Project] = []
        for p in out:
            if p.id not in seen:
                seen.add(p.id)
                unique.append(p)
        return unique

    def find_by_path(self, path: str | Path) -> Project | None:
        target = str(Path(path).expanduser().resolve())
        for p in self.list():
            if p.path == target:
                return p
        return None
