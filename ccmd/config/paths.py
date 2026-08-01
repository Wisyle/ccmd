"""Filesystem layout under ~/.ccmd."""

from __future__ import annotations

import os
from pathlib import Path


def home() -> Path:
    override = os.environ.get("CCMD_HOME")
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".ccmd"


def ensure_dirs() -> Path:
    root = home()
    for sub in (
        "projects",
        "ssh",
        "legacy",
        "generated",
        "backups",
    ):
        (root / sub).mkdir(parents=True, exist_ok=True)
    return root


def config_toml() -> Path:
    return home() / "config.toml"


def projects_dir() -> Path:
    return home() / "projects"


def ssh_hosts() -> Path:
    return home() / "ssh" / "hosts.yaml"


def aliases_yaml() -> Path:
    return home() / "aliases.yaml"


def sessions_log() -> Path:
    return home() / "sessions.jsonl"


def audit_log() -> Path:
    return home() / "audit.jsonl"


def legacy_dir() -> Path:
    return home() / "legacy"


def generated_dir() -> Path:
    return home() / "generated"


# 1.x paths (read during migrate)
def legacy_custom_commands() -> Path:
    return home() / "custom_commands.yaml"


def legacy_shortcuts() -> Path:
    return home() / "shortcuts.yaml"
