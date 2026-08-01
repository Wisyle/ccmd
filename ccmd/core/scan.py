"""Scan filesystem roots for project-like directories."""

from __future__ import annotations

from pathlib import Path

from ccmd.config.schema import load_config
from ccmd.core.projects import ProjectRegistry

# markers that suggest a project root
MARKERS = {
    ".git",
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "CLAUDE.md",
    "AGENTS.md",
}


def scan_roots(
    roots: list[str] | None = None,
    depth: int = 3,
    *,
    register: bool = False,
    default_agent: str = "claude",
) -> list[dict]:
    cfg = load_config()
    root_paths = [Path(r).expanduser() for r in (roots or cfg.scan_roots)]
    found: list[dict] = []
    reg = ProjectRegistry() if register else None

    for root in root_paths:
        if not root.is_dir():
            continue
        _walk(root, root, depth, found)

    # dedupe by path
    by_path: dict[str, dict] = {}
    for row in found:
        by_path[row["path"]] = row
    rows = list(by_path.values())

    if register and reg:
        for row in rows:
            if reg.find_by_path(row["path"]):
                continue
            reg.add(
                name=row["name"],
                path=row["path"],
                default_agent=default_agent,
                project_id=row["name"],
                notes="scanned",
            )
    return rows


def _walk(root: Path, current: Path, depth: int, found: list[dict]) -> None:
    if depth < 0:
        return
    try:
        entries = list(current.iterdir())
    except OSError:
        return
    names = {e.name for e in entries}
    if names & MARKERS and current != root:
        found.append(
            {
                "name": current.name,
                "path": str(current.resolve()),
                "markers": sorted(names & MARKERS),
            }
        )
        return  # don't nest further inside a project
    if depth == 0:
        return
    for e in entries:
        if not e.is_dir() or e.name.startswith(".") or e.name in (
            "node_modules",
            "dist",
            "build",
            ".venv",
            "venv",
            "__pycache__",
            "target",
        ):
            continue
        _walk(root, e, depth - 1, found)
