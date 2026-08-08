"""Version information for AdCreator."""

from pathlib import Path

# Read version from VERSION file
VERSION_FILE = Path(__file__).parent / "VERSION"

def get_version() -> str:
    """Get the current version from VERSION file."""
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return "1.0.0"

def set_version(version: str) -> None:
    """Set the version in VERSION file."""
    VERSION_FILE.write_text(version.strip())

__version__ = get_version()
