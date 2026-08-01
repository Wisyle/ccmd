"""Session log for ccmd-spawned launches."""

from __future__ import annotations

import json
import os
import signal
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ccmd.config.paths import ensure_dirs, sessions_log


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Session:
    id: str
    project: str
    agent: str
    cwd: str
    pid: int | None
    detach: bool
    ts: str
    status: str = "running"  # running | exited | killed
    tmux_session: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        return cls(
            id=str(data["id"]),
            project=str(data.get("project") or ""),
            agent=str(data.get("agent") or ""),
            cwd=str(data.get("cwd") or ""),
            pid=data.get("pid"),
            detach=bool(data.get("detach", False)),
            ts=str(data.get("ts") or _now()),
            status=str(data.get("status") or "running"),
            tmux_session=data.get("tmux_session"),
        )


class SessionStore:
    def __init__(self, path: Path | None = None) -> None:
        ensure_dirs()
        self.path = path or sessions_log()

    def append(self, session: Session) -> Session:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(session.to_dict()) + "\n")
        try:
            self.path.chmod(0o600)
        except OSError:
            pass
        return session

    def create(
        self,
        project: str,
        agent: str,
        cwd: str,
        pid: int | None = None,
        detach: bool = False,
        tmux_session: str | None = None,
    ) -> Session:
        s = Session(
            id=uuid.uuid4().hex[:12],
            project=project,
            agent=agent,
            cwd=cwd,
            pid=pid,
            detach=detach,
            ts=_now(),
            tmux_session=tmux_session,
        )
        return self.append(s)

    def list(self, limit: int = 100) -> list[Session]:
        if not self.path.exists():
            return []
        rows: list[Session] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(Session.from_dict(json.loads(line)))
            except (json.JSONDecodeError, KeyError):
                continue
        # refresh live status
        for s in rows:
            if s.status == "running" and s.pid:
                if not _pid_alive(s.pid):
                    s.status = "exited"
        return list(reversed(rows[-limit:]))

    def kill(self, session_id: str) -> bool:
        sessions = self.list(limit=500)
        target = next((s for s in sessions if s.id == session_id), None)
        if not target or not target.pid:
            return False
        try:
            os.kill(target.pid, signal.SIGTERM)
            return True
        except (ProcessLookupError, PermissionError, OSError):
            return False


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False
    except OSError:
        return False
