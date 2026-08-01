"""Safe agent launch — argv lists only, no shell=True for untrusted strings."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from ccmd.core.agents import LaunchContext, get_agent
from ccmd.core.profiles import AliasStore, merge_project_env
from ccmd.core.projects import Project, ProjectRegistry
from ccmd.core.sessions import SessionStore
from ccmd.core.ssh import SSHStore


class LaunchError(Exception):
    pass


def launch_project(
    project: Project,
    agent_id: str | None = None,
    *,
    prompt: str | None = None,
    extra_args: list[str] | None = None,
    detach: bool = False,
    replace: bool = True,
) -> int:
    """Launch agent in project cwd.

    replace=True: os.execvpe (hands TTY to agent, never returns).
    detach=True: tmux session if available, else background subprocess.
    """
    agent_id = agent_id or project.default_agent or "claude"
    agent = get_agent(agent_id)
    if not agent:
        raise LaunchError(f"Unknown agent: {agent_id}")

    cwd = project.resolved_path()
    if not cwd.is_dir():
        raise LaunchError(f"Project path does not exist: {cwd}")

    env = merge_project_env(project)

    # Optional SSH note only — tunnel support: if ssh_host set we don't block launch
    # (connect is separate). Could open tunnel later.

    ctx = LaunchContext(
        cwd=cwd,
        env=env,
        extra_args=list(extra_args or []),
        initial_prompt=prompt,
        session_label=project.id,
        detach=detach,
    )

    if agent_id == "chatgpt":
        from ccmd.core.agents.chatgpt import ChatGPTAgent

        ChatGPTAgent().open(ctx)
        SessionStore().create(
            project=project.id, agent=agent_id, cwd=str(cwd), pid=None, detach=True
        )
        ProjectRegistry().touch_opened(project.id)
        return 0

    try:
        cmd = agent.build_command(ctx)
    except FileNotFoundError as e:
        raise LaunchError(str(e)) from e

    # optional alias wrapper for interactive shell agents — only if aliases configured
    store = AliasStore()
    if project.aliases or store.aliases:
        wrapper = store.write_wrapper_script(project, cmd, env)
        cmd = ["bash", str(wrapper)]

    sessions = SessionStore()
    registry = ProjectRegistry()
    registry.touch_opened(project.id)

    if detach:
        return _detach_launch(cmd, cwd, env, project.id, agent_id, sessions)

    if replace and sys.stdin.isatty():
        # record session with unknown pid (replaced)
        sessions.create(
            project=project.id, agent=agent_id, cwd=str(cwd), pid=os.getpid(), detach=False
        )
        os.chdir(cwd)
        os.execvpe(cmd[0], cmd, env)

    # non-replace: run and wait
    proc = subprocess.Popen(cmd, cwd=str(cwd), env=env)  # noqa: S603
    sessions.create(
        project=project.id, agent=agent_id, cwd=str(cwd), pid=proc.pid, detach=False
    )
    return proc.wait()


def _detach_launch(
    cmd: list[str],
    cwd: Path,
    env: dict[str, str],
    project_id: str,
    agent_id: str,
    sessions: SessionStore,
) -> int:
    tmux = shutil.which("tmux")
    name = f"ccmd-{project_id}-{agent_id}"[:40]
    if tmux:
        # tmux new-session -d -s name -c cwd cmd...
        argv = [tmux, "new-session", "-d", "-s", name, "-c", str(cwd), "--", *cmd]
        subprocess.run(argv, env=env, check=False)  # noqa: S603
        sessions.create(
            project=project_id,
            agent=agent_id,
            cwd=str(cwd),
            pid=None,
            detach=True,
            tmux_session=name,
        )
        print(f"Detached: tmux attach -t {name}")
        return 0

    proc = subprocess.Popen(  # noqa: S603
        cmd,
        cwd=str(cwd),
        env=env,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    sessions.create(
        project=project_id, agent=agent_id, cwd=str(cwd), pid=proc.pid, detach=True
    )
    print(f"Background pid {proc.pid}")
    return 0


def connect_ssh(host_id: str) -> int:
    host = SSHStore().get(host_id)
    if not host:
        raise LaunchError(f"Unknown SSH host: {host_id}")
    cmd = host.build_ssh_argv()
    if sys.stdin.isatty():
        os.execvp(cmd[0], cmd)
    return subprocess.call(cmd)  # noqa: S603
