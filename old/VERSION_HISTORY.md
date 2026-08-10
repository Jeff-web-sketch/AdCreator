# Version History

## Version 2.0.0 - 2026-08-08

### Major Changes
- **Complete GUI Redesign**: Sidebar navigation with modern dark theme
- **Enhanced User Experience**: Professional styling, better layout, improved navigation
- **Asset Browser Improvements**: Parent folder navigation, path display, better file listing
- **Settings Page Enhancement**: Clear field descriptions, better organization, helpful tooltips
- **Functional Buttons**: All buttons now work with proper feedback and actions

### New Features
- Sidebar navigation with 10 main sections
- Context-sensitive help system
- Refresh functionality for all views
- Parent folder navigation in asset browser
- Current path display in asset browser
- Detailed settings explanations
- Enhanced overview page with statistics

### Bug Fixes
- Fixed ZIP file directory listing to show all files correctly
- Fixed folder directory listing sorting
- Improved error handling throughout the application
- Fixed non-functional buttons (Refresh, Help, navigation)
- Better null/undefined reference handling

### UI/UX Improvements
- Modern dark theme with consistent styling
- Rounded corners and professional appearance
- Better spacing and padding throughout
- Tooltips on all interactive elements
- Improved button states and feedback
- Enhanced empty state messages
- Better visual hierarchy

## Version 1.2.0 - 2026-08-08

### UI/UX Enhancements
- Enhanced startup dialog with better layout and tips
- Added tooltips to all menu items and buttons
- Added keyboard shortcuts dialog
- Modern styling with rounded corners and better spacing
- Improved tab widget styling
- Enhanced button states and hover effects

### New Features
- Keyboard shortcuts dialog showing all available shortcuts
- Enhanced About dialog with feature list
- Context menus in recent projects list
- Better empty state messages
- Movable tabs for personalized workflow

### Bug Fixes
- Fixed KeyError risk in recent projects handling (7 locations)
- Fixed improper resource cleanup with direct __del__ calls
- Added proper logging infrastructure
- Improved error handling with logging instead of silent exceptions

## Version 1.1.0 - 2026-08-08

### Added
- Versioning system with VERSION file and CHANGELOG.md
- Python version module (version.py) for programmatic version access
- Bug tracking and documentation system
- Update script for version management

### Bug Fixes
- Fixed KeyError risk in recent projects handling across multiple files
- Fixed improper resource cleanup with direct __del__ calls
- Added base64 decoding error handling
- Added path navigation error handling
- Added subprocess call validation
- Enhanced exception handling with proper logging

### Security
- No security vulnerabilities found during audit

## Version 1.0.0 - Initial Release

### Features
- Initial release of AdCreator mod maker for 0 A.D.
- Basic mod project management
- Asset browsing and import functionality
- Unit template editor
- Support for multiple GUI frameworks (PyQt6, CustomTkinter)
- Game data auto-detection
- Recent projects tracking
