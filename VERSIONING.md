# Versioning Guide

This document explains how to use the versioning system for AdCreator.

## Files

- **VERSION_HISTORY.md** - Contains complete version history with all changes
- **CHANGELOG.md** - Human-readable changelog following Keep a Changelog format
- **version.py** - Python module for programmatic version access
- **update_version.py** - Utility script to update versions

## Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards compatible manner
- **PATCH** version when you make backwards compatible bug fixes

## Using the Update Script

To update the version and add a changelog entry:

```bash
# For bug fixes
python update_version.py patch "Fixed critical bug in recent projects handling"

# For new features
python update_version.py minor "Added unit template preview functionality"

# For breaking changes
python update_version.py major "Changed project file format"
```

This will:
1. Automatically bump the version number
2. Add a new version entry to VERSION_HISTORY.md with date and description
3. Add an entry to the [Unreleased] section in CHANGELOG.md

## Manual Version Updates

If you prefer to update manually:

1. Add a new version entry to VERSION_HISTORY.md with date and changes
2. Add a new section to CHANGELOG.md under [Unreleased]
3. When releasing, move [Unreleased] entries to a new version section with the date

## Programmatic Access

To get the current version in Python code:

```python
from version import get_version, __version__

# Using the function
current_version = get_version()
print(f"Current version: {current_version}")

# Using the constant
print(f"Current version: {__version__}")
```

## Changelog Format

Entries should follow this format:

```markdown
## [Unreleased]

### Added
- New feature description

### Changed
- Modification description

### Fixed
- Bug fix description

### Security
- Security fix description
```

## Release Process

When creating a release:

1. Ensure all changes are documented in [Unreleased]
2. Update the version using the update script or manually
3. Change [Unreleased] to [X.Y.Z] - YYYY-MM-DD
4. Create a new [Unreleased] section at the top
5. Commit the changes
6. Tag the commit with the version number
