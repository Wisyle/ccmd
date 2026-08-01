"""Interactive directory browser — pick any folder as a project."""

from __future__ import annotations

from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Input, OptionList, Static
from textual.widgets.option_list import Option

from ccmd.config.schema import load_config
from ccmd.core.agents import all_agents, get_agent
from ccmd.core.fs import default_browse_roots, is_projectish, list_dir_entries
from ccmd.core.projects import ProjectRegistry

_AGENT_IDS = [a.id for a in all_agents()]


class DirBrowserScreen(Screen[bool | None]):
    """Browse the filesystem; select a directory to register as a project.

    Keys:
      enter     open directory / enter root
      backspace go up
      s / a     select highlighted (or current) dir as project
      r         jump to roots list
      .         toggle hidden
      /         focus filter
      esc       cancel
    """

    BINDINGS = [
        Binding("escape", "cancel", "Back", show=True),
        Binding("enter", "open_or_select", "Open", show=True),
        Binding("backspace", "up", "Up", show=True),
        Binding("s", "select", "Select", show=True),
        Binding("a", "select", "Add", show=False),
        Binding("r", "roots", "Roots", show=True),
        Binding("period", "toggle_hidden", "Hidden", show=True),
        Binding("slash", "focus_filter", "Filter", show=False),
        Binding("/", "focus_filter", "Filter", show=True),
        Binding("g", "go_path", "Go path", show=True),
        Binding("left_square_bracket", "agent_prev", "Agent−", show=True),
        Binding("right_square_bracket", "agent_next", "Agent+", show=True),
        Binding("1", "agent_n_1", show=False),
        Binding("2", "agent_n_2", show=False),
        Binding("3", "agent_n_3", show=False),
        Binding("4", "agent_n_4", show=False),
        Binding("5", "agent_n_5", show=False),
        Binding("6", "agent_n_6", show=False),
        Binding("7", "agent_n_7", show=False),
    ]

    def __init__(self, start: Path | None = None) -> None:
        super().__init__()
        self._mode: str = "browse"  # browse | roots | goto
        self._cwd: Path = (start or Path.home()).expanduser()
        try:
            self._cwd = self._cwd.resolve()
        except OSError:
            self._cwd = Path.home()
        self._show_hidden = False
        self._entries: list[tuple[str, Path, bool]] = []  # label, path, is_dir
        self._filter = ""
        self._agent = load_config().default_agent or "claude"

    def compose(self) -> ComposeResult:
        yield Static("directory browser", id="subtitle")
        yield Static("", id="path-bar")
        yield Input(placeholder="filter this folder…", id="filter")
        with Horizontal(id="main"):
            with Vertical(id="projects-panel"):
                yield Static("entries", classes="panel-title", id="list-title")
                yield OptionList(id="dir-list")
            with Vertical(id="detail-panel"):
                yield Static("preview", classes="panel-title")
                yield Static("", id="preview")
        yield Static(
            "↵ open · ⌫ up · s add project · ]/[ agent · 1-7 agent · r roots · g path · esc",
            id="footer-bar",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._render_list()
        self.query_one("#dir-list", OptionList).focus()

    # ── listing ──────────────────────────────────────────────

    def _set_path_bar(self, extra: str = "") -> None:
        bar = self.query_one("#path-bar", Static)
        mark = " · project?" if is_projectish(self._cwd) else ""
        hidden = " · hidden" if self._show_hidden else ""
        ag = get_agent(self._agent)
        ag_s = f"{ag.ascii_logo} {self._agent}" if ag else self._agent
        bar.update(
            f"[bold #00ffc8]{self._cwd}[/]{mark}{hidden}  ·  "
            f"agent [bold #c84bff]{ag_s}[/]"
            + (f"  [#6a6a80]{extra}[/]" if extra else "")
        )

    def _render_list(self) -> None:
        if self._mode == "roots":
            self._render_roots()
            return

        self._set_path_bar()
        self.query_one("#list-title", Static).update("directories")
        ol = self.query_one("#dir-list", OptionList)
        ol.clear_options()

        entries = list_dir_entries(
            self._cwd, show_hidden=self._show_hidden, dirs_only=True
        )
        q = self._filter.strip().lower()
        if q:
            entries = [e for e in entries if q in e[0].lower()]

        self._entries = []
        # parent always first when not at filesystem root
        if self._cwd.parent != self._cwd:
            self._entries.append(("..", self._cwd.parent, True))
            ol.add_option(Option("  ../", id="__parent__"))

        if not entries and not self._entries:
            ol.add_option(Option("  (empty)", id="__empty__"))
            self._update_preview(None)
            return

        for name, path, is_dir in entries:
            self._entries.append((name, path, is_dir))
            badge = "◆" if is_projectish(path) else "·"
            ol.add_option(Option(f"  {badge} {name}/", id=str(path)))

        ol.highlighted = 0
        self._update_preview(self._selected_path())

    def _render_roots(self) -> None:
        self._mode = "roots"
        self.query_one("#path-bar", Static).update(
            "[bold #c84bff]browse roots[/]  ·  pick a starting point"
        )
        self.query_one("#list-title", Static).update("roots")
        ol = self.query_one("#dir-list", OptionList)
        ol.clear_options()
        self._entries = []
        for root in default_browse_roots():
            self._entries.append((root.name or str(root), root, True))
            label = str(root)
            badge = "◆" if is_projectish(root) else "·"
            ol.add_option(Option(f"  {badge} {label}", id=str(root)))
        if not self._entries:
            ol.add_option(Option("  (no roots)", id="__empty__"))
        ol.highlighted = 0
        self._update_preview(self._selected_path())

    def _selected_path(self) -> Path | None:
        ol = self.query_one("#dir-list", OptionList)
        if ol.highlighted is None:
            return None
        try:
            opt = ol.get_option_at_index(ol.highlighted)
        except Exception:
            return None
        if opt.id in (None, "__empty__"):
            return None
        if opt.id == "__parent__":
            return self._cwd.parent
        return Path(str(opt.id))

    def _update_preview(self, path: Path | None) -> None:
        prev = self.query_one("#preview", Static)
        if path is None:
            prev.update("—")
            return
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        kids = list_dir_entries(resolved, show_hidden=self._show_hidden, dirs_only=True)
        project = is_projectish(resolved)
        lines = [
            f"[bold #00ffc8]{resolved.name or resolved}[/]",
            f"path     {resolved}",
            f"project  {'yes ◆' if project else 'no (still selectable)'}",
            f"subdirs  {len(kids)}",
            "",
            "[#6a6a80]children[/]",
        ]
        for name, _, _ in kids[:12]:
            lines.append(f"  · {name}/")
        if len(kids) > 12:
            lines.append(f"  … +{len(kids) - 12} more")
        lines.extend(
            [
                "",
                "[#6a6a80]↵ open folder · s select as project[/]",
            ]
        )
        prev.update("\n".join(lines))

    # ── events ───────────────────────────────────────────────

    @on(Input.Changed, "#filter")
    def on_filter(self, event: Input.Changed) -> None:
        self._filter = event.value
        if self._mode != "roots":
            self._render_list()

    @on(OptionList.OptionHighlighted)
    def on_highlight(self, event: OptionList.OptionHighlighted) -> None:
        self._update_preview(self._selected_path())

    @on(OptionList.OptionSelected)
    def on_select_event(self, event: OptionList.OptionSelected) -> None:
        self.action_open_or_select()

    # ── actions ──────────────────────────────────────────────

    def action_focus_filter(self) -> None:
        self.query_one("#filter", Input).focus()

    def action_toggle_hidden(self) -> None:
        self._show_hidden = not self._show_hidden
        self._render_list()

    def action_roots(self) -> None:
        self._filter = ""
        self.query_one("#filter", Input).value = ""
        self._render_roots()

    def action_up(self) -> None:
        if self._mode == "roots":
            return
        parent = self._cwd.parent
        if parent == self._cwd:
            self.notify("already at filesystem root", severity="warning")
            return
        self._cwd = parent
        self._filter = ""
        self.query_one("#filter", Input).value = ""
        self._render_list()

    def action_open_or_select(self) -> None:
        path = self._selected_path()
        if path is None:
            return
        if self._mode == "roots":
            self._mode = "browse"
            self._cwd = path
            self._filter = ""
            self.query_one("#filter", Input).value = ""
            self._render_list()
            return
        # open into directory
        if path.is_dir():
            self._cwd = path
            self._filter = ""
            self.query_one("#filter", Input).value = ""
            self._render_list()

    def action_agent_prev(self) -> None:
        try:
            i = _AGENT_IDS.index(self._agent)
        except ValueError:
            i = 0
        self._agent = _AGENT_IDS[(i - 1) % len(_AGENT_IDS)]
        self._set_path_bar()
        self.notify(f"agent → {self._agent}", severity="information", timeout=1)

    def action_agent_next(self) -> None:
        try:
            i = _AGENT_IDS.index(self._agent)
        except ValueError:
            i = 0
        self._agent = _AGENT_IDS[(i + 1) % len(_AGENT_IDS)]
        self._set_path_bar()
        self.notify(f"agent → {self._agent}", severity="information", timeout=1)

    def _agent_n(self, n: int) -> None:
        if 1 <= n <= len(_AGENT_IDS):
            self._agent = _AGENT_IDS[n - 1]
            self._set_path_bar()
            self.notify(f"agent → {self._agent}", severity="information", timeout=1)

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

    def action_select(self) -> None:
        """Register highlighted path, or current directory if nothing useful."""
        path = self._selected_path()
        # if on .. or empty, use cwd
        if path is None or (path == self._cwd.parent and self._mode == "browse"):
            path = self._cwd
        if not path or not path.is_dir():
            self.notify("not a directory", severity="error")
            return
        try:
            resolved = path.resolve()
        except OSError as e:
            self.notify(str(e), severity="error")
            return

        reg = ProjectRegistry()
        existing = reg.find_by_path(resolved)
        if existing:
            existing.default_agent = self._agent
            reg.save(existing)
            self.notify(
                f"already had {existing.id} — default agent → {self._agent}",
                severity="information",
            )
            self.dismiss(True)
            return

        name = resolved.name or str(resolved)
        p = reg.add(
            name=name,
            path=resolved,
            default_agent=self._agent,
            notes="added via browser",
        )
        self.notify(
            f"added {p.id} · agent {self._agent} → {resolved}",
            severity="information",
        )
        self.dismiss(True)

    def action_go_path(self) -> None:
        """Type an absolute/relative path and jump there."""
        self.app.push_screen(_GoPathModal(self._cwd), self._after_go)

    def _after_go(self, result: str | None) -> None:
        if not result:
            return
        path = Path(result).expanduser()
        if not path.is_dir():
            self.notify(f"not a directory: {result}", severity="error")
            return
        try:
            self._cwd = path.resolve()
        except OSError:
            self._cwd = path
        self._mode = "browse"
        self._filter = ""
        self.query_one("#filter", Input).value = ""
        self._render_list()

    def action_cancel(self) -> None:
        self.dismiss(False)


class _GoPathModal(Screen[str | None]):
    """Minimal path jump prompt."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
        Binding("enter", "submit", "Go", show=True),
    ]

    def __init__(self, cwd: Path) -> None:
        super().__init__()
        self._cwd = cwd

    def compose(self) -> ComposeResult:
        yield Static("go to path", id="subtitle")
        yield Input(value=str(self._cwd), id="path-input", placeholder="/home/you/project")
        yield Static("enter jump · esc cancel", id="footer-bar")

    def on_mount(self) -> None:
        inp = self.query_one("#path-input", Input)
        inp.focus()
        inp.cursor_position = len(inp.value)

    def action_submit(self) -> None:
        self.dismiss(self.query_one("#path-input", Input).value.strip())

    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Input.Submitted, "#path-input")
    def on_submit(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip())
