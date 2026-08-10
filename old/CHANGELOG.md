# Changelog

All notable changes to AdCreator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Complete GUI redesign with sidebar navigation, modern dark theme, improved layout, enhanced user experience, and professional styling

## [1.1.0] - 2026-08-08

### Added
- Versioning system with VERSION file and CHANGELOG.md
- Python version module (version.py) for programmatic version access
- Bug tracking and documentation system

### Fixed
- **Critical**: Fixed KeyError risk in recent projects handling across 7 locations
  - Changed direct dictionary access `r["path"]` to safe access `r.get("path")`
  - Added validation to skip malformed entries without paths
  - Affected files: settings.py, ui/dialogs.py, ui/tabs.py, gui/app_pyqt6.py, ui/tabs_old.py, gui/tab_recent.py

- **Critical**: Fixed improper resource cleanup with direct `__del__()` calls
  - Replaced direct `__del__()` calls with proper `close()` method calls
  - Added proper error handling for resource cleanup
  - Affected files: gui/app_pyqt6.py, gui/app.py

- **Medium**: Added logging infrastructure to 7 modules
  - Added `import logging` and logger initialization where missing
  - Replaced silent exception handling with proper logging
  - Improved debugging capabilities across the application

- **Medium**: Added base64 decoding error handling
  - Added try-catch for base64 decoding in mod build function
  - Prevents crashes when binary content is invalid
  - Affected file: core/mod.py

- **Medium**: Added path navigation error handling
  - Added proper error handling for path parent navigation
  - Prevents crashes when directory structure is unexpected
  - Affected files: gui/app_pyqt6.py, gui/app_ctk.py

- **Medium**: Added subprocess call validation
  - Added path existence validation before launching 0 A.D. executable
  - Prevents silent failures when executable path is invalid
  - Affected file: ui/main_window.py

### Security
- No security vulnerabilities found during this audit

### Changed
- Improved error handling across 15+ exception handlers
- Enhanced resource management for ZIP file handles
- Better validation of user-provided data and paths

## [1.0.0] - Initial Release

### Added
- Initial release of AdCreator mod maker for 0 A.D.
- Basic mod project management
- Asset browsing and import functionality
- Unit template editor
- Support for multiple GUI frameworks (PyQt6, CustomTkinter)
- Game data auto-detection
- Recent projects tracking
