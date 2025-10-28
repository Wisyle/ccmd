#!/usr/bin/env python3
"""
CCMD Release Showcase Generator
Reads configuration from showcase_config.yaml and displays beautiful release information
Works for any version - just update the YAML file!
"""

import sys
import yaml
from pathlib import Path

# ANSI Color Codes
class Colors:
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'

    # Reset
    END = '\033[0m'

    @staticmethod
    def get_color(name):
        """Get color by name"""
        color_map = {
            'red': Colors.BRIGHT_RED,
            'green': Colors.BRIGHT_GREEN,
            'yellow': Colors.BRIGHT_YELLOW,
            'blue': Colors.BRIGHT_BLUE,
            'magenta': Colors.BRIGHT_MAGENTA,
            'cyan': Colors.BRIGHT_CYAN,
            'white': Colors.BRIGHT_WHITE,
        }
        return color_map.get(name.lower(), Colors.WHITE)


def load_config():
    """Load showcase configuration from YAML"""
    config_path = Path(__file__).parent / "showcase_config.yaml"

    if not config_path.exists():
        print(f"Error: {config_path} not found!")
        print("Please create showcase_config.yaml with your release information.")
        sys.exit(1)

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def print_header(config):
    """Print the showcase header"""
    version = config.get('version', 'Unknown')
    subtitle = config.get('subtitle', '')
    release_date = config.get('release_date', '')

    print()
    print(Colors.BOLD + Colors.BRIGHT_CYAN + "╔" + "═"*78 + "╗" + Colors.END)
    print(Colors.BOLD + Colors.BRIGHT_CYAN + "║" + " "*78 + "║" + Colors.END)

    title = f"CCMD v{version} — {subtitle}"
    padding = (78 - len(title)) // 2
    print(Colors.BOLD + Colors.BRIGHT_CYAN + "║" + " "*padding +
          Colors.BRIGHT_WHITE + title + Colors.BRIGHT_CYAN + " "*(78-padding-len(title)) + "║" + Colors.END)

    if release_date:
        date_text = f"Released {release_date}"
        padding = (78 - len(date_text)) // 2
        print(Colors.BOLD + Colors.BRIGHT_CYAN + "║" + " "*padding +
              Colors.BRIGHT_YELLOW + date_text + Colors.BRIGHT_CYAN + " "*(78-padding-len(date_text)) + "║" + Colors.END)

    print(Colors.BOLD + Colors.BRIGHT_CYAN + "║" + " "*78 + "║" + Colors.END)
    print(Colors.BOLD + Colors.BRIGHT_CYAN + "╚" + "═"*78 + "╝" + Colors.END)
    print()


def print_section_header(title, emoji):
    """Print a section header"""
    print()
    print(Colors.BOLD + Colors.BRIGHT_MAGENTA + f"┌─ {emoji} {title} " + "─"*(70-len(title)) + "┐" + Colors.END)
    print()


def print_feature(icon, title, description, example=""):
    """Print a feature with icon, title, and description"""
    print(Colors.BRIGHT_GREEN + f"  {icon} " + Colors.BOLD + Colors.WHITE + title + Colors.END)
    print(Colors.DIM + "    " + description + Colors.END)
    if example:
        print(Colors.CYAN + "    Example: " + Colors.BRIGHT_YELLOW + example + Colors.END)
    print()


def print_command_demo(command, description):
    """Print a command demonstration"""
    print(Colors.BRIGHT_BLUE + "  $ " + Colors.BRIGHT_WHITE + Colors.BOLD + command + Colors.END)
    print(Colors.DIM + "    → " + description + Colors.END)
    print()


def print_security_fix(number, title, description):
    """Print a security fix"""
    print(Colors.BRIGHT_RED + f"  [{number}] " + Colors.BOLD + Colors.WHITE + title + Colors.END)
    print(Colors.DIM + "      " + description + Colors.END)
    print()


