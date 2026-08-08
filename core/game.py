"""Game data detection and management."""

import shutil
from pathlib import Path
from typing import Optional, Tuple


class GameDataLocator:
    """Locates 0 A.D. game data on the system."""
    
    @staticmethod
    def find_public_folder() -> Optional[Tuple[Path, bool]]:
        """
        Find the 0 A.D. public mod folder.
        
        Returns:
            Tuple of (path, is_zip) or None if not found
        """
        # Try to find public.zip in common locations
        common_paths = [
            Path.home() / "Library" / "Application Support" / "0ad" / "data" / "mods" / "public.zip",
            Path.home() / ".local" / "share" / "0ad" / "data" / "mods" / "public.zip",
            Path("/Applications/0ad.app/Contents/Resources/data/mods/public.zip"),
        ]
        
        for path in common_paths:
            if path.exists():
                return path, True
        
        # Try to find public folder
        folder_paths = [
            Path.home() / "Library" / "Application Support" / "0ad" / "data" / "mods" / "public",
            Path.home() / ".local" / "share" / "0ad" / "data" / "mods" / "public",
        ]
        
        for path in folder_paths:
            if path.exists() and path.is_dir():
                return path, False
        
        return None
    
    @staticmethod
    def get_user_mods_dir() -> Path:
        """Get the user mods directory for creating new mods."""
        paths = [
            Path.home() / "Library" / "Application Support" / "0ad" / "usermods",
            Path.home() / ".local" / "share" / "0ad" / "usermods",
        ]
        
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)
            return path
        
        # Fallback
        fallback = Path.home() / "0ad_mods"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback
