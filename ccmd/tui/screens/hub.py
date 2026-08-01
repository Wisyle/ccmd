"""Main project hub screen."""

from __future__ import annotations

from pathlib import Path

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Input, OptionList, Static
from textual.widgets.option_list import Option

from ccmd import __version__
from ccmd.core.agents import all_agents, detect_agents, get_agent
from ccmd.core.launcher import LaunchError, launch_project
from ccmd.core.projects import Project, ProjectRegistry
from ccmd.tui.ascii import BANNER, BANNER_COMPACT

# Order for 1–7 hotkeys
AGENT_ORDER = [a.id for a in all_agents()]


def _agent_bar() -> str:
    """Plain text — no Rich tags (logos/paths break markup easily)."""
    parts: list[str] = []
    for i, a in enumerate(detect_agents(), start=1):
        flag = "+" if a["installed"] else "-"
        parts.append(f"{i}:{a['logo']}{a['id']}{flag}")
    return "  ".join(parts)


class HubScreen(Screen):
    # Filter Input is can_focus=False until / is pressed, so f/b/a never type into it.
    BINDINGS = [
        Binding("enter", "open_project", "Open", show=True),
        Binding("a", "pick_agent", "Agents", show=True),
        Binding("A", "set_agent_only", "Set agent", show=True),
        Binding("n", "new_project", "New", show=True),
        Binding("b", "browse", "Browse", show=True),
        Binding("f", "browse_mnt", "Disk /mnt", show=True),
        Binding("s", "sessions", "Sessions", show=True),
        Binding("h", "ssh", "SSH", show=True),
        Binding("l", "aliases", "Aliases", show=True),
        Binding("d", "detach", "Detach", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("left_square_bracket", "agent_prev", "Agent−", show=True),
        Binding("right_square_bracket", "agent_next", "Agent+", show=True),
        Binding("slash", "focus_filter", "Filter", show=False),
        Binding("/", "focus_filter", "Filter", show=True),
        Binding("escape", "blur_filter", "Esc", show=False),
        Binding("1", "agent_n_1", show=False),
        Binding("2", "agent_n_2", show=False),
        Binding("3", "agent_n_3", show=False),
        Binding("4", "agent_n_4", show=False),
        Binding("5", "agent_n_5", show=False),
        Binding("6", "agent_n_6", show=False),
        Binding("7", "agent_n_7", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.registry = ProjectRegistry()
        self._projects: list[Project] = []
        self._filtered: list[Project] = []
        self._agent_info = detect_agents()

    def compose(self) -> ComposeResult:
        yield Static(BANNER.strip("\n"), id="banner")
        yield Static(
            f"project hub  ·  v{__version__}  ·  b/f browse disk  ·  ] cycle agent  ·  1–7 set agent",
            id="subtitle",
        )
        yield Static(_agent_bar(), id="agent-bar")
        # can_focus stays False until / — prevents f/b/a landing in the box
        yield Input(
            placeholder="press / to filter projects…",
            id="filter",
        )
        with Horizontal(id="main"):
            with Vertical(id="projects-panel"):
                yield Static("projects (registry — not whole disk)", classes="panel-title")
                yield OptionList(id="project-list")
            with Vertical(id="detail-panel"):
                yield Static("detail", classes="panel-title")
                # markup=False: paths, timestamps, and key hints must never hit Rich
                yield Static("Select a project", id="detail", markup=False)
        yield Static("", id="status", markup=False)
        yield Static(
            "enter open · f /mnt · b browse · / filter · esc list · a agent · ] cycle · q quit",
            id="footer-bar",
            markup=False,
        )
        yield Footer()

    def on_mount(self) -> None:
        filt = self.query_one("#filter", Input)
        filt.can_focus = False
        self._load_projects()
        self.query_one("#project-list", OptionList).focus()
        if not self._projects:
            self.notify(
                "no projects — opening disk browser (or press f for /mnt)",
                severity="information",
                timeout=4,
            )
            self.set_timer(0.3, self.action_browse)
        else:
            if all(p.default_agent == "claude" for p in self._projects[:20]):
                self.notify(
                    "tip: f = browse /mnt · / = filter · ] = cycle agent",
                    severity="information",
                    timeout=5,
                )

    def _load_projects(self, query: str = "") -> None:
        self._projects = self.registry.list()
        if query.strip():
            self._filtered = self.registry.fuzzy(query)
        else:
            self._filtered = list(self._projects)
        ol = self.query_one("#project-list", OptionList)
        # preserve highlight id
        prev_id = None
        if ol.highlighted is not None:
            try:
                prev_id = ol.get_option_at_index(ol.highlighted).id
            except Exception:
                prev_id = None
        ol.clear_options()
        if not self._filtered:
            ol.add_option(Option("  (no projects — press b or f to browse disk)", id="__empty__"))
            self.query_one("#status", Static).update(
                "empty registry · b browse · f /mnt · n type path"
            )
            return
        restore_idx = 0
        for i, p in enumerate(self._filtered):
            mark = "✓" if p.exists() else "!"
            agent = get_agent(p.default_agent)
            logo = agent.ascii_logo if agent else "?"
            # short root hint so non-vylth stands out
            root_hint = _root_label(p.path)
            label = f" {mark} {logo} {p.name:<18}  {p.default_agent:<8}  {root_hint} {p.path}"
            ol.add_option(Option(label, id=p.id))
            if prev_id and p.id == prev_id:
                restore_idx = i
        ol.highlighted = restore_idx
        self._update_detail()
        agents_used = sorted({p.default_agent for p in self._projects})
        self.query_one("#status", Static).update(
            f"{len(self._filtered)}/{len(self._projects)} projects  ·  "
            f"defaults: {', '.join(agents_used)}  ·  "
            f"disk: b / f not this list"
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
            detail.update(
                "Select a project\n\n"
                "This list is your saved registry.\n"
                "Press f to browse /mnt and subdirs,\n"
                "or b for home + all roots.\n"
                "Press ] to cycle default agent."
            )
            return
        agent = get_agent(p.default_agent)
        agent_line = (
            f"{agent.ascii_logo} {agent.display_name}"
            if agent
            else p.default_agent
        )
        exists = "yes" if p.exists() else "MISSING"
        roster: list[str] = []
        for i, a in enumerate(self._agent_info, start=1):
            mark = "*" if a["id"] == p.default_agent else " "
            ready = "ok" if a["installed"] else "no"
            roster.append(f"  {mark} {i} {a['logo']} {a['id']:<8} {ready}")

        short = p.short or p.id[:4]
        lines = [
            p.name,
            f"id      {p.id}",
            f"short   {short}  →  {short}c claude · {short}g grok · {short}x codex · {short}u cursor",
            f"        {short}o goose · {short}a aider · {short}p chatgpt · bare {short} = default",
            f"path    {p.path}",
            f"root    {_root_label(p.path)}",
            f"exists  {exists}",
            f"agent   {agent_line}  (default)",
            f"ssh     {p.ssh_host or '-'}",
            f"env     {', '.join(p.env_files) or '-'}",
            f"tags    {', '.join(p.tags) or '-'}",
            f"opened  {p.last_opened_at or 'never'}",
            "",
            "agents  ]/[ cycle · 1-7 set · A set · a launch",
            *roster,
            "",
            "enter open · d detach · b/f add from disk",
            "shell: source ~/.ccmd/shell_cmds.sh  (or: ccmd shell install)",
        ]
        detail.update("\n".join(lines))

    def _set_default_agent(self, agent_id: str, *, notify: bool = True) -> None:
        p = self._selected()
        if not p:
            self.notify("select a project first", severity="warning")
            return
        if get_agent(agent_id) is None:
            self.notify(f"unknown agent {agent_id}", severity="error")
            return
        p.default_agent = agent_id
        self.registry.save(p)
        if notify:
            self.notify(f"{p.id} → default agent {agent_id}", severity="information")
        self._load_projects(self.query_one("#filter", Input).value)

    def _cycle_agent(self, delta: int) -> None:
        p = self._selected()
        if not p:
            self.notify("select a project first", severity="warning")
            return
        ids = AGENT_ORDER
        try:
            idx = ids.index(p.default_agent)
        except ValueError:
            idx = 0
        new_id = ids[(idx + delta) % len(ids)]
        self._set_default_agent(new_id)

    def _agent_n(self, n: int) -> None:
        if 1 <= n <= len(AGENT_ORDER):
            self._set_default_agent(AGENT_ORDER[n - 1])

    # ── events ───────────────────────────────────────────────

    @on(Input.Changed, "#filter")
    def on_filter(self, event: Input.Changed) -> None:
        self._load_projects(event.value)

    @on(OptionList.OptionHighlighted)
    def on_highlight(self, event: OptionList.OptionHighlighted) -> None:
        self._update_detail()

    @on(OptionList.OptionSelected)
    def on_select(self, event: OptionList.OptionSelected) -> None:
        self.action_open_project()

    # ── actions ──────────────────────────────────────────────

    def action_focus_filter(self) -> None:
        """Only way into the filter — so f never types into the box by accident."""
        filt = self.query_one("#filter", Input)
        filt.can_focus = True
        filt.focus()

    def action_blur_filter(self) -> None:
        """Esc: leave filter, give keys back to hub (f/b/a work again)."""
        filt = self.query_one("#filter", Input)
        if self.focused is filt or filt.has_focus:
            filt.can_focus = False
            self.query_one("#project-list", OptionList).focus()
            return
        # if not in filter, esc clears filter text
        if filt.value:
            filt.value = ""
            self._load_projects("")
        self.query_one("#project-list", OptionList).focus()

    def action_refresh(self) -> None:
        self._agent_info = detect_agents()
        try:
            self.query_one("#agent-bar", Static).update(_agent_bar())
        except Exception:
            pass
        self._load_projects(self.query_one("#filter", Input).value)
        self.notify("refreshed", severity="information")

    def action_agent_prev(self) -> None:
        self._cycle_agent(-1)

    def action_agent_next(self) -> None:
        self._cycle_agent(1)

    def action_agent_n_1(self) -> None:
        self._agent_n(1)

    def action_agent_n_2(self) -> None:
        self._agent_n(2)

    def action_agent_n_3(self) -> None:
        self._agent_n(3)

    def action_agent_n_4(self) -> None:
        self._agent_n(4)

    def action_agent_n_5(self) -> None:
        self._agent_n(5)

    def action_agent_n_6(self) -> None:
        self._agent_n(6)

    def action_agent_n_7(self) -> None:
        self._agent_n(7)

    def action_open_project(self) -> None:
        p = self._selected()
        if not p:
            self.notify("no project selected", severity="warning")
            return
        if not p.exists():
            self.notify(f"path missing: {p.path} — press b to re-add", severity="error")
            return
        self._launch(p, p.default_agent, detach=False)

    def action_detach(self) -> None:
        p = self._selected()
        if not p:
            self.notify("no project selected", severity="warning")
            return
        if not p.exists():
            self.notify(f"path missing: {p.path}", severity="error")
            return
        self._launch(p, p.default_agent, detach=True)

    def action_pick_agent(self) -> None:
        """Pick agent, save as default, then launch."""
        p = self._selected()
        if not p:
            self.notify("select a project first", severity="warning")
            return
        from ccmd.tui.screens.agents import AgentScreen

        def _done(agent_id: str | None) -> None:
            if not agent_id:
                return
            p2 = self.registry.get(p.id) or p
            p2.default_agent = agent_id
            self.registry.save(p2)
            self._load_projects(self.query_one("#filter", Input).value)
            self._launch(p2, agent_id, detach=False)

        self.app.push_screen(AgentScreen(project=p, mode="launch"), _done)

    def action_set_agent_only(self) -> None:
        """Pick agent and save as default without launching."""
        p = self._selected()
        if not p:
            self.notify("select a project first", severity="warning")
            return
        from ccmd.tui.screens.agents import AgentScreen

        def _done(agent_id: str | None) -> None:
            if agent_id:
                self._set_default_agent(agent_id)

        self.app.push_screen(AgentScreen(project=p, mode="set"), _done)

    def action_new_project(self) -> None:
        from ccmd.tui.screens.project_edit import ProjectEditScreen

        def _done(ok: bool | None) -> None:
            if ok:
                self._load_projects(self.query_one("#filter", Input).value)

        self.app.push_screen(ProjectEditScreen(), _done)

    def action_browse(self) -> None:
        from ccmd.tui.screens.browser import DirBrowserScreen

        def _done(ok: bool | None) -> None:
            if ok:
                self._load_projects(self.query_one("#filter", Input).value)

        # start at home; roots list includes /mnt/*
        self.app.push_screen(DirBrowserScreen(start=Path.home()), _done)

    def action_browse_mnt(self) -> None:
        from ccmd.tui.screens.browser import DirBrowserScreen

        def _done(ok: bool | None) -> None:
            if ok:
                self._load_projects(self.query_one("#filter", Input).value)

        start = Path("/mnt")
        if not start.is_dir():
            start = Path.home()
            self.notify("/mnt not found — browsing home", severity="warning")
        self.app.push_screen(DirBrowserScreen(start=start), _done)

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

            def _do() -> None:
                try:
                    code = launch_project(
                        project, agent_id, detach=detach, replace=not detach
                    )
                    if detach:
                        self.notify(
                            f"launched {agent_id} (detached)", severity="information"
                        )
                    else:
                        self.notify(
                            f"{agent_id} exited ({code})", severity="information"
                        )
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


def _root_label(path: str) -> str:
    """Short badge for where the project lives.

    Uses angle brackets, not square ones — square brackets break Rich markup.
    """
    p = path.replace("\\", "/")
    if p.startswith("/mnt/vylth"):
        return "<vylth>"
    if p.startswith("/mnt/c"):
        return "<win-c>"
    if p.startswith("/mnt/d"):
        return "<win-d>"
    if p.startswith("/mnt/"):
        part = p.split("/")[2] if len(p.split("/")) > 2 else "mnt"
        return f"<mnt/{part}>"
    if p.startswith(str(Path.home())):
        return "<home>"
    if p.startswith("/opt"):
        return "<opt>"
    return "<disk>"
