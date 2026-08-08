"""Asset source management for reading game files."""

import zipfile
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AssetEntry:
    """Represents a file or directory in the asset source."""
    name: str
    type: str  # 'file' or 'dir'
    size: int = 0
    rel_path: str = ""


class AssetSource:
    """Base class for asset sources."""
    
    def read_text(self, path: str) -> Optional[str]:
        """Read text content from a file."""
        raise NotImplementedError
    
    def read_binary(self, path: str) -> Optional[bytes]:
        """Read binary content from a file."""
        raise NotImplementedError
    
    def list_dir(self, path: str) -> List[AssetEntry]:
        """List contents of a directory."""
        raise NotImplementedError
    
    def list_unit_templates(self) -> List[AssetEntry]:
        """List all unit templates."""
        raise NotImplementedError


class FolderAssetSource(AssetSource):
    """Asset source that reads from a local folder."""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
    
    def read_text(self, path: str) -> Optional[str]:
        try:
            full_path = self.base_path / path
            if full_path.exists() and full_path.is_file():
                return full_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Error reading text from {path}: {e}")
        return None
    
    def read_binary(self, path: str) -> Optional[bytes]:
        try:
            full_path = self.base_path / path
            if full_path.exists() and full_path.is_file():
                return full_path.read_bytes()
        except Exception as e:
            logger.warning(f"Error reading binary from {path}: {e}")
        return None
    
    def list_dir(self, path: str) -> List[AssetEntry]:
        entries = []
        try:
            full_path = self.base_path / path
            if full_path.exists() and full_path.is_dir():
                for item in full_path.iterdir():
                    rel_path = str(item.relative_to(self.base_path))
                    if item.is_dir():
                        entries.append(AssetEntry(
                            name=item.name,
                            type="dir",
                            rel_path=rel_path
                        ))
                    else:
                        entries.append(AssetEntry(
                            name=item.name,
                            type="file",
                            size=item.stat().st_size,
                            rel_path=rel_path
                        ))
        except Exception as e:
            logger.warning(f"Error listing directory {path}: {e}")
        return entries
    
    def list_unit_templates(self) -> List[AssetEntry]:
        entries = []
        try:
            units_path = self.base_path / "simulation" / "templates" / "units"
            if units_path.exists():
                for xml_file in units_path.rglob("*.xml"):
                    rel_path = str(xml_file.relative_to(self.base_path))
                    entries.append(AssetEntry(
                        name=xml_file.stem,
                        type="file",
                        size=xml_file.stat().st_size,
                        rel_path=rel_path
                    ))
        except Exception as e:
            logger.warning(f"Error listing unit templates: {e}")
        return entries


class ZipAssetSource(AssetSource):
    """Asset source that reads from a ZIP file."""
    
    def __init__(self, zip_path: Path):
        self.zip_path = Path(zip_path)
        self._zip = None
    
    def _ensure_open(self):
        if self._zip is None:
            self._zip = zipfile.ZipFile(self.zip_path, 'r')
    
    def read_text(self, path: str) -> Optional[str]:
        try:
            self._ensure_open()
            if path in self._zip.namelist():
                return self._zip.read(path).decode('utf-8')
        except Exception as e:
            logger.warning(f"Error reading text from ZIP {path}: {e}")
        return None
    
    def read_binary(self, path: str) -> Optional[bytes]:
        try:
            self._ensure_open()
            if path in self._zip.namelist():
                return self._zip.read(path)
        except Exception as e:
            logger.warning(f"Error reading binary from ZIP {path}: {e}")
        return None
    
    def list_dir(self, path: str) -> List[AssetEntry]:
        entries = []
        try:
            self._ensure_open()
            path_prefix = path.rstrip('/') + '/' if path else ''
            
            for name in self._zip.namelist():
                if name.startswith(path_prefix):
                    rel_name = name[len(path_prefix):]
                    if '/' not in rel_name or rel_name.endswith('/'):
                        # Direct item in this directory
                        if rel_name.endswith('/'):
                            dir_name = rel_name.rstrip('/')
                            entries.append(AssetEntry(
                                name=dir_name,
                                type="dir",
                                rel_path=name.rstrip('/')
                            ))
                        else:
                            info = self._zip.getinfo(name)
                            entries.append(AssetEntry(
                                name=rel_name,
                                type="file",
                                size=info.file_size,
                                rel_path=name
                            ))
        except Exception as e:
            logger.warning(f"Error listing ZIP directory {path}: {e}")
        return entries
    
    def list_unit_templates(self) -> List[AssetEntry]:
        entries = []
        try:
            self._ensure_open()
            for name in self._zip.namelist():
                if name.startswith('simulation/templates/units/') and name.endswith('.xml'):
                    entries.append(AssetEntry(
                        name=Path(name).stem,
                        type="file",
                        size=self._zip.getinfo(name).file_size,
                        rel_path=name
                    ))
        except Exception as e:
            logger.warning(f"Error listing ZIP unit templates: {e}")
        return entries
    
    def close(self):
        if self._zip:
            self._zip.close()
            self._zip = None
    
    def __del__(self):
        self.close()
