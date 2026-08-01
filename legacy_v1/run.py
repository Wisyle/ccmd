#!/usr/bin/env python3
"""
CCMD - Cross-platform Command Manager
Main entry point for command execution
"""

import sys
from pathlib import Path

# Add the ccmd package to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from ccmd.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
