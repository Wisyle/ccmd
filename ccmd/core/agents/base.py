"""Agent adapter protocol and registry."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass
class LaunchContext:
    cwd: Path
    env: dict[str, str]
    extra_args: list[str] = field(default_factory=list)
    initial_prompt: str | None = None
    session_label: str | None = None
    detach: bool = False


@runtime_checkable
class AgentAdapter(Protocol):
    id: str
    display_name: str
    brand_color: str
    ascii_logo: str
    binaries: list[str]

    def is_installed(self) -> bool: ...
    def version(self) -> str | None: ...
    def install_hint(self) -> str: ...
    def build_command(self, ctx: LaunchContext) -> list[str]: ...


class BaseAgent:
    id: str = "base"
    display_name: str = "Base"
    brand_color: str = "#00ffc8"
    ascii_logo: str = "?"
    binaries: list[str] = []
    install_url: str = ""

    def which(self) -> str | None:
        for b in self.binaries:
            path = shutil.which(b)
            if path:
                return path
        return None

    def is_installed(self) -> bool:
        return self.which() is not None

    def version(self) -> str | None:
        import subprocess

        bin_path = self.which()
        if not bin_path:
            return None
        for args in (["--version"], ["-V"], ["version"]):
            try:
                r = subprocess.run(
                    [bin_path, *args],
                    capture_output=True,
                    text=True,
                    timeout=3,
                    check=False,
                )
                out = (r.stdout or r.stderr or "").strip().splitlines()
                if out:
                    return out[0][:80]
            except (OSError, subprocess.TimeoutExpired):
                continue
        return "installed"

    def install_hint(self) -> str:
        return self.install_url or f"Install {self.display_name} and ensure it is on PATH"

    def build_command(self, ctx: LaunchContext) -> list[str]:
        bin_path = self.which()
        if not bin_path:
            raise FileNotFoundError(f"{self.display_name} is not installed")
        cmd = [bin_path, *ctx.extra_args]
        if ctx.initial_prompt:
            cmd.extend(self._prompt_args(ctx.initial_prompt))
        return cmd

    def _prompt_args(self, prompt: str) -> list[str]:
        return [prompt]
