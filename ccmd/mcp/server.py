"""Minimal MCP-style stdio JSON-RPC tools (works without mcp SDK).

Protocol: newline-delimited JSON requests:
  {"id":1,"method":"tools/list"}
  {"id":2,"method":"tools/call","params":{"name":"projects.list","arguments":{}}}

If the `mcp` package is installed, prefer its server; else use this bridge
so agents can still talk to ccmd.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from ccmd.core.agents import detect_agents
from ccmd.core.launcher import LaunchError, launch_project
from ccmd.core.projects import ProjectRegistry
from ccmd.core.sessions import SessionStore
from ccmd.core.ssh import SSHStore


TOOLS = [
    {
        "name": "projects.list",
        "description": "List registered ccmd projects",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "projects.get",
        "description": "Get one project by id",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"],
        },
    },
    {
        "name": "agents.list",
        "description": "List agents and install status",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "agents.launch",
        "description": "Launch an agent on a project (detached)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "agent": {"type": "string"},
                "prompt": {"type": "string"},
            },
            "required": ["project"],
        },
    },
    {
        "name": "sessions.list",
        "description": "List ccmd sessions",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "sessions.kill",
        "description": "Kill a session by id",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"],
        },
    },
    {
        "name": "ssh.list",
        "description": "List SSH host profiles (no secrets)",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _call(name: str, args: dict[str, Any]) -> Any:
    if name == "projects.list":
        return [
            {
                "id": p.id,
                "name": p.name,
                "path": p.path,
                "default_agent": p.default_agent,
                "exists": p.exists(),
            }
            for p in ProjectRegistry().list()
        ]
    if name == "projects.get":
        p = ProjectRegistry().get(str(args["id"]))
        if not p:
            return {"error": "not found"}
        return {
            "id": p.id,
            "name": p.name,
            "path": p.path,
            "default_agent": p.default_agent,
            "ssh_host": p.ssh_host,
            "env_files": p.env_files,
        }
    if name == "agents.list":
        return detect_agents()
    if name == "agents.launch":
        p = ProjectRegistry().get(str(args["project"]))
        if not p:
            return {"error": "project not found"}
        agent = args.get("agent") or p.default_agent
        try:
            launch_project(
                p,
                agent,
                prompt=args.get("prompt"),
                detach=True,
                replace=False,
            )
            return {"ok": True, "project": p.id, "agent": agent}
        except LaunchError as e:
            return {"error": str(e)}
    if name == "sessions.list":
        return [s.to_dict() for s in SessionStore().list(50)]
    if name == "sessions.kill":
        return {"ok": SessionStore().kill(str(args["id"]))}
    if name == "ssh.list":
        return [
            {"id": h.id, "host": h.host, "user": h.user, "port": h.port}
            for h in SSHStore().list()
        ]
    return {"error": f"unknown tool {name}"}


def run_mcp_stdio() -> int:
    """Simple NDJSON tool bridge on stdin/stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            print(json.dumps({"error": "invalid json"}), flush=True)
            continue
        rid = req.get("id")
        method = req.get("method")
        if method == "tools/list":
            resp = {"id": rid, "result": {"tools": TOOLS}}
        elif method == "tools/call":
            params = req.get("params") or {}
            name = params.get("name")
            arguments = params.get("arguments") or {}
            result = _call(str(name), dict(arguments))
            resp = {
                "id": rid,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                },
            }
        elif method in ("initialize", "ping"):
            resp = {
                "id": rid,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "ccmd", "version": "2.0.0"},
                    "capabilities": {"tools": {}},
                },
            }
        else:
            resp = {"id": rid, "error": {"message": f"unknown method {method}"}}
        print(json.dumps(resp), flush=True)
    return 0
