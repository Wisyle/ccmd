"""Isolate HOME for tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture()
def ccmd_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "ccmd-home"
    home.mkdir()
    monkeypatch.setenv("CCMD_HOME", str(home))
    monkeypatch.setenv("HOME", str(tmp_path / "user"))
    (tmp_path / "user").mkdir(exist_ok=True)
    return home
