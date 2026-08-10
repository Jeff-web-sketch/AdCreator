"""Persistent settings storage for the 0 A.D. Mod Maker."""

import json
import logging
import platform
from pathlib import Path
from typing import Optional, List

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class AppSettings:
    """Load and save application settings to a JSON file."""

    DEFAULTS = {
        "game_data_path": "",
        "game_data_is_zip": False,
        "last_mod_dir": "",
        "recent_projects": [],  # List of dicts: {"path", "label", "timestamp"}
        "window_width": 1100,
        "window_height": 720,
    }

    MAX_RECENT = 10

    def __init__(self):
        self.settings_dir = self._get_settings_dir()
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.settings_dir / "modmaker_settings.json"
        self.data: dict = dict(self.DEFAULTS)
        self.load()

    @staticmethod
    def _get_settings_dir() -> Path:
        """Return the platform-appropriate config directory."""
        system = platform.system()
        if system == "Windows":
            return Path.home() / "Documents" / "My Games" / "0ad" / "modmaker"
        elif system == "Darwin":
            return Path.home() / "Library" / "Application Support" / "0ad" / "modmaker"
        else:
            return Path.home() / ".local" / "share" / "0ad" / "modmaker"

    def load(self):
        """Load settings from disk if they exist."""
        if self.settings_file.is_file():
            try:
                with open(self.settings_file) as f:
                    loaded = json.load(f)
                self.data.update(loaded)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load settings from {self.settings_file}: {e}")
                # Use defaults if file is corrupted

    def save(self):
        """Persist current settings to disk."""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.data, f, indent=4)
        except IOError as e:
            logger.warning(f"Failed to save settings to {self.settings_file}: {e}")

    def get(self, key: str, default=None) -> any:
        """Get a setting value with optional default."""
        return self.data.get(key, default if default is not None else self.DEFAULTS.get(key))

    def set(self, key: str, value: any) -> None:
        """Set a setting value."""
        self.data[key] = value

    @property
    def game_data_path(self) -> str:
        return self.data.get("game_data_path", "")

    @game_data_path.setter
    def game_data_path(self, v: str):
        self.data["game_data_path"] = v

    @property
    def game_data_is_zip(self) -> bool:
        return self.data.get("game_data_is_zip", False)

    @game_data_is_zip.setter
    def game_data_is_zip(self, v: bool):
        self.data["game_data_is_zip"] = v

    @property
    def last_mod_dir(self) -> str:
        return self.data.get("last_mod_dir", "")

    @last_mod_dir.setter
    def last_mod_dir(self, v: str):
        self.data["last_mod_dir"] = v

    @property
    def recent_projects(self) -> list:
        return self.data.get("recent_projects", [])

    def add_recent(self, path: str, label: str):
        """Add a project to recent list, deduplicate, limit count."""
        import time
        recent = self.data.get("recent_projects", [])
        
        # Remove if already exists
        recent = [r for r in recent if r.get("path") != path]
        
        # Add new entry at front
        recent.insert(0, {
            "path": path,
            "label": label,
            "timestamp": int(time.time()),
        })
        
        # Trim to max
        recent = recent[:self.MAX_RECENT]
        self.data["recent_projects"] = recent
        self.save()

    def remove_recent(self, path: str):
        """Remove a project from recent list."""
        recent = self.data.get("recent_projects", [])
        recent = [r for r in recent if r.get("path") != path]
        self.data["recent_projects"] = recent
        self.save()