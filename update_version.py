#!/usr/bin/env python3
"""
Utility script to update the version and add changelog entries.

Usage:
    python update_version.py patch "Fixed critical bug in recent projects"
    python update_version.py minor "Added new feature"
    python update_version.py major "Breaking changes"
"""

import sys
from pathlib import Path
from datetime import datetime
from version import get_version, set_version

def bump_version(current: str, bump_type: str) -> str:
    """Bump version according to semantic versioning."""
    major, minor, patch = map(int, current.split('.'))
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return f"{major}.{minor}.{patch}"

def add_changelog_entry(version: str, description: str):
    """Add a new entry to the changelog."""
    changelog = Path(__file__).parent / "CHANGELOG.md"
    
    if not changelog.exists():
        return
    
    content = changelog.read_text()
    
    # Find the version header
    version_header = f"## [Unreleased]"
    
    if version_header in content:
        # Add to existing unreleased section
        lines = content.split('\n')
        unreleased_idx = lines.index(version_header)
        # Insert after the header and before the first sub-header
        insert_idx = unreleased_idx + 2
        lines.insert(insert_idx, f"- {description}")
        content = '\n'.join(lines)
    else:
        # Create new unreleased section at the top
        unreleased_section = f"""## [Unreleased]

### Changed
- {description}

"""
        content = unreleased_section + content
    
    changelog.write_text(content)

def main():
    if len(sys.argv) < 3:
        print("Usage: python update_version.py <patch|minor|major> <description>")
        sys.exit(1)
    
    bump_type = sys.argv[1]
    description = ' '.join(sys.argv[2:])
    
    if bump_type not in ['patch', 'minor', 'major']:
        print("Error: bump_type must be 'patch', 'minor', or 'major'")
        sys.exit(1)
    
    current_version = get_version()
    new_version = bump_version(current_version, bump_type)
    
    print(f"Bumping version: {current_version} -> {new_version}")
    print(f"Description: {description}")
    
    # Update VERSION file
    set_version(new_version)
    
    # Add to changelog
    add_changelog_entry(new_version, description)
    
    print(f"✓ Version updated to {new_version}")
    print(f"✓ Changelog updated")

if __name__ == "__main__":
    main()
