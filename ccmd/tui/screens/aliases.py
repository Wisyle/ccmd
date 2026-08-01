"""Alias + PATH manager screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from ccmd.core.profiles import AliasStore


class AliasesScreen(Screen):
    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("i", "import_bashrc", "Import bashrc", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Static("aliases & PATH", id="subtitle")
        yield DataTable(id="alias-table")
        yield Static("", id="path-line")
        yield Static("i import ~/.bashrc aliases · r refresh · esc back", id="footer-bar")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#alias-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("name", "command")
        self.action_refresh()

    def action_refresh(self) -> None:
        store = AliasStore()
        table = self.query_one("#alias-table", DataTable)
        table.clear()
        for name, cmd in sorted(store.aliases.items()):
            table.add_row(name, cmd[:80])
        paths = store.path_prepend
        self.query_one("#path-line", Static).update(
            "PATH prepend: " + (":".join(paths) if paths else "(none)")
        )

    def action_import_bashrc(self) -> None:
        store = AliasStore()
        found = store.import_from_bashrc()
        n = 0
        for name, cmd in found:
            if name not in store.aliases:
                store.set_alias(name, cmd)
                n += 1
        self.notify(f"imported {n} new aliases ({len(found)} found)", severity="information")
        self.action_refresh()

    def action_back(self) -> None:
        self.app.pop_screen()
