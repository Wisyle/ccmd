from pathlib import Path

from ccmd.core.projects import ProjectRegistry


def test_add_list_get(ccmd_home: Path, tmp_path: Path) -> None:
    proj_dir = tmp_path / "myapp"
    proj_dir.mkdir()
    reg = ProjectRegistry()
    p = reg.add(name="My App", path=proj_dir, default_agent="claude")
    assert p.id == "my-app"
    assert reg.get(p.id) is not None
    assert len(reg.list()) == 1
    assert reg.list()[0].exists()


def test_fuzzy(ccmd_home: Path, tmp_path: Path) -> None:
    a = tmp_path / "vylth-flow"
    a.mkdir()
    b = tmp_path / "decatalyst"
    b.mkdir()
    reg = ProjectRegistry()
    reg.add(name="Vylth Flow", path=a, project_id="vylth-flow")
    reg.add(name="De Catalyst", path=b, project_id="decatalyst")
    hits = reg.fuzzy("flow")
    assert hits
    assert hits[0].id == "vylth-flow"
