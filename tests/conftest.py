"""Shared pytest fixtures for CCMD tests.

Important: several CCMD modules read/write under ~/.ccmd/ (custom commands,
shortcuts, auth key, etc.). Tests must NOT touch the real user home, so we
point HOME (and USERPROFILE on Windows) at a per-test tmp_path before any
ccmd module is imported.
"""
import os
import sys
from pathlib import Path

import pytest

# Make the repo root importable so `import ccmd...` works whether or not
# the package is pip-installed. This mirrors run.py's sys.path.insert.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Redirect HOME/USERPROFILE to a temp dir so tests never touch the
    real ~/.ccmd. Also (re)load ccmd modules against the isolated home.
    """
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    # On Windows, Python's Path.home() consults USERPROFILE.
    monkeypatch.setenv("USERPROFILE", str(fake_home))
    yield fake_home
