"""SSH host manager."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from ccmd.core.launcher import LaunchError, connect_ssh
from ccmd.core.ssh import SSHStore


class SSHScreen(Screen):
    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("enter", "connect", "Connect", show=True),
        Binding("i", "import_config", "Import ~/.ssh/config", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Static("ssh hosts", id="subtitle")
        yield DataTable(id="ssh-table")
        yield Static("↵ connect · i import config · r refresh · esc back", id="footer-bar")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#ssh-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("id", "user@host", "port", "identity")
        self.action_refresh()

    def action_refresh(self) -> None:
        table = self.query_one("#ssh-table", DataTable)
        table.clear()
        for h in SSHStore().list():
            target = f"{h.user}@{h.host}" if h.user else h.host
            table.add_row(
                h.id,
                target,
                str(h.port),
                h.identity_file or "—",
                key=h.id,
            )

    def action_connect(self) -> None:
        table = self.query_one("#ssh-table", DataTable)
        if table.row_count == 0:
            self.notify("no hosts — press i to import", severity="warning")
            return
        try:
            host_id = str(table.get_row_at(table.cursor_row)[0])
        except Exception:
            return
        self.notify(f"connecting {host_id}…", severity="information")
        try:
            connect_ssh(host_id)
        except LaunchError as e:
            self.notify(str(e), severity="error")

    def action_import_config(self) -> None:
        hosts = SSHStore().import_ssh_config()
        self.notify(f"imported {len(hosts)} hosts", severity="information")
        self.action_refresh()

    def action_back(self) -> None:
        self.app.pop_screen()
