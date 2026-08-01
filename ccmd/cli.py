"""ccmd CLI entry — TUI by default, subcommands for scripts."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

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
    print("usage: ccmd project add|rm|scan", file=sys.stderr)
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
    proj.add_argument("project_cmd", choices=["add", "rm", "scan"])
    proj.add_argument("--name")
    proj.add_argument("--path")
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
    }
    handler = handlers.get(args.cmd)
    if not handler:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
