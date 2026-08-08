"""Application settings management."""

import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class AppSettings:
    """Manages application settings."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "0admodmaker"
        self.config_file = self.config_dir / "settings.json"
        self.data: Dict[str, Any] = {}
        self._load()
    
    def _load(self) -> None:
        """Load settings from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            self.data = {}
    
    def save(self) -> None:
        """Save settings to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self.data[key] = value
    
    @property
    def game_data_path(self) -> str:
        return self.get("game_data_path", "")
    
    @game_data_path.setter
    def game_data_path(self, value: str):
        self.set("game_data_path", value)
    
    @property
    def game_data_is_zip(self) -> bool:
        return self.get("game_data_is_zip", False)
    
    @game_data_is_zip.setter
    def game_data_is_zip(self, value: bool):
        self.set("game_data_is_zip", value)
    
    @property
    def last_mod_dir(self) -> str:
        return self.get("last_mod_dir", "")
    
    @last_mod_dir.setter
    def last_mod_dir(self, value: str):
        self.set("last_mod_dir", value)
    
    @property
    def projects_dir(self) -> Path:
        """Get the directory where .adcreator projects are stored."""
        dir_path = Path(self.get("projects_dir", ""))
        if not dir_path.exists():
            # Use Documents folder for easy access
            documents = Path.home() / "Documents" / "0 A.D. Mod Maker Projects"
            documents.mkdir(parents=True, exist_ok=True)
            self.projects_dir = str(documents)
            return documents
        return Path(dir_path)
    
    @projects_dir.setter
    def projects_dir(self, value: str):
        self.set("projects_dir", value)
    
    @property
    def recent_projects(self) -> List[Dict[str, Any]]:
        return self.get("recent_projects", [])
    
    def add_recent(self, path: str, label: str) -> None:
        """Add a project to recent projects."""
        recent = self.recent_projects
        
        # Remove if already exists
        recent = [r for r in recent if r.get("path") != path]
        
        # Add to front
        recent.insert(0, {
            "path": path,
            "label": label,
            "timestamp": int(time.time())
        })
        
        # Keep only last 10
        recent = recent[:10]
        
        self.set("recent_projects", recent)
    
    def clear_recent(self) -> None:
        """Clear all recent projects."""
        self.set("recent_projects", [])
