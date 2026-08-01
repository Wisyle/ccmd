"""Agent picker with logo tiles."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static

from ccmd.core.agents import detect_agents
from ccmd.core.projects import Project


class AgentScreen(Screen[str | None]):
    BINDINGS = [
        Binding("escape", "cancel", "Back", show=True),
        Binding("left", "left", show=False),
        Binding("right", "right", show=False),
        Binding("up", "up", show=False),
        Binding("down", "down", show=False),
        Binding("enter", "select", "Select", show=True),
        Binding("i", "hint", "Install hint", show=True),
    ]

    def __init__(
        self,
        project: Project | None = None,
        mode: str = "launch",  # launch | set
    ) -> None:
        super().__init__()
        self.project = project
        self.mode = mode
        self._agents = detect_agents()
        self._index = 0
        # prefer project's default
        if project:
            for i, a in enumerate(self._agents):
                if a["id"] == project.default_agent:
                    self._index = i
                    break

    def compose(self) -> ComposeResult:
        if self.mode == "set":
            title = "set default agent"
        else:
            title = "choose agent · saves default · launches"
        if self.project:
            title = f"{title}  ·  [bold #00ffc8]{self.project.name}[/]"
        yield Static(title, id="subtitle")
        yield Static("", id="spinner-line")
        with Vertical():
            yield Grid(id="agent-grid")
            yield Static("", id="agent-detail")
        yield Static(
            "←→↑↓ move · ↵ select · i install hint · esc back",
            id="footer-bar",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#spinner-line", Static).update("⠋  detecting agents…")
        self._render_grid()
        installed = sum(1 for a in self._agents if a["installed"])
        self.query_one("#spinner-line", Static).update(
            f"✦  {installed}/{len(self._agents)} agents ready  ·  "
            f"not just claude — pick any"
        )

    def _render_grid(self) -> None:
        grid = self.query_one("#agent-grid", Grid)
        grid.remove_children()
        for i, a in enumerate(self._agents):
            classes = ["agent-card"]
            classes.append("-installed" if a["installed"] else "-missing")
            if i == self._index:
                classes.append("-focus")
            color = a["color"] if a["installed"] else "#6a6a80"
            num = i + 1
            body = (
                f"[#6a6a80]{num}[/] [{color}]{a['logo']}[/]\n"
                f"[bold]{a['name']}[/]\n"
                f"{'ready' if a['installed'] else 'not found'}"
            )
            grid.mount(Static(body, classes=" ".join(classes), id=f"agent-{i}"))
        self._update_detail()

    def _update_detail(self) -> None:
        a = self._agents[self._index]
        action = "set default only" if self.mode == "set" else "set default + launch"
        lines = [
            f"[bold]{a['logo']} {a['name']}[/]  ({a['id']})",
            f"status   {'installed' if a['installed'] else 'missing'}",
            f"version  {a['version'] or '—'}",
            f"binary   {a['binary'] or '—'}",
            f"hint     {a['hint']}",
            f"action   {action}",
        ]
        self.query_one("#agent-detail", Static).update("\n".join(lines))

    def _move(self, delta: int) -> None:
        n = len(self._agents)
        self._index = (self._index + delta) % n
        self._render_grid()

    def action_left(self) -> None:
        self._move(-1)

    def action_right(self) -> None:
        self._move(1)

    def action_up(self) -> None:
        self._move(-4)

    def action_down(self) -> None:
        self._move(4)

    def action_select(self) -> None:
        a = self._agents[self._index]
        if not a["installed"] and a["id"] != "chatgpt":
            self.notify(
                f"{a['name']} not installed — press i for hint", severity="warning"
            )
            return
        self.dismiss(a["id"])

    def action_hint(self) -> None:
        a = self._agents[self._index]
        self.notify(a["hint"], severity="information", timeout=8)

    def action_cancel(self) -> None:
        self.dismiss(None)
