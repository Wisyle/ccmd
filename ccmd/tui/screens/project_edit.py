"""Create a new project."""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Label, Static

from ccmd.core.projects import ProjectRegistry


class ProjectEditScreen(Screen[bool | None]):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Static("new project", id="subtitle")
        with Vertical():
            yield Label("name")
            yield Input(placeholder="vylth-flow", id="name")
            yield Label("path")
            yield Input(placeholder="/mnt/vylth/vylth-flow", id="path")
            yield Label("default agent (claude|grok|codex|cursor|goose|aider|chatgpt)")
            yield Input(value="claude", id="agent")
            yield Button("save", id="save", variant="success")
            yield Button("cancel", id="cancel")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(False)
            return
        name = self.query_one("#name", Input).value.strip()
        path = self.query_one("#path", Input).value.strip()
        agent = self.query_one("#agent", Input).value.strip() or "claude"
        if not name or not path:
            self.notify("name and path required", severity="error")
            return
        p = Path(path).expanduser()
        if not p.is_dir():
            self.notify(f"not a directory: {p}", severity="error")
            return
        from ccmd.core.shell_cmds import cmds_notice

        proj = ProjectRegistry().add(name=name, path=p, default_agent=agent)
        proj = ProjectRegistry().get(proj.id) or proj
        self.notify(f"added {name}", severity="information", timeout=3)
        self.notify(cmds_notice(proj), severity="information", timeout=10)
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)
