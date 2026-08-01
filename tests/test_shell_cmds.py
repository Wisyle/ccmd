from pathlib import Path

from ccmd.core.projects import Project, ProjectRegistry
from ccmd.core.shell_cmds import (
    AGENT_SUFFIX,
    allocate_shorts,
    render_shell_cmds,
    short_candidates,
    write_shell_cmds,
)


def test_short_candidates_anastasis() -> None:
    c = short_candidates("anastasis", "anastasis")
    assert "ana" in c or "anastasis" in c


def test_allocate_unique(ccmd_home: Path) -> None:
    projects = [
        Project(id="anastasis", name="anastasis", path="/tmp/a"),
        Project(id="analytics", name="analytics", path="/tmp/b"),
        Project(id="flow", name="flow", path="/tmp/c"),
    ]
    shorts = allocate_shorts(projects)
    assert len(set(shorts.values())) == 3
    assert all(s[0].isalpha() for s in shorts.values())


def test_render_contains_agent_variants(ccmd_home: Path) -> None:
    p = Project(id="anastasis", name="anastasis", path="/tmp/a", default_agent="claude")
    shorts = {"anastasis": "ana"}
    text = render_shell_cmds([p], shorts)
    assert "ana() {" in text
    assert "anac() {" in text
    assert "anag() {" in text
    assert "anax() {" in text
    assert "--agent claude" in text
    assert "--agent grok" in text
    assert "ccmd open anastasis" in text


def test_write_persists_short(ccmd_home: Path, tmp_path: Path) -> None:
    proj = tmp_path / "myapp"
    proj.mkdir()
    reg = ProjectRegistry()
    p = reg.add(name="myapp", path=proj, default_agent="grok")
    path, shorts = write_shell_cmds()
    assert path.exists()
    body = path.read_text(encoding="utf-8")
    assert "ccmd open" in body
    assert "ccmds()" in body
    p2 = reg.get(p.id)
    assert p2 is not None
    assert p2.short
    # agent suffix functions exist for short
    assert f"{p2.short}c() {{" in body or f"{p2.short}g() {{" in body
    assert p2.id in shorts


def test_cmds_notice(ccmd_home: Path, tmp_path: Path) -> None:
    from ccmd.core.shell_cmds import cmds_notice

    proj = tmp_path / "anastasis"
    proj.mkdir()
    p = ProjectRegistry().add(name="anastasis", path=proj)
    p = ProjectRegistry().get(p.id) or p
    msg = cmds_notice(p)
    assert "cmds:" in msg
    assert "ccmds" in msg
    assert p.short in msg


def test_agent_suffix_map_complete() -> None:
    for a in ("claude", "grok", "codex", "cursor", "goose", "aider", "chatgpt"):
        assert a in AGENT_SUFFIX
