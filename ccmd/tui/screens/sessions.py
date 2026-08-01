"""Session list / kill."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from ccmd.core.sessions import SessionStore


class SessionsScreen(Screen):
    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("k", "kill", "Kill", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Static("sessions", id="subtitle")
        yield DataTable(id="session-table")
        yield Static("r refresh · k kill · esc back", id="footer-bar")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#session-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("id", "project", "agent", "status", "pid", "when")
        self.action_refresh()

    def action_refresh(self) -> None:
        table = self.query_one("#session-table", DataTable)
        table.clear()
        for s in SessionStore().list(80):
            table.add_row(
                s.id,
                s.project,
                s.agent,
                s.status,
                str(s.pid or s.tmux_session or "—"),
                s.ts[:19],
                key=s.id,
            )

    def action_kill(self) -> None:
        table = self.query_one("#session-table", DataTable)
        if table.row_count == 0:
            return
        row = table.cursor_row
        # get key
        try:
            row_key = table.get_row_at(row)[0]
        except Exception:
            self.notify("no session", severity="warning")
            return
        ok = SessionStore().kill(str(row_key))
        self.notify("killed" if ok else "could not kill", severity="information" if ok else "error")
        self.action_refresh()

    def action_back(self) -> None:
        self.app.pop_screen()
