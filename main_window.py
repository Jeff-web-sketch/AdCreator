"""Main application window."""

import sys
import tempfile
import subprocess
import platform
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QMessageBox, QFileDialog,
    QTreeWidget, QTreeWidgetItem, QStatusBar, QScrollArea, QMenu
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QPalette

from assets import AssetSource, FolderAssetSource, ZipAssetSource
from mod import ModProject
from settings import AppSettings
from styles import get_dark_theme_palette, get_button_style
from version import __version__
from tabs import (
    AssetsTab, UnitsTab, NewUnitTab, SettingsTab,
    OverviewTab, RecentTab, StructuresTab, TechsTab, AurasTab
)

# Simple game data locator
class GameDataLocator:
    @staticmethod
    def find_public_folder():
        import platform
        from pathlib import Path
        
        system = platform.system()
        candidates = []
        
        if system == "Darwin":
            candidates.extend([
                Path("/Applications/0 A.D..app/Contents/Resources/data/mods/public.zip"),
                Path("/Applications/0ad.app/Contents/Resources/data/mods/public.zip"),
                Path.home() / "Library" / "Application Support" / "0ad" / "data" / "mods" / "public.zip",
            ])
        elif system == "Windows":
            program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
            candidates.append(Path(program_files) / "0 A.D." / "binaries" / "data" / "mods" / "public.zip")
        else:
            candidates.extend([
                Path("/usr/share/0ad/data/mods/public.zip"),
                Path.home() / ".local" / "share" / "0ad" / "data" / "mods" / "public.zip",
            ])
        
        for path in candidates:
            if path.exists():
                return path, True
        
        return None


