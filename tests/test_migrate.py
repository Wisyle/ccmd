from pathlib import Path

import yaml

from ccmd.core.migrate import apply_plan, build_plan
from ccmd.core.projects import ProjectRegistry


def test_migrate_shortcuts_and_macros(ccmd_home: Path, tmp_path: Path) -> None:
    flow = tmp_path / "vylth-flow"
    flow.mkdir()
    shortcuts = ccmd_home / "shortcuts.yaml"
    shortcuts.write_text(
        yaml.safe_dump({"flow": str(flow), "lhs": str(tmp_path / "lhs")}),
        encoding="utf-8",
    )
    (tmp_path / "lhs").mkdir()
    custom = ccmd_home / "custom_commands.yaml"
    custom.write_text(
        yaml.safe_dump(
            {
                "commands": {
                    "flow": {
                        "action": "go flow >>> claude",
                        "type": "custom",
                    },
                    "here": {
                        "action": "ls -la",
                        "type": "custom",
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    plan = build_plan()
    assert any(p["id"] == "flow" for p in plan.projects)
    result = apply_plan(plan)
    assert result["created"] >= 1
    reg = ProjectRegistry()
    p = reg.get("flow")
    assert p is not None
    assert p.default_agent == "claude"
