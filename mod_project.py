"""Mod metadata and project management."""

import json
import logging
import re
import zipfile
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Union

from asset_source import LocalAssetSource

logger = logging.getLogger(__name__)

@dataclass
class ModInfo:
    name: str = ""
    version: str = "1.0.0"
    label: str = ""
    description: str = ""
    dependencies: list = field(default_factory=lambda: ["0ad=0.28.0"])
    type: str = "content"

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "label": self.label or self.name,
            "description": self.description,
            "dependencies": self.dependencies,
            "type": self.type,
        }

class ModProject:
    """Manages a local mod directory with proper 0 A.D. folder structure."""

    ALL_DIRS = [
        "simulation/templates/units",
        "simulation/templates",
        "simulation/data",
        "art/meshes",
        "art/textures",
        "art/actors",
        "gui",
        "audio",
        "maps",
        "globalscripts",
    ]

    def __init__(self, mod_dir: Path):
        self.mod_dir = Path(mod_dir)
        self.info = ModInfo()

    @property
    def name(self) -> str:
        return self.info.name

    @property
    def is_loaded(self) -> bool:
        return (self.mod_dir / "mod.json").exists()

    def create(self, name: str, label: str, description: str = "",
               version: str = "1.0.0", dependencies: list = None):
        # Validate mod name
        if not name or not name.strip():
            raise ValueError("Mod name cannot be empty")
        
        # Check for valid characters (alphanumeric, hyphens, underscores, spaces)
        if not re.match(r'^[a-zA-Z0-9_\-\s]+$', name):
            raise ValueError("Mod name must contain only alphanumeric characters, hyphens, underscores, and spaces")
        
        # Validate version format (basic semantic versioning check)
        if not re.match(r'^\d+\.\d+\.\d+.*$', version):
            logger.warning(f"Version '{version}' does not follow semantic versioning (x.y.z)")
        
        if self.mod_dir.exists():
            raise FileExistsError(f"Directory already exists: {self.mod_dir}")
        
        self.mod_dir.mkdir(parents=True)
        for sub in self.ALL_DIRS:
            (self.mod_dir / sub).mkdir(parents=True, exist_ok=True)
        
        self.info = ModInfo(
            name=name.strip(), label=label or name, description=description,
            version=version, dependencies=dependencies or ["0ad=0.28.0"],
        )
        self.save_info()

    @classmethod
    def load(cls, mod_dir: Path) -> "ModProject":
        mod_dir = Path(mod_dir)
        proj = cls(mod_dir)
        mod_json = mod_dir / "mod.json"
        if not mod_json.exists():
            raise FileNotFoundError(f"No mod.json in {mod_dir}")
        with open(mod_json) as f:
            data = json.load(f)
        proj.info = ModInfo(
            name=data.get("name", mod_dir.name),
            version=data.get("version", "1.0.0"),
            label=data.get("label", mod_dir.name),
            description=data.get("description", ""),
            dependencies=data.get("dependencies", ["0ad=0.28.0"]),
            type=data.get("type", "content"),
        )
        return proj

    def save_info(self):
        with open(self.mod_dir / "mod.json", "w") as f:
            json.dump(self.info.to_json(), f, indent=4)

    def add_file(self, rel_path: str, content: str | bytes):
        """Add a file to the mod project with the given relative path and content."""
        full = self.mod_dir / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            full.write_bytes(content)
        else:
            full.write_text(content, encoding="utf-8")

    def import_from_local(self, src_path: Path, source: LocalAssetSource) -> str:
        """Import a file from a local asset source into the mod project."""
        rel = str(src_path.relative_to(source.root)).replace(os.sep, "/")
        data = src_path.read_bytes()
        self.add_file(rel, data)
        return rel

    def list_files(self, subdir: str = "") -> list[Path]:
        """List all files in the mod project, excluding mod.json."""
        target = self.mod_dir / subdir if subdir else self.mod_dir
        if not target.is_dir():
            return []
        return sorted(
            p for p in target.rglob("*")
            if p.is_file() and p.name != "mod.json"
        )

    def delete_file(self, rel_path: str):
        fp = self.mod_dir / rel_path
        if fp.is_file():
            fp.unlink()
            parent = fp.parent
            while parent != self.mod_dir and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent

    def build_pyromod(self, output_path: Path) -> Path:
        if not (self.mod_dir / "mod.json").exists():
            raise FileNotFoundError("mod.json not found")
        output_path = Path(output_path)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(self.mod_dir / "mod.json", "mod.json")
            for filepath in self.list_files():
                arcname = str(filepath.relative_to(self.mod_dir)).replace(os.sep, "/")
                zf.write(filepath, arcname)
        return output_path