class MainWindow(QMainWindow):
    """Main application window."""
    
    MIN_WIDTH = 900
    MIN_HEIGHT = 600
    DEFAULT_WIDTH = 1100
    DEFAULT_HEIGHT = 720
    
    def __init__(self):
        super().__init__()
        
        self.settings = AppSettings()
        self.asset_source: Optional[AssetSource] = None
        self.project: Optional[ModProject] = None
        
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_window(self):
        """Configure the main window."""
        self.setWindowTitle(f"0 A.D. Mod Maker v{__version__}")
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        
        # Apply dark theme
        self.setPalette(get_dark_theme_palette())
        self.setStyleSheet("background-color: #1a1a2a;")
    
    def _setup_ui(self):
        """Build the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #1a1a2a;")
        main_layout.addWidget(self.content_stack, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #2d2d3d; color: #c0c0d0;")
        self.setStatusBar(self.status_bar)
        
        # Create tabs
        self._create_tabs()
    
    def _create_sidebar(self) -> QFrame:
        """Create the navigation sidebar."""
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-right: 2px solid #4a4a6a;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)
        
        # App title
        title = QLabel("🎮 0 A.D. Mod Maker")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("overview", "📊 Overview"),
            ("assets", "📁 Assets"),
            ("units", "⚔️ Units"),
            ("new_unit", "➕ New Unit"),
            ("structures", "🏗️ Structures"),
            ("techs", "🔬 Technologies"),
            ("auras", "✨ Auras"),
            ("settings", "⚙️ Settings"),
        ]
        
        for key, label in nav_items:
            btn = QPushButton(label)
            btn.setStyleSheet(get_button_style())
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, k=key: self._navigate_to(k))
            layout.addWidget(btn)
            self.nav_buttons[key] = btn
        
        layout.addStretch()
        
        # Project info
        self.project_label = QLabel("No project loaded")
        self.project_label.setStyleSheet("color: #9090a0; font-size: 12px;")
        self.project_label.setWordWrap(True)
        layout.addWidget(self.project_label)
        
        return sidebar
    
    def _create_tabs(self):
        """Create all tab pages."""
        # Overview tab
        self.overview_tab = OverviewTab(self)
        self.content_stack.addWidget(self.overview_tab)
        
        # Assets tab
        self.assets_tab = AssetsTab(self)
        self.content_stack.addWidget(self.assets_tab)
        
        # Units tab
        self.units_tab = UnitsTab(self)
        self.content_stack.addWidget(self.units_tab)
        
        # New Unit tab
        self.new_unit_tab = NewUnitTab(self)
        self.content_stack.addWidget(self.new_unit_tab)
        
        # Structures tab
        self.structures_tab = StructuresTab(self)
        self.content_stack.addWidget(self.structures_tab)
        
        # Techs tab
        self.techs_tab = TechsTab(self)
        self.content_stack.addWidget(self.techs_tab)
        
        # Auras tab
        self.auras_tab = AurasTab(self)
        self.content_stack.addWidget(self.auras_tab)
        
        # Settings tab
        self.settings_tab = SettingsTab(self)
        self.content_stack.addWidget(self.settings_tab)
        
        # Default to overview
        self._navigate_to("overview")
    
    def _connect_signals(self):
        """Connect signals and slots."""
        pass
    
    def _navigate_to(self, tab_key: str):
        """Navigate to a specific tab."""
        # Update button states
        for key, btn in self.nav_buttons.items():
            btn.setChecked(key == tab_key)
        
        # Show appropriate tab
        if tab_key == "overview":
            self.content_stack.setCurrentWidget(self.overview_tab)
        elif tab_key == "assets":
            self.content_stack.setCurrentWidget(self.assets_tab)
        elif tab_key == "units":
            self.content_stack.setCurrentWidget(self.units_tab)
        elif tab_key == "new_unit":
            self.content_stack.setCurrentWidget(self.new_unit_tab)
        elif tab_key == "structures":
            self.content_stack.setCurrentWidget(self.structures_tab)
        elif tab_key == "techs":
            self.content_stack.setCurrentWidget(self.techs_tab)
        elif tab_key == "auras":
            self.content_stack.setCurrentWidget(self.auras_tab)
        elif tab_key == "settings":
            self.content_stack.setCurrentWidget(self.settings_tab)
    
    def action_new_mod(self):
        """Create a new mod project."""
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setNameFilter("AD Creator Projects (*.adcreator)")
        dialog.setDefaultSuffix("adcreator")
        
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            file_path = dialog.selectedFiles()[0]
            if file_path:
                try:
                    project = ModProject(Path(file_path))
                    project.create(
                        name="New Mod",
                        label="New Mod",
                        description="A new 0 A.D. mod"
                    )
                    self.project = project
                    self.project_label.setText(f"📁 {project.project_name}")
                    self._update_status_bar(f"Created new project: {project.project_name}")
                    self._refresh_all_tabs()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
    
    def action_open_mod(self):
        """Open an existing mod project."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project",
            str(Path.home()),
            "AD Creator Projects (*.adcreator);;All Files (*)"
        )
        
        if file_path:
            try:
                project = ModProject(Path(file_path))
                project.load()
                self.project = project
                self.project_label.setText(f"📁 {project.project_name}")
                self.settings.add_recent(str(project.project_path), project.info.label)
                self.settings.save()
                self._update_status_bar(f"Loaded project: {project.project_name}")
                self._refresh_all_tabs()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {e}")
    
    def action_save_mod(self):
        """Save the current mod project."""
        if self.project:
            try:
                self.project.save()
                self._update_status_bar(f"Saved project: {self.project.project_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project: {e}")
    
    def action_build_mod(self):
        """Build the mod as a .pyromod file."""
        if not self.project:
            QMessageBox.warning(self, "No Project", "No project loaded to build.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Build Mod",
            str(Path.home()),
            "Pyromod Files (*.pyromod);;All Files (*)"
        )
        
        if file_path:
            try:
                output_path = self.project.build_pyromod(Path(file_path))
                QMessageBox.information(self, "Success", f"Mod built successfully:\n{output_path}")
                self._update_status_bar(f"Built mod: {output_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to build mod: {e}")
    
    def _update_status_bar(self, message: str):
        """Update the status bar with a message."""
        self.status_bar.showMessage(message, 5000)
    
    def _refresh_all_tabs(self):
        """Refresh all tabs to reflect current project state."""
        if self.project:
            self.overview_tab.refresh()
            self.assets_tab.refresh()
            self.units_tab.refresh()
            self.new_unit_tab.refresh()
            self.structures_tab.refresh()
            self.techs_tab.refresh()
            self.auras_tab.refresh()
            self.settings_tab.refresh()
