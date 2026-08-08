"""Auto-detect the 0 A.D. installation on the local machine."""

import os
import zipfile
import platform
from pathlib import Path
from typing import Optional, Tuple, List

class GameDataLocator:
    """Locate the 0 A.D. public mod folder (folder or public.zip)."""

    REL_PUBLIC = "binaries/data/mods/public"
    PUBLIC_ZIP_NAME = "public.zip"

    @staticmethod
    def candidate_paths() -> List[Path]:
        """Return a list of candidate paths where 0 A.D. might be installed."""
        candidates: List[Path] = []
        system = platform.system()

        if system == "Windows":
            program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
            program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
            local_appdata = os.environ.get("LOCALAPPDATA", "")

            for pf in [program_files, program_files_x86]:
                candidates.append(Path(pf) / "0 A.D.")
            candidates.append(Path(local_appdata) / "itch" / "apps" / "0 A.D.")
            candidates.append(Path(program_files) / "0ad")

        elif system == "Darwin":
            candidates.append(Path("/Applications/0 A.D..app/Contents/Resources"))
            candidates.append(Path("/Applications/0ad.app/Contents/Resources"))

        else:
            candidates.extend([
                Path("/usr/share/0ad"),
                Path("/usr/local/share/0ad"),
                Path("/opt/0ad"),
                Path("/snap/0ad/current"),
                Path.home() / ".local" / "share" / "0ad",
                Path.home() / "games" / "0ad",
            ])

        env_path = os.environ.get("ZEROAD_ROOT")
        if env_path:
            candidates.insert(0, Path(env_path))

        return candidates

    @staticmethod
    def find_public_folder() -> Optional[Tuple[Path, bool]]:
        """Try to locate the public mod folder or public.zip.
        Returns (path, is_zip) tuple or None if not found."""
        for base in GameDataLocator.candidate_paths():
            # First check if it's a ZIP file
            zip_path = base / GameDataLocator.PUBLIC_ZIP_NAME
            if zip_path.is_file():
                return (zip_path, True)

            # Check folder path
            public = base / GameDataLocator.REL_PUBLIC
            if public.is_dir() and GameDataLocator.validate_public_folder(public):
                return (public, False)

        return None

    @staticmethod
    def validate_public_folder(path: Path) -> bool:
        """Check that a given path looks like the 0 A.D. public mod folder."""
        return path.is_dir() and (path / "simulation").is_dir()

    @staticmethod
    def validate_public_zip(zip_path: Path) -> bool:
        """Check that a public.zip file contains valid 0 A.D. data."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Check for key directories that should exist in the root
                test_paths = [
                    'simulation/',
                    'art/',
                    'audio/',
                    'gui/',
                    'maps/'
                ]
                names = set(n.split('/')[0] + '/' for n in zf.namelist())
                for test in test_paths:
                    if not any(test in n for n in names):
                        return False
                return True
        except zipfile.BadZipFile:
            return False

    @staticmethod
    def get_user_mods_dir() -> Path:
        """Return the default user mods directory for the current platform."""
        system = platform.system()
        if system == "Windows":
            return Path.home() / "Documents" / "My Games" / "0ad" / "mods"
        elif system == "Darwin":
            return Path.home() / "Library" / "Application Support" / "0ad" / "mods"
        else:
            return Path.home() / ".local" / "share" / "0ad" / "mods"