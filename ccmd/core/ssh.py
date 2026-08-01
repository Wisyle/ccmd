"""SSH host profiles — paths only, never private key material."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ccmd.config.paths import ensure_dirs, ssh_hosts


@dataclass
class SSHHost:
    id: str
    host: str
    user: str = ""
    port: int = 22
    identity_file: str | None = None
    jump: str | None = None
    tags: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SSHHost:
        return cls(
            id=str(data["id"]),
            host=str(data["host"]),
            user=str(data.get("user") or ""),
            port=int(data.get("port") or 22),
            identity_file=data.get("identity_file"),
            jump=data.get("jump"),
            tags=list(data.get("tags") or []),
            notes=str(data.get("notes") or ""),
        )

    def build_ssh_argv(self) -> list[str]:
        cmd = ["ssh"]
        if self.port and self.port != 22:
            cmd.extend(["-p", str(self.port)])
        if self.identity_file:
            cmd.extend(["-i", str(Path(self.identity_file).expanduser())])
        if self.jump:
            cmd.extend(["-J", self.jump])
        target = f"{self.user}@{self.host}" if self.user else self.host
        cmd.append(target)
        return cmd


class SSHStore:
    def __init__(self, path: Path | None = None) -> None:
        ensure_dirs()
        self.path = path or ssh_hosts()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, SSHHost]:
        if not self.path.exists():
            return {}
        data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        hosts = data.get("hosts") or {}
        out: dict[str, SSHHost] = {}
        if isinstance(hosts, dict):
            for hid, body in hosts.items():
                if not isinstance(body, dict):
                    continue
                body = {**body, "id": hid}
                out[hid] = SSHHost.from_dict(body)
        return out

    def save_all(self, hosts: dict[str, SSHHost]) -> None:
        payload = {"hosts": {hid: h.to_dict() for hid, h in hosts.items()}}
        # strip id from nested to avoid duplication noise
        for hid, body in payload["hosts"].items():
            body.pop("id", None)
        self.path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        self.path.chmod(0o600)

    def list(self) -> list[SSHHost]:
        return sorted(self.load().values(), key=lambda h: h.id)

    def get(self, host_id: str) -> SSHHost | None:
        return self.load().get(host_id)

    def upsert(self, host: SSHHost) -> SSHHost:
        hosts = self.load()
        hosts[host.id] = host
        self.save_all(hosts)
        return host

    def delete(self, host_id: str) -> bool:
        hosts = self.load()
        if host_id not in hosts:
            return False
        del hosts[host_id]
        self.save_all(hosts)
        return True

    def import_ssh_config(self, config_path: Path | None = None) -> list[SSHHost]:
        path = config_path or (Path.home() / ".ssh" / "config")
        if not path.is_file():
            return []
        imported: list[SSHHost] = []
        current: dict[str, Any] | None = None
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            key, val = parts[0].lower(), parts[1].strip()
            if key == "host":
                if current and current.get("id") and "*" not in current["id"]:
                    imported.append(SSHHost.from_dict(current))
                name = val.split()[0]
                if "*" in name:
                    current = None
                    continue
                current = {"id": name, "host": name, "user": "", "port": 22}
            elif current is None:
                continue
            elif key == "hostname":
                current["host"] = val
            elif key == "user":
                current["user"] = val
            elif key == "port":
                try:
                    current["port"] = int(val)
                except ValueError:
                    pass
            elif key == "identityfile":
                current["identity_file"] = val
            elif key == "proxyjump":
                current["jump"] = val
        if current and current.get("id") and "*" not in current["id"]:
            imported.append(SSHHost.from_dict(current))
        # merge into store
        hosts = self.load()
        for h in imported:
            if h.id not in hosts:
                hosts[h.id] = h
        self.save_all(hosts)
        return imported

    def import_ssh_aliases(self, aliases: list[tuple[str, str]]) -> list[SSHHost]:
        """From (name, command) where command looks like ssh user@host."""
        pat = re.compile(
            r"^ssh\s+(?:-p\s+(\d+)\s+)?(?:-i\s+(\S+)\s+)?(?:([^\s@]+)@)?([^\s]+)\s*$"
        )
        hosts = self.load()
        added: list[SSHHost] = []
        for name, cmd in aliases:
            m = pat.match(cmd.strip())
            if not m:
                continue
            port_s, ident, user, host = m.groups()
            h = SSHHost(
                id=name,
                host=host,
                user=user or "",
                port=int(port_s) if port_s else 22,
                identity_file=ident,
            )
            if h.id not in hosts:
                hosts[h.id] = h
                added.append(h)
        self.save_all(hosts)
        return added
