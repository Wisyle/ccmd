"""ccmd CLI entry — TUI by default, subcommands for scripts."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path  # noqa: F401 — used by project browse/add

from ccmd import __version__
from ccmd.config.paths import ensure_dirs, home
from ccmd.config.schema import load_config
from ccmd.core.agents import detect_agents, get_agent
from ccmd.core.launcher import LaunchError, connect_ssh, launch_project
from ccmd.core.migrate import apply_plan, build_plan
from ccmd.core.profiles import AliasStore
from ccmd.core.projects import ProjectRegistry
from ccmd.core.sessions import SessionStore
from ccmd.core.ssh import SSHStore


# Rich colors for agent columns / badges
_AGENT_STYLE = {
    "claude": "dark_orange3",
    "grok": "bright_white",
    "codex": "green",
    "cursor": "medium_purple",
    "goose": "yellow",
    "aider": "cyan",
    "chatgpt": "sea_green3",
}


def _agent_meta() -> list[dict]:
    """Logo + name + id for every agent (order matches variants)."""
    from ccmd.core.agents import all_agents

    return [
        {
            "id": a.id,
            "name": a.display_name,
            "logo": a.ascii_logo,
            "color": a.brand_color,
            "style": _AGENT_STYLE.get(a.id, "white"),
        }
        for a in all_agents()
    ]


def _print_cmd_rows(rows: list, *, verbose: bool = False) -> None:
    """Full ccmds view: base cmd + every agent variant with logo & name."""
    try:
        from rich import box
        from rich.console import Console
        from rich.table import Table
        from rich.text import Text

        console = Console(highlight=False)
        use_rich = True
    except Exception:
        use_rich = False

    if not rows:
        print("no matching commands")
        return

    agents = _agent_meta()

    if use_rich:
        console = Console(highlight=False)

        # legend once
        legend = Text()
        legend.append("agents  ", style="dim")
        for a in agents:
            legend.append(f"{a['logo']} ", style=a["style"])
            legend.append(f"{a['name']}", style=a["style"])
            legend.append("  ", style="dim")
        console.print(legend)
        console.print()

        table = Table(
            show_header=True,
            header_style="bold bright_cyan",
            border_style="bright_black",
            box=box.SIMPLE_HEAVY,
            pad_edge=False,
            expand=False,
            show_lines=False,
        )
        table.add_column("cmd", style="bold bright_cyan", no_wrap=True)
        table.add_column("project", style="white", no_wrap=True)
        table.add_column("default", style="magenta", no_wrap=True)
        for a in agents:
            # header: logo + short id
            hdr = Text()
            hdr.append(f"{a['logo']}\n", style=a["style"])
            hdr.append(a["id"][:6], style=f"dim {a['style']}")
            table.add_column(hdr, justify="center", no_wrap=True)
        if verbose:
            table.add_column("path", style="dim", overflow="ellipsis", max_width=36)

        for r in rows:
            cells: list = [
                Text(r["short"], style="bold bright_cyan"),
                Text(r["project"], style="white"),
                Text(r["default_agent"], style="magenta"),
            ]
            for a in agents:
                fn = r["variants"].get(a["id"], "")
                is_default = r["default_agent"] == a["id"]
                style = a["style"] if is_default else f"dim {a['style']}"
                # mark default with *
                label = f"{fn}*" if is_default and fn else fn
                cells.append(Text(label, style=style))
            if verbose:
                cells.append(Text(r["path"], style="dim"))
            table.add_row(*cells)

        console.print(table)
        console.print()
        console.print(
            f"[dim]{len(rows)} project(s)[/]  "
            f"[dim]·[/]  [bright_cyan]cmd[/][dim] = default agent[/]  "
            f"[dim]·[/]  [bright_cyan]*[/][dim] = project default[/]  "
            f"[dim]·[/]  [bright_cyan]ccmds ana[/][dim] filter[/]  "
            f"[dim]·[/]  [bright_cyan]ccmds -v[/][dim] show paths[/]"
        )
        return

    # plain fallback — still show all agent cmds
    headers = ["cmd", "project", "default"] + [a["id"][:6] for a in agents]
    print("  ".join(f"{h:<10}" for h in headers))
    print("-" * (12 * len(headers)))
    for r in rows:
        cols = [r["short"], r["project"], r["default_agent"]]
        for a in agents:
            cols.append(r["variants"].get(a["id"], ""))
        print("  ".join(f"{c:<10}" for c in cols))
        if verbose:
            print(f"           {r['path']}")
    print(f"\n{len(rows)} project(s)  ·  * default agent on project")


def _cmd_shell(args: argparse.Namespace) -> int:
    from ccmd.core.shell_cmds import (
        install_shell_hook,
        list_cmd_rows,
        write_shell_cmds,
    )

    sub = args.shell_cmd or "list"
    filt = getattr(args, "filter", None)
    verbose = bool(getattr(args, "verbose", False))

    if sub == "install":
        path, shorts = write_shell_cmds()
        rcs = install_shell_hook()
        print(f"wrote {path}")
        for rc in rcs:
            print(f"hooked {rc}")
        print("restart shell or:  source ~/.ccmd/shell_cmds.sh")
        print("then:  ccmds          # all cmds + agents with logos")
        print("       ccmds ana      # filter one project")
        print("       ana / anac / anag  …")
        if verbose:
            _print_cmd_rows(list_cmd_rows(), verbose=True)
        return 0
    if sub == "regen":
        path, shorts = write_shell_cmds()
        print(f"regenerated {path}  ({len(shorts)} projects)")
        _print_cmd_rows(list_cmd_rows(filter_text=filt), verbose=verbose)
        return 0
    if sub in ("list", "show"):
        _print_cmd_rows(list_cmd_rows(filter_text=filt), verbose=verbose)
        return 0
    print("usage: ccmd shell install|regen|list [--filter NAME] [-v]", file=sys.stderr)
    print("       ccmds              # full table with agent logos", file=sys.stderr)
    return 1


def _cmd_cmds(args: argparse.Namespace) -> int:
    """Top-level: ccmd cmds [name] [-v] — same as ccmds."""
    from ccmd.core.shell_cmds import list_cmd_rows

    filt = args.filter or args.name
    rows = list_cmd_rows(filter_text=filt)
    _print_cmd_rows(rows, verbose=bool(args.verbose))
    return 0


def _cmd_open(args: argparse.Namespace) -> int:
    reg = ProjectRegistry()
    project = reg.get(args.project)
    if not project:
        # try fuzzy
        hits = reg.fuzzy(args.project, limit=1)
        project = hits[0] if hits else None
    if not project:
        print(f"project not found: {args.project}", file=sys.stderr)
        return 1
    try:
        return launch_project(
            project,
            args.agent,
            prompt=args.prompt,
            detach=args.detach,
            replace=not args.detach and sys.stdin.isatty(),
        )
    except LaunchError as e:
        print(e, file=sys.stderr)
        return 2


def _cmd_list(args: argparse.Namespace) -> int:
    projects = ProjectRegistry().list()
    if args.json:
        print(json.dumps([p.to_dict() for p in projects], indent=2))
        return 0
    if not projects:
        print("no projects — try: ccmd project add  or  ccmd migrate --apply")
        return 0
    for p in projects:
        mark = "✓" if p.exists() else "!"
        print(f"{mark} {p.id:<20} {p.default_agent:<8} {p.path}")
    return 0


def _cmd_agents(args: argparse.Namespace) -> int:
    rows = detect_agents()
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    for a in rows:
        mark = "✓" if a["installed"] else "·"
        print(f"{mark} {a['logo']} {a['id']:<10} {a['name']:<16} {a['version'] or a['hint'][:40]}")
    return 0


def _cmd_sessions(args: argparse.Namespace) -> int:
    store = SessionStore()
    if args.kill:
        ok = store.kill(args.kill)
        print("killed" if ok else "failed")
        return 0 if ok else 1
    for s in store.list(50):
        print(f"{s.id}  {s.status:<8}  {s.project:<16}  {s.agent:<8}  pid={s.pid or s.tmux_session}")
    return 0


def _cmd_migrate(args: argparse.Namespace) -> int:
    plan = build_plan()
    print(f"projects to import: {len(plan.projects)}")
    for p in plan.projects[:20]:
        print(f"  · {p['id']:<16} agent={p.get('default_agent')} path={p.get('path')}")
    if len(plan.projects) > 20:
        print(f"  … +{len(plan.projects) - 20} more")
    print(f"aliases: {len(plan.aliases)}")
    for n in plan.notes[:10]:
        print(f"  note: {n}")
    if not args.apply:
        print("\ndry-run only. re-run with --apply to write.")
        return 0
    result = apply_plan(plan)
    print(f"created={result['created']} updated={result['updated']} aliases={result['aliases']}")
    return 0


def _cmd_project(args: argparse.Namespace) -> int:
    reg = ProjectRegistry()
    if args.project_cmd == "add":
        if not args.name or not args.path:
            print("usage: ccmd project add --name NAME --path PATH [--agent AGENT]", file=sys.stderr)
            return 1
        p = reg.add(name=args.name, path=args.path, default_agent=args.agent or "claude")
        print(f"added {p.id} -> {p.path}")
        return 0
    if args.project_cmd == "rm":
        ok = reg.delete(args.name)
        print("deleted" if ok else "not found")
        return 0 if ok else 1
    if args.project_cmd == "scan":
        from ccmd.core.scan import scan_roots

        rows = scan_roots(register=args.register, default_agent=args.agent or "claude")
        for r in rows:
            print(f"{r['name']:<24} {r['path']}  ({', '.join(r['markers'])})")
        print(f"{len(rows)} project-like dirs" + (" (registered new)" if args.register else ""))
        return 0
    if args.project_cmd == "browse":
        from ccmd.tui.app import CcmdApp
        from ccmd.tui.screens.browser import DirBrowserScreen

        class _BrowseApp(CcmdApp):
            def on_mount(self) -> None:
                def _done(ok: bool | None) -> None:
                    self.exit(0 if ok else 1)

                start = Path(args.path).expanduser() if args.path else None
                self.push_screen(DirBrowserScreen(start=start), _done)

        _BrowseApp().run()
        return 0
    print("usage: ccmd project add|rm|scan|browse", file=sys.stderr)
    return 1


def _cmd_ssh(args: argparse.Namespace) -> int:
    store = SSHStore()
    if args.ssh_cmd == "list" or args.ssh_cmd is None:
        for h in store.list():
            print(f"{h.id:<16} {h.user}@{h.host}:{h.port}")
        return 0
    if args.ssh_cmd == "import":
        hosts = store.import_ssh_config()
        print(f"imported {len(hosts)}")
        return 0
    if args.ssh_cmd == "connect":
        if not args.host:
            print("usage: ccmd ssh connect HOST_ID", file=sys.stderr)
            return 1
        try:
            return connect_ssh(args.host)
        except LaunchError as e:
            print(e, file=sys.stderr)
            return 2
    return 1


def _cmd_aliases(args: argparse.Namespace) -> int:
    store = AliasStore()
    if args.aliases_cmd == "import":
        found = store.import_from_bashrc()
        n = 0
        for name, cmd in found:
            if name not in store.aliases:
                store.set_alias(name, cmd)
                n += 1
        print(f"imported {n} aliases")
        return 0
    for name, cmd in sorted(store.aliases.items()):
        print(f"{name}={cmd}")
    if store.path_prepend:
        print("PATH+=" + ":".join(store.path_prepend))
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    ensure_dirs()
    cfg = load_config()
    print(f"ccmd {__version__}")
    print(f"home     {home()}")
    print(f"python   {sys.executable}")
    print(f"config   default_agent={cfg.default_agent}")
    print("agents:")
    for a in detect_agents():
        print(f"  {'✓' if a['installed'] else '·'} {a['id']:<10} {a['binary'] or a['hint'][:50]}")
    print(f"projects {len(ProjectRegistry().list())}")
    print(f"tmux     {shutil.which('tmux') or 'not found (detach uses background pid)'}")
    print(f"ssh      {shutil.which('ssh') or 'missing'}")
    legacy = home() / "custom_commands.yaml"
    if legacy.exists():
        print(f"legacy   {legacy} present — run: ccmd migrate --apply")
    return 0


def _cmd_mcp(args: argparse.Namespace) -> int:
    from ccmd.mcp.server import run_mcp_stdio

    return run_mcp_stdio()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ccmd",
        description="ccmd — Agentic Project Hub",
    )
    p.add_argument("--version", action="version", version=f"ccmd {__version__}")
    sub = p.add_subparsers(dest="cmd")

    open_p = sub.add_parser("open", help="Open project with agent")
    open_p.add_argument("project")
    open_p.add_argument("--agent", "-a")
    open_p.add_argument("--prompt", "-p")
    open_p.add_argument("--detach", "-d", action="store_true")

    list_p = sub.add_parser("list", help="List projects")
    list_p.add_argument("--json", action="store_true")

    agents_p = sub.add_parser("agents", help="Detect agents")
    agents_p.add_argument("--json", action="store_true")

    sess = sub.add_parser("sessions", help="List or kill sessions")
    sess.add_argument("--kill", metavar="ID")

    mig = sub.add_parser("migrate", help="Import ccmd 1.x config")
    mig.add_argument("--apply", action="store_true")

    proj = sub.add_parser("project", help="Manage projects")
    proj.add_argument("project_cmd", choices=["add", "rm", "scan", "browse"])
    proj.add_argument("--name")
    proj.add_argument("--path", help="browse start path, or add path")
    proj.add_argument("--agent")
    proj.add_argument("--register", action="store_true", help="scan: add found projects")

    ssh_p = sub.add_parser("ssh", help="SSH hosts")
    ssh_p.add_argument("ssh_cmd", nargs="?", choices=["list", "import", "connect"])
    ssh_p.add_argument("host", nargs="?")

    al = sub.add_parser("aliases", help="Aliases / PATH")
    al.add_argument("aliases_cmd", nargs="?", choices=["list", "import"])

    sub.add_parser("doctor", help="Environment diagnostics")
    sub.add_parser("mcp", help="Run MCP stdio server")
    sub.add_parser("tui", help="Force open TUI")

    sh = sub.add_parser(
        "shell",
        help="Short project commands (ana/anac/anag…) for bash/zsh",
    )
    sh.add_argument(
        "shell_cmd",
        nargs="?",
        choices=["install", "regen", "list", "show"],
        default="list",
        help="install|regen|list|show",
    )
    sh.add_argument(
        "--filter",
        "-f",
        dest="filter",
        help="filter by short/project/path (e.g. ana)",
    )
    sh.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show full agent variant map",
    )

    cmds = sub.add_parser(
        "cmds",
        help="List short shell commands (same as: ccmd shell list / ccmds)",
    )
    cmds.add_argument("name", nargs="?", help="filter (e.g. ana or flow)")
    cmds.add_argument("--filter", "-f", dest="filter", help="filter text")
    cmds.add_argument("-v", "--verbose", action="store_true")
    cmds.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="list all (default)",
    )

    return p


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    # no args or only flags that aren't subcommands → TUI
    if not argv or argv[0] in ("tui",):
        if argv and argv[0] == "tui":
            argv = argv[1:]
        ensure_dirs()
        from ccmd.tui.app import run_tui

        run_tui()
        return 0

    args = parser.parse_args(argv)
    ensure_dirs()
    handlers = {
        "open": _cmd_open,
        "list": _cmd_list,
        "agents": _cmd_agents,
        "sessions": _cmd_sessions,
        "migrate": _cmd_migrate,
        "project": _cmd_project,
        "ssh": _cmd_ssh,
        "aliases": _cmd_aliases,
        "doctor": _cmd_doctor,
        "mcp": _cmd_mcp,
        "shell": _cmd_shell,
        "cmds": _cmd_cmds,
    }
    handler = handlers.get(args.cmd)
    if not handler:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
