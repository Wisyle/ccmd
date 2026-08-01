"""Filesystem helpers for browse / scan roots (no machine-specific hardcoding)."""

from __future__ import annotations

from pathlib import Path

from ccmd.config.schema import load_config

# Never show these as browsable children (noise / huge trees)
SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        ".svn",
        ".hg",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        "target",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "site-packages",
    }
)


def default_browse_roots() -> list[Path]:
    """Portable roots: home, config scan_roots, and any existing /mnt/* tops."""
    roots: list[Path] = []
    seen: set[str] = set()

    def add(p: Path) -> None:
        try:
            r = p.expanduser().resolve()
        except OSError:
            return
        if not r.is_dir():
            return
        key = str(r)
        if key in seen:
            return
        seen.add(key)
        roots.append(r)

    add(Path.home())
    add(Path.home() / "projects")
    add(Path.home() / "code")
    add(Path.home() / "dev")
    add(Path.home() / "src")
    add(Path.cwd())

    try:
        cfg = load_config()
        for s in cfg.scan_roots:
            add(Path(s))
    except Exception:
        pass

    # Any mount under /mnt (WSL drives, shared volumes) — not just one folder
    mnt = Path("/mnt")
    if mnt.is_dir():
        add(mnt)
        try:
            for child in sorted(mnt.iterdir()):
                if child.is_dir() and not child.name.startswith("."):
                    add(child)
        except OSError:
            pass

    # Common Unix work locations
    for p in (Path("/opt"), Path("/srv"), Path("/var/www")):
        add(p)

    return roots


def list_dir_entries(
    path: Path,
    *,
    show_hidden: bool = False,
    dirs_only: bool = True,
) -> list[tuple[str, Path, bool]]:
    """Return sorted (label, path, is_dir) for children of path."""
    path = path.expanduser()
    try:
        path = path.resolve()
    except OSError:
        return []

    entries: list[tuple[str, Path, bool]] = []
    try:
        children = list(path.iterdir())
    except OSError:
        return []

    for child in children:
        name = child.name
        if not show_hidden and name.startswith("."):
            continue
        if name in SKIP_DIR_NAMES:
            continue
        try:
            is_dir = child.is_dir()
        except OSError:
            continue
        if dirs_only and not is_dir:
            continue
        # skip symlinks that loop / broken
        if child.is_symlink():
            try:
                if not child.resolve().exists():
                    continue
            except OSError:
                continue
        entries.append((name, child, is_dir))

    entries.sort(key=lambda t: (not t[2], t[0].lower()))
    return entries


def is_projectish(path: Path) -> bool:
    markers = {
        ".git",
        "package.json",
        "pyproject.toml",
        "Cargo.toml",
        "go.mod",
        "CLAUDE.md",
        "AGENTS.md",
        "Makefile",
        "composer.json",
    }
    try:
        names = {p.name for p in path.iterdir()}
    except OSError:
        return False
    return bool(names & markers)
