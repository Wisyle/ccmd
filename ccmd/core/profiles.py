"""Env files, PATH prepend, alias application for launch."""

from __future__ import annotations

import os
import re
import shlex
import tempfile
from pathlib import Path
from typing import Mapping

import yaml

from ccmd.config.paths import aliases_yaml, ensure_dirs
from ccmd.core.projects import Project


_ENV_LINE = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


def load_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _ENV_LINE.match(line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]
        out[key] = val
    return out


def merge_project_env(project: Project, base: Mapping[str, str] | None = None) -> dict[str, str]:
    env = dict(base or os.environ)
    root = project.resolved_path()
    for rel in project.env_files:
        env.update(load_env_file(root / rel))
    # PATH prepend
    prepend = [str(Path(p).expanduser()) for p in project.path_prepend]
    # global path prepends
    store = AliasStore()
    prepend.extend(store.path_prepend)
    if prepend:
        old = env.get("PATH", "")
        env["PATH"] = os.pathsep.join(prepend + ([old] if old else []))
    env["CCMD_PROJECT"] = project.id
    env["CCMD_PROJECT_PATH"] = str(root)
    return env


class AliasStore:
    def __init__(self, path: Path | None = None) -> None:
        ensure_dirs()
        self.path = path or aliases_yaml()

    def load(self) -> dict:
        if not self.path.exists():
            return {"aliases": {}, "path_prepend": []}
        data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            return {"aliases": {}, "path_prepend": []}
        return {
            "aliases": dict(data.get("aliases") or {}),
            "path_prepend": list(data.get("path_prepend") or []),
        }

    def save(self, data: dict) -> None:
        self.path.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        self.path.chmod(0o600)

    @property
    def aliases(self) -> dict[str, str]:
        return self.load()["aliases"]

    @property
    def path_prepend(self) -> list[str]:
        return self.load()["path_prepend"]

    def set_alias(self, name: str, command: str) -> None:
        data = self.load()
        data["aliases"][name] = command
        self.save(data)

    def remove_alias(self, name: str) -> bool:
        data = self.load()
        if name not in data["aliases"]:
            return False
        del data["aliases"][name]
        self.save(data)
        return True

    def set_path_prepend(self, paths: list[str]) -> None:
        data = self.load()
        data["path_prepend"] = paths
        self.save(data)

    def import_from_bashrc(self, bashrc: Path | None = None) -> list[tuple[str, str]]:
        """Parse alias lines from bashrc. Returns list of (name, value) found."""
        path = bashrc or (Path.home() / ".bashrc")
        if not path.is_file():
            return []
        found: list[tuple[str, str]] = []
        # alias name='value' or alias name="value"
        pat = re.compile(r"^\s*alias\s+([A-Za-z0-9_./-]+)=(['\"])(.*?)\2\s*$")
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = pat.match(line)
            if m:
                found.append((m.group(1), m.group(3)))
        return found

    def write_wrapper_script(
        self, project: Project, inner_cmd: list[str], env: dict[str, str]
    ) -> Path:
        """Ephemeral bash wrapper that defines selected aliases then execs agent."""
        store = self.load()
        names = project.aliases or list(store["aliases"].keys())
        lines = ["#!/usr/bin/env bash", "set -euo pipefail"]
        for name in names:
            if name in store["aliases"]:
                cmd = store["aliases"][name]
                # define as function/alias safely
                lines.append(f"alias {shlex.quote(name)}={shlex.quote(cmd)}")
        # expand PATH already in env; still set for shell
        if "PATH" in env:
            lines.append(f"export PATH={shlex.quote(env['PATH'])}")
        lines.append("exec " + " ".join(shlex.quote(c) for c in inner_cmd))
        fd, name = tempfile.mkstemp(prefix="ccmd-launch-", suffix=".sh")
        os = __import__("os")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        path = Path(name)
        path.chmod(0o700)
        return path
