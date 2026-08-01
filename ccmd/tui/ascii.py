"""ASCII banners and glyphs."""

BANNER = r"""
   ██████╗ ██████╗███╗   ███╗██████╗
  ██╔════╝██╔════╝████╗ ████║██╔══██╗
  ██║     ██║     ██╔████╔██║██║  ██║
  ██║     ██║     ██║╚██╔╝██║██║  ██║
  ╚██████╗╚██████╗██║ ╚═╝ ██║██████╔╝
   ╚═════╝ ╚═════╝╚═╝     ╚═╝╚═════╝
"""

BANNER_COMPACT = "◇ ccmd · project hub"

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

AGENT_BOX = """\
┌──────────┐
│   {logo}    │
│ {name:^8} │
│ {status:^8} │
└──────────┘"""


def agent_tile(logo: str, name: str, installed: bool) -> str:
    status = "ready" if installed else "miss"
    short = name[:8]
    return AGENT_BOX.format(logo=logo, name=short, status=status)
