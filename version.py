"""Version information for AdCreator."""

from pathlib import Path
import re

# Read version from VERSION_HISTORY.md
VERSION_FILE = Path(__file__).parent / "VERSION_HISTORY.md"

def get_version() -> str:
    """Get the current version from VERSION_HISTORY.md."""
    if VERSION_FILE.exists():
        content = VERSION_FILE.read_text()
        # Find the first version line (e.g., "## Version 2.0.0")
        match = re.search(r'## Version (\d+\.\d+\.\d+)', content)
        if match:
            return match.group(1)
    return "1.0.0"

def set_version(version: str) -> None:
    """Set the version in VERSION_HISTORY.md (for use by update script)."""
    # This is mainly used by the update script to add new version entries
    pass

__version__ = get_version()
