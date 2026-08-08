"""Mod project management with .adcreator project files."""

import json
import re
import zipfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class ModFile:
    """Represents a file in the mod project."""
    path: str  # Relative path in the mod
    content: str  # File content (text or base64 encoded binary)
    is_binary: bool = False
    created_at: str = ""
    modified_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.modified_at:
            self.modified_at = datetime.now().isoformat()


@dataclass
class ModInfo:
    """Metadata for a mod."""
    name: str = ""
    version: str = "1.0.0"
    label: str = ""
    description: str = ""
    dependencies: List[str] = field(default_factory=lambda: ["0ad=0.28.0"])
    type: str = "content"
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "label": self.label or self.name,
            "description": self.description,
            "dependencies": self.dependencies,
            "type": self.type,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ModInfo':
        return cls(
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            label=data.get("label", ""),
            description=data.get("description", ""),
            dependencies=data.get("dependencies", ["0ad=0.28.0"]),
            type=data.get("type", "content"),
        )


class ModProject:
    """Manages a mod project using .adcreator files."""
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.info: Optional[ModInfo] = None
        self.files: Dict[str, ModFile] = {}  # path -> ModFile
    
    @property
    def is_loaded(self) -> bool:
        """Check if project is loaded."""
        return self.info is not None
    
    @property
    def project_name(self) -> str:
        """Get the project name (without extension)."""
        return self.project_path.stem
    
    def create(self, name: str, label: str, description: str = "", 
               version: str = "1.0.0", dependencies: List[str] = None) -> None:
        """Create a new project."""
        # Validate name
        if not name or not name.strip():
            raise ValueError("Mod name cannot be empty")
        
        if not re.match(r'^[a-zA-Z0-9_\-\s]+$', name):
            raise ValueError("Mod name must contain only alphanumeric characters, hyphens, underscores, and spaces")
        
        # Validate version
        if not re.match(r'^\d+\.\d+\.\d+.*$', version):
            raise ValueError("Version must follow semantic versioning (x.y.z)")
        
        # Check if project file exists
        if self.project_path.exists():
            raise FileExistsError(f"Project file already exists: {self.project_path}")
        
        # Create project info
        self.info = ModInfo(
            name=name.strip(),
            label=label or name,
            description=description,
            version=version,
            dependencies=dependencies or ["0ad=0.28.0"],
        )
        
        # Save project
        self.save()
    
    def load(self) -> None:
        """Load project from .adcreator file."""
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project file not found: {self.project_path}")
        
        with open(self.project_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Load info
        self.info = ModInfo.from_dict(data.get("info", {}))
        
        # Load files
        self.files = {}
        for file_data in data.get("files", []):
            mod_file = ModFile(
                path=file_data["path"],
                content=file_data["content"],
                is_binary=file_data.get("is_binary", False),
                created_at=file_data.get("created_at", ""),
                modified_at=file_data.get("modified_at", "")
            )
            self.files[mod_file.path] = mod_file
    
    def save(self) -> None:
        """Save project to .adcreator file."""
        if not self.info:
            raise ValueError("No project info to save")
        
        data = {
            "version": "1.0",
            "info": self.info.to_dict(),
            "files": [
                {
                    "path": f.path,
                    "content": f.content,
                    "is_binary": f.is_binary,
                    "created_at": f.created_at,
                    "modified_at": f.modified_at
                }
                for f in self.files.values()
            ]
        }
        
        self.project_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.project_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def add_file(self, content: str, rel_path: str, is_binary: bool = False) -> None:
        """Add a file to the project."""
        mod_file = ModFile(
            path=rel_path,
            content=content,
            is_binary=is_binary
        )
        self.files[rel_path] = mod_file
    
    def update_file(self, content: str, rel_path: str, is_binary: bool = False) -> None:
        """Update an existing file in the project."""
        if rel_path in self.files:
            self.files[rel_path].content = content
            self.files[rel_path].is_binary = is_binary
            self.files[rel_path].modified_at = datetime.now().isoformat()
        else:
            self.add_file(content, rel_path, is_binary)
    
    def remove_file(self, rel_path: str) -> None:
        """Remove a file from the project."""
        if rel_path in self.files:
            del self.files[rel_path]
    
    def get_file(self, rel_path: str) -> Optional[ModFile]:
        """Get a file from the project."""
        return self.files.get(rel_path)
    
    def list_files(self, subdir: str = "") -> List[str]:
        """List all file paths in the project, optionally filtered by subdirectory."""
        files = []
        for path in self.files.keys():
            if not subdir or path.startswith(subdir):
                files.append(path)
        return sorted(files)
    
    def build_pyromod(self, output_path: Path) -> Path:
        """Build the mod as a .pyromod file."""
        output_path = Path(output_path)
        if not output_path.suffix:
            output_path = output_path.with_suffix('.pyromod')
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add mod.json
            zf.writestr("mod.json", json.dumps(self.info.to_dict(), indent=2))
            
            # Add all files
            for mod_file in self.files.values():
                if mod_file.is_binary:
                    # Assume content is base64 encoded
                    import base64
                    content = base64.b64decode(mod_file.content)
                else:
                    content = mod_file.content.encode('utf-8')
                
                zf.writestr(mod_file.path, content)
        
        return output_path
