from __future__ import annotations

import webbrowser

from ccmd.core.agents.base import BaseAgent, LaunchContext


class ChatGPTAgent(BaseAgent):
    id = "chatgpt"
    display_name = "ChatGPT"
    brand_color = "#74aa9c"
    ascii_logo = "○"
    binaries: list[str] = []
    install_url = "Opens https://chatgpt.com in your browser"
    url = "https://chatgpt.com"

    def is_installed(self) -> bool:
        return True  # browser always available as best-effort

    def version(self) -> str | None:
        return "browser"

    def build_command(self, ctx: LaunchContext) -> list[str]:
        # Special-cased in launcher — returns marker
        return ["__chatgpt_browser__", self.url]

    def open(self, ctx: LaunchContext) -> None:
        webbrowser.open(self.url)
