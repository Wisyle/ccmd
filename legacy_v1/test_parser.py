"""Parser tests for CCMD.

Exercises CommandParser (ccmd/core/parser.py) against the merged
command set — including user-shortcut-driven go subcommands — to confirm
`go <shortcut>` resolves and `go <unknown>` falls back to search_dir.
"""
import pytest
from pathlib import Path

from ccmd.core.registry import CommandRegistry, create_default_config
from ccmd.core.parser import CommandParser


@pytest.fixture
def parser(tmp_path):
    """A parser over a freshly-seeded registry."""
    config = tmp_path / "commands.yaml"
    create_default_config(config)
    registry = CommandRegistry(config)
    return CommandParser(registry)


# ---------------------------------------------------------------------------
# go subcommand resolution
# ---------------------------------------------------------------------------
def test_go_builtin_subcommand_resolves(parser):
    name, sub, params = parser.parse(["go", "downloads"])
    assert name == "go"
    assert sub == "downloads"
    assert "error" not in params


def test_go_user_shortcut_subcommand_resolves(parser):
    """A user-added shortcut must resolve as a go subcommand via the merge."""
    parser.registry.add_shortcut("projects", "/home/u/projects")
    name, sub, params = parser.parse(["go", "projects"])
    assert name == "go"
    assert sub == "projects"
    assert "error" not in params


def test_go_unknown_name_sets_search_dir(parser):
    """An unknown second arg to 'go' is treated as a directory to search for,
    not an error."""
    name, sub, params = parser.parse(["go", "some-dir"])
    assert name == "go"
    assert sub is None
    assert params.get("search_dir") == "some-dir"
    assert "error" not in params


def test_go_with_no_args(parser):
    name, sub, params = parser.parse(["go"])
    assert name == "go"
    assert sub is None


# ---------------------------------------------------------------------------
# Other commands
# ---------------------------------------------------------------------------
def test_unknown_command_returns_error(parser):
    name, sub, params = parser.parse(["totally-fake"])
    assert name is None
    assert "error" in params


def test_empty_args_returns_none(parser):
    name, sub, params = parser.parse([])
    assert name is None and sub is None


def test_non_dict_action_command_passes_extra_args(parser):
    """A command whose action is a string should treat trailing args as params."""
    # 'push' has a string action in the default seed
    name, sub, params = parser.parse(["push", "fix", "the", "thing"])
    assert name == "push"
    assert sub is None  # no subcommand concept for string actions
    assert "error" not in params


def test_dict_action_unknown_subcommand_on_non_go_errors(parser):
    """For non-go dict-action commands, an unknown subcommand is an error
    (the search_dir fallback is go-specific)."""
    # Build a synthetic dict-action command that isn't 'go'
    parser.registry.add_command(
        "mydict",
        {
            "description": "dict action test",
            "action": {"only-key": "echo only"},
            "type": "custom",
        },
    )
    name, sub, params = parser.parse(["mydict", "wrong-key"])
    assert name == "mydict"
    assert sub is None
    assert "error" in params
