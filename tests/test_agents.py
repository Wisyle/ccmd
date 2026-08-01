from ccmd.core.agents import all_agents, detect_agents, get_agent


def test_catalog_has_seven() -> None:
    agents = all_agents()
    ids = {a.id for a in agents}
    assert ids == {"claude", "grok", "codex", "cursor", "goose", "aider", "chatgpt"}


def test_detect_runs() -> None:
    rows = detect_agents()
    assert len(rows) == 7
    assert get_agent("claude") is not None
