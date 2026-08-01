"""Main project hub screen."""

from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Input, OptionList, Static
from textual.widgets.option_list import Option

from ccmd import __version__
from ccmd.core.agents import get_agent
from ccmd.core.launcher import LaunchError, launch_project
from ccmd.core.projects import Project, ProjectRegistry
from ccmd.tui.ascii import BANNER, BANNER_COMPACT


class HubScreen(Screen):
    BINDINGS = [
        Binding("enter", "open_project", "Open", show=True),
        Binding("a", "pick_agent", "Agents", show=True),
        Binding("n", "new_project", "New", show=True),
        Binding("s", "sessions", "Sessions", show=True),
        Binding("h", "ssh", "SSH", show=True),
        Binding("l", "aliases", "Aliases", show=True),
        Binding("slash", "focus_filter", "Filter", show=False),
        Binding("/", "focus_filter", "Filter", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.registry = ProjectRegistry()
        self._projects: list[Project] = []
        self._filtered: list[Project] = []

    def compose(self) -> ComposeResult:
        yield Static(BANNER.strip("\n"), id="banner")
        yield Static(f"project hub  ·  v{__version__}  ·  pick → agent → launch", id="subtitle")
        yield Input(placeholder="filter projects…  (/ to focus)", id="filter")
        with Horizontal(id="main"):
            with Vertical(id="projects-panel"):
                yield Static("projects", classes="panel-title")
                yield OptionList(id="project-list")
            with Vertical(id="detail-panel"):
                yield Static("detail", classes="panel-title")
                yield Static("Select a project", id="detail")
        yield Static("", id="status")
        yield Static(
            "↵ open · a agents · n new · s sessions · h ssh · l aliases · / filter · q quit",
            id="footer-bar",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._load_projects()
        self.query_one("#filter", Input).focus()

    def _load_projects(self, query: str = "") -> None:
        self._projects = self.registry.list()
        if query.strip():
            self._filtered = self.registry.fuzzy(query)
        else:
            self._filtered = list(self._projects)
        ol = self.query_one("#project-list", OptionList)
        ol.clear_options()
        if not self._filtered:
            ol.add_option(Option("  (no projects — press n to add)", id="__empty__"))
            self.query_one("#status", Static).update(
                "no projects yet · n new · or: ccmd migrate --apply"
            )
            return
        for p in self._filtered:
            mark = "✓" if p.exists() else "!"
            agent = p.default_agent
            label = f" {mark} {p.name:<20}  {agent:<8}  {p.path}"
            ol.add_option(Option(label, id=p.id))
        ol.highlighted = 0
        self._update_detail()
        self.query_one("#status", Static).update(
            f"{len(self._filtered)}/{len(self._projects)} projects"
        )

    def _selected(self) -> Project | None:
        ol = self.query_one("#project-list", OptionList)
        if ol.highlighted is None:
            return None
        try:
            opt = ol.get_option_at_index(ol.highlighted)
        except Exception:
            return None
        if opt.id in (None, "__empty__"):
            return None
        return self.registry.get(str(opt.id))

    def _update_detail(self) -> None:
        p = self._selected()
        detail = self.query_one("#detail", Static)
        if not p:
            detail.update("Select a project")
            return
        agent = get_agent(p.default_agent)
        agent_line = (
            f"{agent.ascii_logo} {agent.display_name}"
            if agent
            else p.default_agent
        )
        exists = "yes" if p.exists() else "MISSING"
        lines = [
            f"[bold #00ffc8]{p.name}[/]",
            f"id      {p.id}",
            f"path    {p.path}",
            f"exists  {exists}",
            f"agent   {agent_line}",
            f"ssh     {p.ssh_host or '—'}",
            f"env     {', '.join(p.env_files) or '—'}",
            f"tags    {', '.join(p.tags) or '—'}",
            f"opened  {p.last_opened_at or 'never'}",
            "",
            "[#6a6a80]enter open · a choose agent · d detach[/]",
        ]
        detail.update("\n".join(lines))

    @on(Input.Changed, "#filter")
    def on_filter(self, event: Input.Changed) -> None:
        self._load_projects(event.value)

    @on(OptionList.OptionHighlighted)
    def on_highlight(self, event: OptionList.OptionHighlighted) -> None:
        self._update_detail()

    @on(OptionList.OptionSelected)
    def on_select(self, event: OptionList.OptionSelected) -> None:
        self.action_open_project()

    def action_focus_filter(self) -> None:
        self.query_one("#filter", Input).focus()

    def action_refresh(self) -> None:
        q = self.query_one("#filter", Input).value
        self._load_projects(q)
        self.notify("refreshed", severity="information")

    def action_open_project(self) -> None:
        p = self._selected()
        if not p:
            self.notify("no project selected", severity="warning")
            return
        if not p.exists():
            self.notify(f"path missing: {p.path}", severity="error")
            return
        self._launch(p, p.default_agent, detach=False)

    def action_pick_agent(self) -> None:
        p = self._selected()
        if not p:
            self.notify("select a project first", severity="warning")
            return
        from ccmd.tui.screens.agents import AgentScreen

        def _done(agent_id: str | None) -> None:
            if agent_id:
                self._launch(p, agent_id, detach=False)

        self.app.push_screen(AgentScreen(project=p), _done)

    def action_new_project(self) -> None:
        from ccmd.tui.screens.project_edit import ProjectEditScreen

        def _done(ok: bool | None) -> None:
            if ok:
                self._load_projects(self.query_one("#filter", Input).value)

        self.app.push_screen(ProjectEditScreen(), _done)

    def action_sessions(self) -> None:
        from ccmd.tui.screens.sessions import SessionsScreen

        self.app.push_screen(SessionsScreen())

    def action_ssh(self) -> None:
        from ccmd.tui.screens.ssh import SSHScreen

        self.app.push_screen(SSHScreen())

    def action_aliases(self) -> None:
        from ccmd.tui.screens.aliases import AliasesScreen

        self.app.push_screen(AliasesScreen())

    def action_quit(self) -> None:
        self.app.exit()

    @work(thread=True)
    def _launch(self, project: Project, agent_id: str, detach: bool) -> None:
        self.app.call_from_thread(
            self.query_one("#status", Static).update,
            f"handing off to {agent_id}…",
        )
        try:
            # replace process — must run on main for exec; use call_from_thread
            def _do() -> None:
                try:
                    code = launch_project(
                        project, agent_id, detach=detach, replace=not detach
                    )
                    if detach:
                        self.notify(f"launched {agent_id} (detached)", severity="information")
                    else:
                        # if returned, agent exited
                        self.notify(f"{agent_id} exited ({code})", severity="information")
                        self._load_projects(self.query_one("#filter", Input).value)
                except LaunchError as e:
                    self.notify(str(e), severity="error")

            self.app.call_from_thread(_do)
        except Exception as e:
            self.app.call_from_thread(self.notify, str(e), severity="error")

    def on_resize(self) -> None:
        banner = self.query_one("#banner", Static)
        if self.size.width < 50:
            banner.update(BANNER_COMPACT)
        else:
            banner.update(BANNER.strip("\n"))
