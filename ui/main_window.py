"""Main application window."""

import sys
import tempfile
import subprocess
import platform
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QStatusBar, QMenuBar, QMenu, QMessageBox, QFileDialog,
    QLineEdit, QTextEdit, QDialog, QFormLayout, QDialogButtonBox,
    QFrame, QSplitter, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QPalette

from core.assets import AssetSource, FolderAssetSource, ZipAssetSource
from core.mod import ModProject
from core.settings import AppSettings
from core.game import GameDataLocator
from ui.styles import get_dark_theme_palette, get_button_style
from version import __version__
from ui.tabs import (
    AssetsTab, UnitsTab, NewUnitTab, SettingsTab,
    OverviewTab, RecentTab, StructureTab, TechsTab, AurasTab, StructuresTab
)


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
        self._setup_theme()
        self._setup_menubar()
        self._setup_ui()
        self._auto_load_game_data()
    
    def _setup_window(self):
        self.setWindowTitle(f"0 A.D. Mod Maker v{__version__}")
        w = self.settings.get("window_width", self.DEFAULT_WIDTH)
        h = self.settings.get("window_height", self.DEFAULT_HEIGHT)
        self.resize(w, h)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
    
    def _setup_theme(self):
        app = self.style().metaObject().className()
        palette = get_dark_theme_palette()
        self.setPalette(palette)
    
    def _setup_menubar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Mod...", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Create a new mod project")
        new_action.setToolTip("Create a brand new mod project from scratch")
        new_action.triggered.connect(self.action_new_mod)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Mod...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open an existing mod project")
        open_action.setToolTip("Open an existing .adcreator project file")
        open_action.triggered.connect(self.action_open_mod)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        set_folder_action = QAction("Set Game Data Folder...", self)
        set_folder_action.setStatusTip("Set the 0 A.D. game data location")
        set_folder_action.setToolTip("Select the folder or ZIP file containing 0 A.D. game data")
        set_folder_action.triggered.connect(self.action_set_game_folder)
        file_menu.addAction(set_folder_action)
        
        file_menu.addSeparator()
        
        build_action = QAction("Build .pyromod", self)
        build_action.setShortcut("Ctrl+B")
        build_action.setStatusTip("Build the mod as a .pyromod file")
        build_action.setToolTip("Export your mod as a .pyromod file for distribution")
        build_action.triggered.connect(self.action_build)
        file_menu.addAction(build_action)
        
        run_action = QAction("Run Mod in 0AD", self)
        run_action.setShortcut("Ctrl+R")
        run_action.setStatusTip("Test your mod in 0 A.D.")
        run_action.setToolTip("Launch 0 A.D. with your mod loaded for testing")
        run_action.triggered.connect(self.action_run_in_0ad)
        file_menu.addAction(run_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.setToolTip("Close the application and save settings")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.setStatusTip("View keyboard shortcuts")
        shortcuts_action.setToolTip("View all available keyboard shortcuts")
        shortcuts_action.triggered.connect(self.action_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("About", self)
        about_action.setStatusTip("About this application")
        about_action.setToolTip("View version and credits information")
        about_action.triggered.connect(self.action_about)
        help_menu.addAction(about_action)
    
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a modern sidebar
        self._create_sidebar(main_layout)
        
        # Create main content area
        self._create_content_area(main_layout)
        
        # Status bar
        self._setup_status_bar()
        
        # Create tabs
        self._create_tabs()
    
    def _create_sidebar(self, parent_layout):
        """Create a modern sidebar with navigation."""
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #1a1a2a;
                border-right: 2px solid #2d2d3d;
            }
        """)
        sidebar.setFixedWidth(200)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)
        
        # App logo/title
        logo_label = QLabel("🎮")
        logo_label.setStyleSheet("font-size: 48px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)
        
        app_name = QLabel("Mod Maker")
        app_name.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_name)
        
        version_label = QLabel(f"v{__version__}")
        version_label.setStyleSheet("font-size: 12px; color: #9090a0;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_label)
        
        sidebar_layout.addSpacing(20)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("📁 Assets", "assets"),
            ("⚔️ Units", "units"),
            ("✨ New Unit", "new_unit"),
            ("🔬 Techs", "techs"),
            ("🏛️ Structures", "structures"),
            ("✨ Auras", "auras"),
            ("🔧 Settings", "settings"),
            ("📊 Overview", "overview"),
            ("🕒 Recent", "recent"),
            ("🏗️ Structure", "structure"),
        ]
        
        for icon_text, tab_id in nav_items:
            btn = QPushButton(icon_text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #c0c0d0;
                    border: none;
                    padding: 12px 15px;
                    text-align: left;
                    font-size: 14px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #2d2d3d;
                    color: #ffffff;
                }
                QPushButton:checked {
                    background-color: #7b5eff;
                    color: #ffffff;
                    font-weight: bold;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, tid=tab_id: self._navigate_to_tab(tid))
            
            # Add tooltips
            tooltips = {
                "assets": "Browse and import game assets from 0 A.D.",
                "units": "Edit and manage unit templates",
                "new_unit": "Create new custom units",
                "techs": "Manage technologies and research",
                "structures": "Edit building and structure templates",
                "auras": "Configure unit auras and effects",
                "settings": "Configure mod settings and metadata",
                "overview": "View mod overview and statistics",
                "recent": "Access recent projects",
                "structure": "View mod file structure",
            }
            btn.setToolTip(tooltips.get(tab_id, ""))
            
            self.nav_buttons[tab_id] = btn
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # Bottom section
        footer_label = QLabel("Made with ❤️")
        footer_label.setStyleSheet("font-size: 11px; color: #707080;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(footer_label)
        
        parent_layout.addWidget(sidebar)
    
    def _create_content_area(self, parent_layout):
        """Create the main content area."""
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
            }
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Header bar
        self.header_bar = QFrame()
        self.header_bar.setStyleSheet("""
            QFrame {
                background-color: #383848;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        header_layout = QHBoxLayout(self.header_bar)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        self.page_title = QLabel("📁 Assets")
        self.page_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #7b5eff;")
        header_layout.addWidget(self.page_title)
        
        header_layout.addStretch()
        
        # Quick actions in header
        quick_actions = QHBoxLayout()
        quick_actions.setSpacing(10)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet(get_button_style())
        self.refresh_btn.setToolTip("Refresh current view")
        self.refresh_btn.clicked.connect(self._refresh_current_view)
        quick_actions.addWidget(self.refresh_btn)
        
        self.help_btn = QPushButton("❓ Help")
        self.help_btn.setStyleSheet(get_button_style())
        self.help_btn.setToolTip("Get help with current section")
        self.help_btn.clicked.connect(self._show_help)
        quick_actions.addWidget(self.help_btn)
        
        header_layout.addLayout(quick_actions)
        content_layout.addWidget(self.header_bar)
        
        # Main content area using stacked widget
        from PyQt6.QtWidgets import QStackedWidget
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #2d2d3d;
                border-radius: 10px;
            }
        """)
        content_layout.addWidget(self.content_stack)
        
        parent_layout.addWidget(content_frame, stretch=1)
    
    def _setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #1a1a2a;
                color: #ffffff;
                border-top: 2px solid #2d2d3d;
                padding: 5px;
            }
        """)
        self.setStatusBar(self.status_bar)
        
        self.lbl_game_status = QLabel("🔍 Detecting 0 A.D.…")
        self.lbl_game_status.setStyleSheet("color: #c0c0d0; font-size: 12px;")
        self.lbl_game_status.setToolTip("Shows the status of 0 A.D. game data")
        self.status_bar.addWidget(self.lbl_game_status)
        
        self.status_bar.addPermanentWidget(QLabel(" | "))
        
        self.lbl_mod_status = QLabel("No mod loaded")
        self.lbl_mod_status.setStyleSheet("color: #c0c0d0; font-size: 12px;")
        self.lbl_mod_status.setToolTip("Shows the currently loaded mod project")
        self.status_bar.addPermanentWidget(self.lbl_mod_status)
    
    def _create_tabs(self):
        # Clear existing content
        while self.content_stack.count() > 0:
            widget = self.content_stack.widget(0)
            self.content_stack.removeWidget(widget)
            widget.deleteLater()
        
        # Create tab instances
        self.assets_tab = AssetsTab(self.asset_source, self.project)
        self.units_tab = UnitsTab(self.project, self.asset_source)
        self.new_unit_tab = NewUnitTab(self.asset_source)
        self.techs_tab = TechsTab(self.project, self.asset_source)
        self.structures_tab = StructuresTab(self.project, self.asset_source)
        self.auras_tab = AurasTab(self.project, self.asset_source)
        self.settings_tab = SettingsTab(self.project)
        self.overview_tab = OverviewTab(self.project)
        self.recent_tab = RecentTab()
        self.structure_tab = StructureTab(self.project)
        
        # Add to stacked widget
        self.content_stack.addWidget(self.assets_tab)
        self.content_stack.addWidget(self.units_tab)
        self.content_stack.addWidget(self.new_unit_tab)
        self.content_stack.addWidget(self.techs_tab)
        self.content_stack.addWidget(self.structures_tab)
        self.content_stack.addWidget(self.auras_tab)
        self.content_stack.addWidget(self.settings_tab)
        self.content_stack.addWidget(self.overview_tab)
        self.content_stack.addWidget(self.recent_tab)
        self.content_stack.addWidget(self.structure_tab)
        
        # Map tab IDs to indices
        self.tab_map = {
            "assets": 0,
            "units": 1,
            "new_unit": 2,
            "techs": 3,
            "structures": 4,
            "auras": 5,
            "settings": 6,
            "overview": 7,
            "recent": 8,
            "structure": 9,
        }
        
        # Set default tab
        self._navigate_to_tab("assets")
    
    def _navigate_to_tab(self, tab_id: str):
        """Navigate to a specific tab using sidebar."""
        if tab_id in self.tab_map:
            # Update button states
            for btn_id, btn in self.nav_buttons.items():
                btn.setChecked(btn_id == tab_id)
            
            # Switch content
            index = self.tab_map[tab_id]
            self.content_stack.setCurrentIndex(index)
            
            # Update header title
            titles = {
                "assets": "📁 Assets",
                "units": "⚔️ Units",
                "new_unit": "✨ New Unit",
                "techs": "🔬 Technologies",
                "structures": "🏛️ Structures",
                "auras": "✨ Auras",
                "settings": "🔧 Settings",
                "overview": "📊 Overview",
                "recent": "🕒 Recent Projects",
                "structure": "🏗️ Mod Structure",
            }
            self.page_title.setText(titles.get(tab_id, "Unknown"))
    
    def _auto_load_game_data(self):
        # Try to load from settings
        saved_path = self.settings.game_data_path
        saved_is_zip = self.settings.game_data_is_zip
        
        if saved_path:
            try:
                path = Path(saved_path)
                if path.exists():
                    if saved_is_zip or path.suffix == '.zip':
                        self._set_asset_source(path, is_zip=True)
                    else:
                        self._set_asset_source(path, is_zip=False)
                    return
            except Exception:
                pass
        
        # Try auto-detection
        result = GameDataLocator.find_public_folder()
        if result:
            path, is_zip = result
            self._set_asset_source(path, is_zip=is_zip)
            self.settings.game_data_path = str(path)
            self.settings.game_data_is_zip = is_zip
            self.settings.save()
        else:
            self.lbl_game_status.setText("⚠️ 0 A.D. not found — Set game data folder")
            self.lbl_game_status.setStyleSheet("color: #fbbf24; font-size: 12px;")
    
    def _set_asset_source(self, path: Path, is_zip: bool):
        try:
            if is_zip:
                self.asset_source = ZipAssetSource(path)
                self.lbl_game_status.setText(f"🎮 0 A.D. loaded: {path.name} (ZIP)")
            else:
                self.asset_source = FolderAssetSource(path)
                self.lbl_game_status.setText(f"🎮 0 A.D. loaded: {path.name}")
            
            self.lbl_game_status.setStyleSheet("color: #4ade80; font-size: 12px;")
            
            self.settings.game_data_path = str(path)
            self.settings.game_data_is_zip = is_zip
            self.settings.save()
            
            # Refresh assets tab
            self._create_tabs()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load game data: {e}")
    
    def _update_status_bar(self):
        if self.project and self.project.is_loaded:
            status_text = f"✅ {self.project.info.label} v{self.project.info.version}"
            self.lbl_mod_status.setText(status_text)
            self.lbl_mod_status.setStyleSheet("color: #4ade80; font-size: 12px; font-weight: bold;")
        else:
            self.lbl_mod_status.setText("⚪ No mod loaded")
            self.lbl_mod_status.setStyleSheet("color: #c0c0d0; font-size: 12px;")
    
    def closeEvent(self, event):
        width = self.width()
        height = self.height()
        
        if width >= self.MIN_WIDTH and height >= self.MIN_HEIGHT:
            self.settings.set("window_width", width)
            self.settings.set("window_height", height)
        
        self.settings.save()
        
        if self.asset_source:
            try:
                self.asset_source.close()
            except Exception as e:
                logger.warning(f"Error closing asset source: {e}")
        
        event.accept()
    
    # Actions
    def action_new_mod(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create New Mod")
        dialog.setMinimumSize(450, 300)
        
        layout = QFormLayout(dialog)
        
        label_input = QLineEdit()
        name_input = QLineEdit()
        version_input = QLineEdit("1.0.0")
        desc_input = QTextEdit()
        desc_input.setMaximumHeight(80)
        
        layout.addRow("Display Name:", label_input)
        layout.addRow("Internal Name:", name_input)
        layout.addRow("Version:", version_input)
        layout.addRow("Description:", desc_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            label = label_input.text().strip()
            name = name_input.text().strip()
            version = version_input.text().strip()
            desc = desc_input.toPlainText().strip()
            
            if not label or not name:
                QMessageBox.warning(self, "Missing Fields", "Display Name and Internal Name are required.")
                return
            
            try:
                projects_dir = self.settings.projects_dir
                project_path = projects_dir / f"{name}.adcreator"
                
                if project_path.exists():
                    reply = QMessageBox.question(
                        self, "Project Exists",
                        f"A project with the name '{name}' already exists. Overwrite?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.No:
                        return
                
                self.project = ModProject(project_path)
                self.project.create(
                    name=name, label=label, description=desc, version=version,
                    dependencies=["0ad=0.28.0"]
                )
                self.settings.last_mod_dir = str(self.project.project_path)
                self.settings.add_recent(str(self.project.project_path), label)
                self.settings.save()
                self._update_status_bar()
                self._create_tabs()
                QMessageBox.information(self, "Success", f"Project '{label}' created successfully!")
                self._navigate_to_tab("overview")  # Navigate to overview tab
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
    
    def action_open_mod(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Project File",
            str(self.settings.projects_dir),
            "AD Creator Projects (*.adcreator);;All Files (*)"
        )
        
        if file_path:
            try:
                self.project = ModProject(Path(file_path))
                self.project.load()
                self.settings.last_mod_dir = str(self.project.project_path)
                self.settings.add_recent(str(self.project.project_path), self.project.info.label)
                self.settings.save()
                self._update_status_bar()
                self._create_tabs()
                QMessageBox.information(self, "Success", f"Project '{self.project.info.label}' loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {e}")
    
    def action_set_game_folder(self):
        """Open a dialog to select the 0 A.D. game data folder or ZIP file."""
        # Start with a more user-friendly approach - show folder selection first
        folder = QFileDialog.getExistingDirectory(
            self, "Select 0 A.D. Installation Folder",
            self.settings.game_data_path or str(Path.home())
        )
        
        if folder:
            path_obj = Path(folder)
            
            # Check if this is the 0 A.D. installation folder
            public_zip = path_obj / "public.zip"
            public_folder = path_obj / "binaries" / "data" / "mods" / "public"
            
            if public_zip.exists():
                self._set_asset_source(public_zip, is_zip=True)
                QMessageBox.information(self, "Success", f"Found 0 A.D. data: {public_zip.name}")
            elif public_folder.exists():
                self._set_asset_source(public_folder, is_zip=False)
                QMessageBox.information(self, "Success", f"Found 0 A.D. data: public folder")
            else:
                # If standard locations not found, ask if they want to select a specific file
                reply = QMessageBox.question(
                    self, "Data Not Found",
                    f"Could not find standard 0 A.D. data in this folder.\n\n"
                    f"Do you want to select a specific public.zip file instead?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self._select_specific_zip_file()
                else:
                    # Try using the selected folder anyway
                    self._set_asset_source(path_obj, is_zip=False)
                    QMessageBox.warning(self, "Warning", "Using selected folder. Data may not be valid.")
        else:
            # If folder selection cancelled, try file selection
            self._select_specific_zip_file()
    
    def _select_specific_zip_file(self):
        """Let user select a specific ZIP file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select 0 A.D. public.zip File",
            self.settings.game_data_path or str(Path.home()),
            "ZIP Files (*.zip);;All Files (*)"
        )
        
        if path:
            path_obj = Path(path)
            if path_obj.exists() and path_obj.suffix == '.zip':
                self._set_asset_source(path_obj, is_zip=True)
                QMessageBox.information(self, "Success", f"Loaded 0 A.D. data from: {path_obj.name}")
            else:
                QMessageBox.warning(self, "Invalid File", "Please select a valid .zip file")
    
    def action_build(self):
        if not self.project or not self.project.is_loaded:
            QMessageBox.warning(self, "No Mod", "No mod is currently loaded.")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save .pyromod File",
            f"{self.project.info.name}.pyromod",
            "Pyromod Files (*.pyromod);;All Files (*)"
        )
        
        if save_path:
            try:
                output = self.project.build_pyromod(Path(save_path))
                QMessageBox.information(self, "Success", f"Mod built successfully!\nSaved to: {output}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to build mod: {e}")
    
    def action_run_in_0ad(self):
        """Run the mod in 0 A.D."""
        if not self.project or not self.project.is_loaded:
            QMessageBox.warning(self, "No Mod", "No mod is currently loaded.")
            return
        
        # First build the mod
        try:
            with tempfile.NamedTemporaryFile(suffix='.pyromod', delete=False) as tmp:
                output = self.project.build_pyromod(Path(tmp.name))
                tmp_path = output
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to build mod: {e}")
            return
        
        # Find 0 A.D. executable
        system = platform.system()
        if system == "Darwin":  # macOS
            ad_path = "/Applications/0ad.app/Contents/MacOS/0ad"
        elif system == "Windows":
            ad_path = "C:\\Program Files\\0 A.D.\\binaries\\system\\0ad.exe"
        else:  # Linux
            ad_path = "/usr/local/bin/0ad"
        
        if not Path(ad_path).exists():
            reply = QMessageBox.question(
                self, "0 A.D. Not Found",
                f"Could not find 0 A.D. at {ad_path}\n\nDo you want to select the 0 A.D. executable manually?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                ad_path, _ = QFileDialog.getOpenFileName(
                    self, "Select 0 A.D. Executable",
                    str(Path.home()),
                    "Executable Files (*)"
                )
                if not ad_path:
                    return
            else:
                return
        
        # Run 0 A.D. with the mod
        try:
            # Validate the executable path before launching
            ad_path_obj = Path(ad_path)
            if not ad_path_obj.exists():
                QMessageBox.critical(self, "Error", f"Executable not found: {ad_path}")
                return
            
            subprocess.Popen([str(ad_path_obj), f"--mod={tmp_path}"])
            QMessageBox.information(self, "Success", "0 A.D. launched with your mod!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch 0 A.D.: {e}")
    
    def _refresh_current_view(self):
        """Refresh the current view."""
        current_index = self.content_stack.currentIndex()
        if current_index == 0:  # Assets
            if hasattr(self.assets_tab, '_load_root'):
                self.assets_tab._load_root()
        elif current_index == 1:  # Units
            if hasattr(self.units_tab, '_refresh_template_list'):
                self.units_tab._refresh_template_list()
        elif current_index == 8:  # Recent
            if hasattr(self.recent_tab, '_load_recent'):
                self.recent_tab._load_recent()
        
        QMessageBox.information(self, "Refreshed", "Current view has been refreshed!")
    
    def _show_help(self):
        """Show help for the current section."""
        current_index = self.content_stack.currentIndex()
        help_texts = {
            0: """📁 Assets Tab Help

Browse and import game assets from 0 A.D.:

• Use the quick navigation buttons to jump to specific folders
• Double-click files to import them into your mod
• Use "Browse Folder" for detailed navigation
• Import selected files with the import button

Tips:
• Start with Units, Techs, or Structures for common assets
• Files are automatically added to your mod project
• Check the Overview tab to see imported files""",
            1: """⚔️ Units Tab Help

Edit and manage unit templates:

• Select a unit template from the list
• Edit properties in the form
• Save changes to update the unit
• Use the search to find specific units

Tips:
• Units inherit from parent templates
• Changes affect your mod's version of the unit
• Test units in 0 A.D. after modifications""",
            2: """✨ New Unit Tab Help

Create new custom units:

• Fill in the unit details
• Select a parent template
• Configure properties like health, speed, costs
• Save to add to your mod

Tips:
• Choose an appropriate parent template
• Start with similar units as templates
• Test new units in-game""",
            6: """🔧 Settings Tab Help

Configure your mod project:

• Set mod name and display label
• Configure version number
• Add description
• Set dependencies

Each setting:
• Mod Name: Internal identifier (no spaces)
• Display Label: User-friendly name shown in game
• Version: Follow semantic versioning (x.y.z)
• Description: What your mod does
• Dependencies: Required mods/versions""",
            7: """📊 Overview Tab Help

View your mod's structure and contents:

• See all files in your mod
• View mod information
• Check mod statistics
• Verify mod structure

Tips:
• Use this to verify your mod is complete
• Check file counts and sizes
• Review mod info before building""",
            8: """🕒 Recent Tab Help

Access recent projects:

• Double-click to open a project
• Right-click to remove from recent list
• Projects are automatically added when opened
• Missing projects are shown in gray

Tips:
• Recent projects persist between sessions
• Use this to quickly resume work
• Clean up old projects to keep list manageable""",
        }
        
        help_text = help_texts.get(current_index, "No help available for this section yet.")
        QMessageBox.information(self, "Help", help_text)
    
    def action_about(self):
        about_text = f"""
        <h2>🎮 0 A.D. Mod Maker</h2>
        <p><b>Version:</b> {__version__}</p>
        <p>A modern tool for creating and managing 0 A.D. mods.</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Create and edit mod projects</li>
            <li>Browse and import game assets</li>
            <li>Edit unit templates</li>
            <li>Build .pyromod files for distribution</li>
            <li>Test mods directly in 0 A.D.</li>
        </ul>
        <p><b>Created with:</b> PyQt6, Python</p>
        """
        QMessageBox.about(self, "About 0 A.D. Mod Maker", about_text)
    
    def action_shortcuts(self):
        shortcuts_text = """
        <h2>⌨️ Keyboard Shortcuts</h2>
        <table border="1" cellpadding="5" cellspacing="0">
        <tr><td><b>Ctrl+N</b></td><td>New Mod</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Open Mod</td></tr>
        <tr><td><b>Ctrl+B</b></td><td>Build .pyromod</td></tr>
        <tr><td><b>Ctrl+R</b></td><td>Run Mod in 0 A.D.</td></tr>
        <tr><td><b>Ctrl+Q</b></td><td>Exit</td></tr>
        </table>
        <p><i>More shortcuts may be available in specific tabs and dialogs.</i></p>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts_text)
