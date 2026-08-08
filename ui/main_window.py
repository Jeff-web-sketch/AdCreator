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
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel,
    QStatusBar, QMenuBar, QMenu, QMessageBox, QFileDialog,
    QLineEdit, QTextEdit, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QPalette

from core.assets import AssetSource, FolderAssetSource, ZipAssetSource
from core.mod import ModProject
from core.settings import AppSettings
from core.game import GameDataLocator
from ui.styles import get_dark_theme_palette, get_button_style
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
        self.setWindowTitle("0 A.D. Mod Maker")
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
        new_action.triggered.connect(self.action_new_mod)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Mod...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.action_open_mod)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        set_folder_action = QAction("Set Game Data Folder...", self)
        set_folder_action.triggered.connect(self.action_set_game_folder)
        file_menu.addAction(set_folder_action)
        
        file_menu.addSeparator()
        
        build_action = QAction("Build .pyromod", self)
        build_action.setShortcut("Ctrl+B")
        build_action.triggered.connect(self.action_build)
        file_menu.addAction(build_action)
        
        run_action = QAction("Run Mod in 0AD", self)
        run_action.setShortcut("Ctrl+R")
        run_action.triggered.connect(self.action_run_in_0ad)
        file_menu.addAction(run_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.action_about)
        help_menu.addAction(about_action)
    
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #383848;
                color: #ffffff;
                border-top: 1px solid #6a6a8a;
            }
        """)
        self.setStatusBar(self.status_bar)
        
        self.lbl_game_status = QLabel("🔍 Detecting 0 A.D.…")
        self.lbl_game_status.setStyleSheet("color: #c0c0d0; font-size: 12px;")
        self.status_bar.addWidget(self.lbl_game_status)
        
        self.status_bar.addPermanentWidget(QLabel(" | "))
        
        self.lbl_mod_status = QLabel("No mod loaded")
        self.lbl_mod_status.setStyleSheet("color: #c0c0d0; font-size: 12px;")
        self.status_bar.addPermanentWidget(self.lbl_mod_status)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #6a6a8a;
                background-color: #2d2d3d;
            }
            QTabBar::tab {
                background-color: #383848;
                color: #c0c0d0;
                padding: 10px 20px;
                border: 1px solid #6a6a8a;
                border-bottom: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #7b5eff;
                color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background-color: #4d4d5d;
            }
        """)
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_tabs()
    
    def _create_tabs(self):
        # Clear existing tabs
        self.tab_widget.clear()
        
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
        
        # Add tabs
        self.tab_widget.addTab(self.assets_tab, "📁 Assets")
        self.tab_widget.addTab(self.units_tab, "⚔️ Units")
        self.tab_widget.addTab(self.new_unit_tab, "✨ New Unit")
        self.tab_widget.addTab(self.techs_tab, "🔬 Techs")
        self.tab_widget.addTab(self.structures_tab, "🏛️ Structures")
        self.tab_widget.addTab(self.auras_tab, "✨ Auras")
        self.tab_widget.addTab(self.settings_tab, "🔧 Settings")
        self.tab_widget.addTab(self.overview_tab, "📊 Overview")
        self.tab_widget.addTab(self.recent_tab, "🕒 Recent")
        self.tab_widget.addTab(self.structure_tab, "🏗️ Structure")
    
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
                self.tab_widget.setCurrentIndex(4)  # Overview tab
                
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
        path, _ = QFileDialog.getOpenFileName(
            self, "Select 0 A.D. Data File (public.zip or folder)",
            self.settings.game_data_path or str(Path.home()),
            "ZIP Files (*.zip);;All Files (*)"
        )
        
        if not path:
            folder = QFileDialog.getExistingDirectory(
                self, "Select 0 A.D. Data Folder",
                self.settings.game_data_path or str(Path.home())
            )
            if folder:
                path = folder
        
        if path:
            path_obj = Path(path)
            
            if path_obj.is_file() and path_obj.suffix == '.zip':
                self._set_asset_source(path_obj, is_zip=True)
            elif path_obj.is_dir():
                public_zip = path_obj / "public.zip"
                public_folder = path_obj / "binaries" / "data" / "mods" / "public"
                
                if public_zip.exists():
                    self._set_asset_source(public_zip, is_zip=True)
                elif public_folder.exists():
                    self._set_asset_source(public_folder, is_zip=False)
                else:
                    self._set_asset_source(path_obj, is_zip=False)
    
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
    
    def action_about(self):
        QMessageBox.about(self, "About", "0 A.D. Mod Maker\n\nA tool for creating and managing 0 A.D. mods.")
