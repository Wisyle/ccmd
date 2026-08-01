"""Global config load/save (TOML)."""

from __future__ import annotations

import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ccmd.config.paths import config_toml, ensure_dirs


@dataclass
class UIConfig:
    theme: str = "vibrant"
    motion: str = "full"  # full | minimal
    nerd_fonts: bool = True


@dataclass
class Config:
    scan_roots: list[str] = field(
        default_factory=lambda: ["~/projects", "~/code", "/mnt/vylth"]
    )
    scan_depth: int = 3
    default_agent: str = "claude"
    ui: UIConfig = field(default_factory=UIConfig)
    allow_roots: list[str] = field(default_factory=list)  # empty = no restriction


def _ui_from_dict(d: dict[str, Any]) -> UIConfig:
    return UIConfig(
        theme=str(d.get("theme", "vibrant")),
        motion=str(d.get("motion", "full")),
        nerd_fonts=bool(d.get("nerd_fonts", True)),
    )


def load_config() -> Config:
    ensure_dirs()
    path = config_toml()
    if not path.exists():
        cfg = Config()
        save_config(cfg)
        return cfg
    with path.open("rb") as f:
        data = tomllib.load(f)
    ui = _ui_from_dict(data.get("ui") or {})
    return Config(
        scan_roots=list(data.get("scan_roots") or Config().scan_roots),
        scan_depth=int(data.get("scan_depth", 3)),
        default_agent=str(data.get("default_agent", "claude")),
        ui=ui,
        allow_roots=list(data.get("allow_roots") or []),
    )


def save_config(cfg: Config) -> None:
    ensure_dirs()
    path = config_toml()
    # Minimal TOML writer (stdlib has no dump in 3.11)
    lines = [
        f'default_agent = "{cfg.default_agent}"',
        f"scan_depth = {cfg.scan_depth}",
        "",
        "scan_roots = [",
    ]
    for r in cfg.scan_roots:
        lines.append(f'  "{r}",')
    lines.append("]")
    lines.append("")
    if cfg.allow_roots:
        lines.append("allow_roots = [")
        for r in cfg.allow_roots:
            lines.append(f'  "{r}",')
        lines.append("]")
        lines.append("")
    lines.extend(
        [
            "[ui]",
            f'theme = "{cfg.ui.theme}"',
            f'motion = "{cfg.ui.motion}"',
            f"nerd_fonts = {'true' if cfg.ui.nerd_fonts else 'false'}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    path.chmod(0o600)


def as_plain_dict(cfg: Config) -> dict[str, Any]:
    d = asdict(cfg)
    return d
