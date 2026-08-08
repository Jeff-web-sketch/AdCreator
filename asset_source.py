"""Browse and read files from the local 0 A.D. public mod folder (or ZIP)."""

import os
import zipfile
import logging
from pathlib import Path
from typing import Optional, List, Dict, Union, Any

logger = logging.getLogger(__name__)

class FakePath:
    """Minimal Path-like object for display purposes with ZIP/folder compatibility."""
    def __init__(self, full_path: str, name: str):
        self.full_path = full_path
        self.name = name
        self.suffix = Path(name).suffix
    
    def rglob(self, pattern): 
        return []
    
    def __lt__(self, other):
        return self.name < other.name
    
    def __eq__(self, other):
        if not isinstance(other, (FakePath, str)):
            return False
        return self.name == (other.name if isinstance(other, FakePath) else other)
    
    def __hash__(self):
        return hash(self.name)

class FileExtensions:
    """File extension constants for asset types."""
    MESHES = {".dae", ".pmd", ".psa"}
    TEXTURES = {".png", ".dds", ".tga", ".jpg", ".jpeg"}
    XML = {".xml"}

class LocalAssetSource:
    """Browse files from the local 0 A.D. installation (folder or public.zip)."""

    SUB_TEMPLATES = "simulation/templates"
    SUB_UNITS = "simulation/templates/units"
    SUB_ART_MESHES = "art/meshes"
    SUB_ART_TEXTURES = "art/textures"
    SUB_ART_ACTORS = "art/actors"
    SUB_SIM_DATA = "simulation/data"

    def __init__(self, public_path: Path, is_zip: bool = False):
        """
        Args:
            public_path: Path to public folder OR public.zip
            is_zip: Whether the path points to a ZIP file
        """
        self.root = Path(public_path)
        self.is_zip = is_zip
        self.zip_handle: Optional[zipfile.ZipFile] = None
        
        if is_zip:
            if not self.root.is_file():
                raise FileNotFoundError(f"Public ZIP not found: {self.root}")
            try:
                self.zip_handle = zipfile.ZipFile(self.root, 'r')
            except zipfile.BadZipFile:
                raise FileNotFoundError(f"Invalid ZIP file: {self.root}")
        else:
            if not self.root.is_dir():
                raise FileNotFoundError(f"Public folder not found: {self.root}")

    def __del__(self):
        """Close ZIP handle if open."""
        if self.zip_handle:
            try:
                self.zip_handle.close()
            except Exception as e:
                logger.warning(f"Error closing ZIP handle: {e}")

    def list_dir(self, rel_path: str = "") -> List[Dict[str, Any]]:
        """List immediate children of a directory."""
        if self.is_zip:
            return self._list_dir_zip(rel_path)
        else:
            return self._list_dir_folder(rel_path)

    def _list_dir_folder(self, rel_path: str = "") -> List[Dict[str, Any]]:
        target = self.root / rel_path if rel_path else self.root
        if not target.is_dir():
            return []

        results = []
        for entry in sorted(target.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
            if entry.name.startswith("."):
                continue
            rel = str(entry.relative_to(self.root)).replace(os.sep, "/")
            results.append({
                "name": entry.name,
                "rel_path": rel,
                "type": "dir" if entry.is_dir() else "file",
                "size": entry.stat().st_size if entry.is_file() else 0,
                "full_path": entry,
            })
        return results

    def _list_dir_zip(self, rel_path: str = "") -> List[Dict[str, Any]]:
        if not self.zip_handle:
            return []

        # Normalize path separator
        search_prefix = rel_path.replace(os.sep, "/")
        if search_prefix and not search_prefix.endswith("/"):
            search_prefix += "/"
        
        results: Dict[str, Dict[str, Any]] = {}

        for name in self.zip_handle.namelist():
            # Get first component relative to search_prefix
            if search_prefix:
                if not name.startswith(search_prefix):
                    continue
                remainder = name[len(search_prefix):]
                if not remainder:
                    continue
                first_component = remainder.split("/")[0] + "/"
                full_rel = search_prefix.rstrip("/") + "/" + remainder.split("/")[0]
            else:
                # Root level
                first_component = name.split("/")[0] + "/"
                full_rel = first_component.rstrip("/")

            if first_component not in results:
                is_dir = name.endswith("/")
                results[first_component] = {
                    "name": first_component.rstrip("/"),
                    "rel_path": full_rel,
                    "type": "dir" if is_dir else "file",
                    "size": self.zip_handle.getinfo(name).compress_size if not is_dir else 0,
                    "full_path": None,
                }

        return list(results.values())

    def read_text(self, rel_path: str) -> Optional[str]:
        if self.is_zip:
            return self._read_text_zip(rel_path)
        else:
            return self._read_text_folder(rel_path)

    def _read_text_folder(self, rel_path: str) -> Optional[str]:
        fp = self.root / rel_path
        if not fp.is_file():
            return None
        return fp.read_text(encoding="utf-8")

    def _read_text_zip(self, rel_path: str) -> Optional[str]:
        if not self.zip_handle:
            return None
        try:
            return self.zip_handle.read(rel_path).decode("utf-8")
        except KeyError:
            return None

    def read_bytes(self, rel_path: str) -> Optional[bytes]:
        if self.is_zip:
            return self._read_bytes_zip(rel_path)
        else:
            return self._read_bytes_folder(rel_path)

    def _read_bytes_folder(self, rel_path: str) -> Optional[bytes]:
        fp = self.root / rel_path
        if not fp.is_file():
            return None
        return fp.read_bytes()

    def _read_bytes_zip(self, rel_path: str) -> Optional[bytes]:
        if not self.zip_handle:
            return None
        try:
            return self.zip_handle.read(rel_path)
        except KeyError:
            return None

    def list_unit_templates(self) -> list[Union[Path, FakePath]]:
        """Returns list of file paths (works for both ZIP and folder by simulating Path objects)."""
        results = []
        
        for rel in ["simulation/templates/units/", "simulation/templates/"]:
            entries = self.list_dir(rel) if rel.endswith("/") else self.list_dir(rel.rstrip("/"))
            # Collect all XML files under these paths
            for entry in entries:
                if entry["type"] == "dir":
                    sub_entries = self.list_dir(entry["rel_path"])
                    for sub in sub_entries:
                        if sub["type"] == "file" and sub["name"].endswith(".xml"):
                            results.append(FakePath(entry["rel_path"] + sub["name"], sub["name"]))
                elif entry["type"] == "file" and entry["name"].endswith(".xml"):
                    results.append(FakePath(entry["rel_path"], entry["name"]))

        return sorted(set(results), key=lambda p: p.name)

    def list_meshes(self) -> list[Union[Path, FakePath]]:
        """Return all 3D model files."""
        results = []
        self._collect_recursive(self.SUB_ART_MESHES, FileExtensions.MESHES, results)
        return results

    def list_textures(self) -> list[Union[Path, FakePath]]:
        """Return all texture image files."""
        results = []
        self._collect_recursive(self.SUB_ART_TEXTURES, FileExtensions.TEXTURES, results)
        return results

    def list_actors(self) -> list[Union[Path, FakePath]]:
        """Return all actor XML files."""
        results = []
        self._collect_recursive(self.SUB_ART_ACTORS, FileExtensions.XML, results)
        return results

    def _collect_recursive(self, start_path: str, extensions: set, results: List[Union[Path, FakePath]]) -> None:
        """Recursively collect files with given extensions."""
        entries = self.list_dir(start_path)
        for entry in entries:
            if entry["type"] == "dir":
                self._collect_recursive(entry["rel_path"], extensions, results)
            elif entry["type"] == "file":
                ext = "." + entry["name"].rsplit(".", 1)[-1].lower()
                if ext in extensions:
                    results.append(FakePath(entry["rel_path"], entry["name"]))

    def search_files(self, query: str, subdir: str = "") -> list[Union[Path, FakePath]]:
        """Search for files by name."""
        search_root = subdir if subdir else ""
        results = []
        q = query.lower()

        # List everything recursively (may be slow for large archives)
        def collect_all(prefix=""):
            entries = self.list_dir(prefix)
            for entry in entries:
                if q in entry["name"].lower():
                    results.append(FakePath(entry["rel_path"], entry["name"]))
                if entry["type"] == "dir" and results:
                    continue  # Limit depth
                    collect_all(entry["rel_path"])
                elif entry["type"] == "dir":
                    collect_all(entry["rel_path"])

        collect_all(search_root)
        return results[:500]