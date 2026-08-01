"""Launch builds argv lists — never shell strings from project name."""

from pathlib import Path
from unittest.mock import patch

import pytest

from ccmd.core.agents.claude import ClaudeAgent
from ccmd.core.agents.base import LaunchContext
from ccmd.core.launcher import LaunchError, launch_project
from ccmd.core.projects import Project


def test_claude_command_is_list(tmp_path: Path) -> None:
    ctx = LaunchContext(cwd=tmp_path, env={}, initial_prompt="hi")
    agent = ClaudeAgent()
    with patch.object(agent, "which", return_value="/usr/bin/claude"):
        cmd = agent.build_command(ctx)
    assert cmd == ["/usr/bin/claude", "-p", "hi"]
    assert all(isinstance(c, str) for c in cmd)


def test_launch_missing_path(ccmd_home, tmp_path: Path) -> None:
    p = Project(id="x", name="x", path=str(tmp_path / "nope"))
    with pytest.raises(LaunchError, match="does not exist"):
        launch_project(p, "claude", replace=False, detach=False)


def test_ssh_metacharacters_in_host_still_argv(ccmd_home) -> None:
    from ccmd.core.ssh import SSHHost

    # host field is one argv element — shell metachars not interpreted by us
    h = SSHHost(id="evil", host="evil.com;rm -rf /", user="u")
    argv = h.build_ssh_argv()
    assert argv[-1] == "u@evil.com;rm -rf /"
    assert len(argv) == 2  # ssh + target
