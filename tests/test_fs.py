from pathlib import Path

from ccmd.core.fs import default_browse_roots, is_projectish, list_dir_entries


def test_list_dir_entries(tmp_path: Path) -> None:
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "file.txt").write_text("x", encoding="utf-8")
    entries = list_dir_entries(tmp_path, dirs_only=True)
    names = {e[0] for e in entries}
    assert "a" in names
    assert "b" in names
    assert "node_modules" not in names
    assert "file.txt" not in names


def test_is_projectish(tmp_path: Path) -> None:
    assert not is_projectish(tmp_path)
    (tmp_path / ".git").mkdir()
    assert is_projectish(tmp_path)


def test_default_roots_include_home() -> None:
    roots = default_browse_roots()
    home = Path.home().resolve()
    assert any(r == home or home in r.parents or r == home for r in roots) or home in roots
