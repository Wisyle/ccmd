"""Agent catalog."""

from __future__ import annotations

from ccmd.core.agents.aider import AiderAgent
from ccmd.core.agents.base import AgentAdapter, BaseAgent, LaunchContext
from ccmd.core.agents.chatgpt import ChatGPTAgent
from ccmd.core.agents.claude import ClaudeAgent
from ccmd.core.agents.codex import CodexAgent
from ccmd.core.agents.cursor import CursorAgent
from ccmd.core.agents.goose import GooseAgent
from ccmd.core.agents.grok import GrokAgent

_AGENTS: list[BaseAgent] = [
    ClaudeAgent(),
    GrokAgent(),
    CodexAgent(),
    CursorAgent(),
    GooseAgent(),
    AiderAgent(),
    ChatGPTAgent(),
]


def all_agents() -> list[BaseAgent]:
    return list(_AGENTS)


def get_agent(agent_id: str) -> BaseAgent | None:
    for a in _AGENTS:
        if a.id == agent_id:
            return a
    return None


def detect_agents() -> list[dict]:
    rows = []
    for a in _AGENTS:
        installed = a.is_installed()
        rows.append(
            {
                "id": a.id,
                "name": a.display_name,
                "installed": installed,
                "version": a.version() if installed or a.id == "chatgpt" else None,
                "color": a.brand_color,
                "logo": a.ascii_logo,
                "hint": a.install_hint(),
                "binary": a.which() if hasattr(a, "which") else None,
            }
        )
    return rows


__all__ = [
    "AgentAdapter",
    "BaseAgent",
    "LaunchContext",
    "all_agents",
    "get_agent",
    "detect_agents",
]
