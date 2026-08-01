"""Registry tests for CCMD.

Covers the default/custom two-layer merge plus the new user-shortcuts
merge into the 'go' command (v1.2.0). Uses isolated_home from conftest
so ~/.ccmd is never touched.
"""
import pytest
from pathlib import Path

from ccmd.core.registry import CommandRegistry, create_default_config


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def registry_with_defaults(tmp_path):
    """A registry backed by a freshly-seeded commands.yaml in tmp_path."""
    config = tmp_path / "commands.yaml"
    create_default_config(config)
    return CommandRegistry(config)


# ---------------------------------------------------------------------------
# Basic load + lookup
# ---------------------------------------------------------------------------
def test_default_config_has_go_shortcuts(registry_with_defaults):
    go = registry_with_defaults.get_command("go")
    assert go is not None
    assert "downloads" in go["action"]
    assert "documents" in go["action"]
    assert "home" in go["action"]


def test_get_unknown_command_returns_none(registry_with_defaults):
    assert registry_with_defaults.get_command("does-not-exist") is None


def test_command_exists(registry_with_defaults):
    assert registry_with_defaults.command_exists("go")
    assert not registry_with_defaults.command_exists("nope")


# ---------------------------------------------------------------------------
# Custom-command merge (existing two-layer behavior)
# ---------------------------------------------------------------------------
def test_custom_command_overrides_default(tmp_path):
    config = tmp_path / "commands.yaml"
    create_default_config(config)
    registry = CommandRegistry(config)

    registry.add_command(
        "go",
        {"description": "override", "action": {"x": "cd /x"}, "type": "navigation"},
        is_custom=True,
    )
    registry.save_custom_commands()

    # Fresh load: custom should win
    r2 = CommandRegistry(config)
    go = r2.get_command("go")
    assert go["action"] == {"x": "cd /x"}


def test_list_commands_includes_both_layers(registry_with_defaults):
    registry_with_defaults.add_command(
        "mine", {"description": "d", "action": "ls", "type": "custom"}, is_custom=True
    )
    names = registry_with_defaults.list_commands()
    assert "go" in names          # default
    assert "mine" in names        # custom


# ---------------------------------------------------------------------------
# User shortcuts (v1.2.0) — the new feature
# ---------------------------------------------------------------------------
def test_shortcut_merges_into_go(registry_with_defaults):
    """A user shortcut should appear in go's action dict as 'cd <path>'."""
    registry_with_defaults.add_shortcut("projects", "/home/u/projects")

    go = registry_with_defaults.get_command("go")
    assert "projects" in go["action"]
    assert go["action"]["projects"] == "cd /home/u/projects"


def test_default_shortcuts_preserved_after_user_shortcuts(registry_with_defaults):
    registry_with_defaults.add_shortcut("projects", "/home/u/projects")
    registry_with_defaults.add_shortcut("work", "/home/u/work")

    go = registry_with_defaults.get_command("go")
    # built-ins still present
    assert "downloads" in go["action"]
    assert "documents" in go["action"]
    assert "home" in go["action"]
    # user shortcuts present
    assert "projects" in go["action"]
    assert "work" in go["action"]


def test_user_shortcut_overrides_builtin_on_collision(registry_with_defaults):
    """If a user names a shortcut the same as a built-in, the user wins."""
    registry_with_defaults.add_shortcut("home", "/custom/home")

    go = registry_with_defaults.get_command("go")
    assert go["action"]["home"] == "cd /custom/home"


def test_shortcut_already_cd_form_kept(registry_with_defaults):
    """A shortcut whose value already starts with 'cd ' is stored verbatim."""
    registry_with_defaults.add_shortcut("stuff", "cd ~/stuff")

    go = registry_with_defaults.get_command("go")
    assert go["action"]["stuff"] == "cd ~/stuff"


def test_shortcut_persists_to_file(registry_with_defaults):
    registry_with_defaults.add_shortcut("persisted", "/home/u/p")

    # Reload from disk and confirm the shortcut survived.
    config_path = registry_with_defaults.config_path
    r2 = CommandRegistry(config_path)
    go = r2.get_command("go")
    assert "persisted" in go["action"]
    assert go["action"]["persisted"] == "cd /home/u/p"


def test_shortcuts_survive_reload(registry_with_defaults):
    registry_with_defaults.add_shortcut("a", "/a")
    registry_with_defaults.add_shortcut("b", "/b")

    registry_with_defaults.reload()
    go = registry_with_defaults.get_command("go")
    assert go["action"]["a"] == "cd /a"
    assert go["action"]["b"] == "cd /b"


def test_remove_shortcut_restores_builtin(registry_with_defaults):
    registry_with_defaults.add_shortcut("home", "/custom/home")
    assert registry_with_defaults.get_command("go")["action"]["home"] == "cd /custom/home"

    removed = registry_with_defaults.remove_shortcut("home")
    assert removed is True

    go = registry_with_defaults.get_command("go")
    # After removing the user override, the built-in home should return.
    assert go["action"]["home"] == "cd ~"


def test_remove_nonexistent_shortcut_returns_false(registry_with_defaults):
    assert registry_with_defaults.remove_shortcut("never-existed") is False


def test_list_user_shortcuts(registry_with_defaults):
    registry_with_defaults.add_shortcut("a", "/a")
    registry_with_defaults.add_shortcut("b", "/b")
    listing = registry_with_defaults.list_user_shortcuts()
    assert listing == {"a": "/a", "b": "/b"}
    # Returns a copy — mutating it must not affect the registry.
    listing["a"] = "/changed"
    assert registry_with_defaults.list_user_shortcuts()["a"] == "/a"


def test_no_shortcuts_go_unchanged(registry_with_defaults):
    """With no user shortcuts, get_command('go') returns the bare default."""
    go = registry_with_defaults.get_command("go")
    assert set(go["action"].keys()) == {"downloads", "documents", "desktop", "home"}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def test_validate_command_requires_action(tmp_path):
    registry = CommandRegistry(tmp_path / "commands.yaml")
    with pytest.raises(ValueError):
        registry.validate_command({"description": "no action"})


def test_validate_command_rejects_non_str_action(tmp_path):
    registry = CommandRegistry(tmp_path / "commands.yaml")
    with pytest.raises(ValueError):
        registry.validate_command({"action": 123})