def print_improvement(title, description):
    """Print a technical improvement"""
    print(Colors.BRIGHT_YELLOW + "  ✓ " + Colors.BOLD + Colors.WHITE + title + Colors.END)
    print(Colors.DIM + "    " + description + Colors.END)
    print()


def print_sections(sections):
    """Print all feature sections"""
    for section in sections:
        title = section.get('title', 'Section')
        emoji = section.get('emoji', '📦')
        section_type = section.get('type', 'features')

        print_section_header(title, emoji)

        if section_type == 'features':
            # Regular features with icon, title, description, example
            for feature in section.get('features', []):
                print_feature(
                    feature.get('icon', '•'),
                    feature.get('title', ''),
                    feature.get('description', ''),
                    feature.get('example', '')
                )

        elif section_type == 'commands':
            # Command demonstrations
            for item in section.get('items', []):
                print_command_demo(
                    item.get('command', ''),
                    item.get('description', '')
                )

        elif section_type == 'security':
            # Security fixes
            for item in section.get('items', []):
                print_security_fix(
                    item.get('number', 1),
                    item.get('title', ''),
                    item.get('description', '')
                )

        elif section_type == 'improvements':
            # Technical improvements
            for item in section.get('items', []):
                print_improvement(
                    item.get('title', ''),
                    item.get('description', '')
                )

        # Close section
        if section_type in ['improvements']:
            print(Colors.BOLD + Colors.BRIGHT_MAGENTA + "└" + "─"*78 + "┘" + Colors.END)


def print_statistics(stats):
    """Print release statistics"""
    if not stats:
        return

    print()
    print(Colors.BOLD + Colors.BRIGHT_CYAN + "┌─ 📊 Release Statistics " + "─"*53 + "┐" + Colors.END)
    print()

    # Print in pairs
    for i in range(0, len(stats), 2):
        line = "  "
        for j in range(2):
            if i + j < len(stats):
                stat = stats[i + j]
                label = stat.get('label', '')
                value = stat.get('value', '')
                color = Colors.get_color(stat.get('color', 'white'))

                line += f"{Colors.WHITE}{label}: {color}{Colors.BOLD}{value}{Colors.END}    "
        print(line)
        print()

    print(Colors.BOLD + Colors.BRIGHT_CYAN + "└" + "─"*78 + "┘" + Colors.END)


def print_footer(footer, version):
    """Print footer with badges, links, and credits"""
    print()

    # Badges
    for badge in footer.get('badges', []):
        print(Colors.BOLD + Colors.BRIGHT_GREEN + f"  ✓ {badge.get('text', '')}" + Colors.END)

    print()

    # Links
    links = footer.get('links', {})
    if 'download' in links:
        print(Colors.BOLD + Colors.BRIGHT_CYAN + "  Download: " +
              Colors.BRIGHT_WHITE + links['download'] + Colors.END)
    if 'docs' in links:
        print(Colors.BOLD + Colors.BRIGHT_CYAN + "  Docs:     " +
              Colors.BRIGHT_WHITE + links['docs'] + Colors.END)

    print()

    # Credits
    credits = footer.get('credits', {})
    developer = credits.get('developer', '')
    license_text = credits.get('license', '')
    warning = credits.get('warning', '')

    if developer or license_text:
        print(Colors.BRIGHT_BLACK + f"  {developer} • {license_text}" + Colors.END)
    if warning:
        print(Colors.BRIGHT_BLACK + f"  {warning}" + Colors.END)

    print()


def main():
    """Main showcase function"""
    try:
        # Load configuration
        config = load_config()

        # Print header
        print_header(config)

        # Print all sections
        sections = config.get('sections', [])
        print_sections(sections)

        # Print statistics
        stats = config.get('statistics', [])
        print_statistics(stats)

        # Print footer
        footer = config.get('footer', {})
        version = config.get('version', 'Unknown')
        print_footer(footer, version)

    except Exception as e:
        print(f"{Colors.BRIGHT_RED}Error: {e}{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        sys.exit(0)
