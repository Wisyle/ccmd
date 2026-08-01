"""Textual application root."""

from __future__ import annotations

from textual.app import App

from ccmd.tui.screens.hub import HubScreen
from ccmd.tui.theme import CSS


class CcmdApp(App):
    TITLE = "ccmd"
    CSS = CSS
    SCREENS = {"hub": HubScreen}

    def on_mount(self) -> None:
        self.push_screen(HubScreen())


def run_tui() -> None:
    CcmdApp().run()
