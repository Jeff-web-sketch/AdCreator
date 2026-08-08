"""Main GUI application using PyQt6 for professional styling."""

import sys
import time
import shutil
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QPushButton, QFrame, QStatusBar, QMenuBar, QMenu,
    QMessageBox, QFileDialog, QTextEdit, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QSplitter, QScrollArea, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QAction, QPalette, QColor

from constants import STYLE
from settings import AppSettings
from game_data import GameDataLocator
from asset_source import LocalAssetSource
from mod_project import ModProject
from unit_template import UnitTemplate

class WindowDefaults:
    """Default window dimensions and constraints."""
    MIN_WIDTH = 900
    MIN_HEIGHT = 600
    DEFAULT_WIDTH = 1100
    DEFAULT_HEIGHT = 720

class ModMakerGUI(QMainWindow):
    """Main GUI application for the 0 A.D. Mod Maker using PyQt6."""

    def __init__(self):
        super().__init__()
        self.settings = AppSettings()
        self.asset_source: Optional[LocalAssetSource] = None
        self.project: Optional[ModProject] = None
        self.current_template: Optional[UnitTemplate] = None
        self.current_template_path: Optional[Path] = None
        
        # UI component references
        self.asset_tree = None
        self.unit_tree = None
        self.recent_tree = None
        self.modinfo_inputs = {}
        self.structure_tree = None

        self._setup_window()
        self._setup_dark_theme()
        self._build_menubar()
        self._build_layout()
        self._auto_detect_game()

    def _setup_window(self):
        self.setWindowTitle("0 A.D. Mod Maker")
        w = self.settings.get("window_width", WindowDefaults.DEFAULT_WIDTH)
        h = self.settings.get("window_height", WindowDefaults.DEFAULT_HEIGHT)
        self.resize(w, h)
        self.setMinimumSize(WindowDefaults.MIN_WIDTH, WindowDefaults.MIN_HEIGHT)

    def _setup_dark_theme(self):
        """Setup modern dark theme with high contrast."""
        app = QApplication.instance()
        palette = QPalette()
        
        # Dark theme colors
        bg_color = QColor("#2d2d3d")
        fg_color = QColor("#ffffff")
        accent_color = QColor("#7b5eff")
        panel_color = QColor("#383848")
        input_bg = QColor("#1a1a2a")
        border_color = QColor("#6a6a8a")
        
        # Set palette colors
        palette.setColor(QPalette.ColorRole.Window, bg_color)
        palette.setColor(QPalette.ColorRole.WindowText, fg_color)
        palette.setColor(QPalette.ColorRole.Base, input_bg)
        palette.setColor(QPalette.ColorRole.AlternateBase, panel_color)
        palette.setColor(QPalette.ColorRole.ToolTipBase, fg_color)
        palette.setColor(QPalette.ColorRole.ToolTipText, fg_color)
        palette.setColor(QPalette.ColorRole.Text, fg_color)
        palette.setColor(QPalette.ColorRole.Button, panel_color)
        palette.setColor(QPalette.ColorRole.ButtonText, fg_color)
        palette.setColor(QPalette.ColorRole.BrightText, fg_color)
        palette.setColor(QPalette.ColorRole.Link, accent_color)
        palette.setColor(QPalette.ColorRole.Highlight, accent_color)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        
        app.setPalette(palette)
        
        # Set default font
        font = QFont("Segoe UI", 10)
        app.setFont(font)

    def _build_menubar(self):
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
        
        recent_action = QAction("Load Recent", self)
        recent_action.setShortcut("Ctrl+R")
        recent_action.triggered.connect(self.action_show_recent)
        file_menu.addAction(recent_action)
        
        file_menu.addSeparator()
        
        set_folder_action = QAction("Set Game Data Folder...", self)
        set_folder_action.triggered.connect(self.action_set_game_folder)
        file_menu.addAction(set_folder_action)
        
        file_menu.addSeparator()
        
        build_action = QAction("Build .pyromod", self)
        build_action.setShortcut("Ctrl+B")
        build_action.triggered.connect(self.action_build)
        file_menu.addAction(build_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.action_about)
        help_menu.addAction(about_action)

    def _build_layout(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
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
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.tab_assets = QWidget()
        self.tab_units = QWidget()
        self.tab_new_unit = QWidget()
        self.tab_modinfo = QWidget()
        self.tab_summary = QWidget()
        self.tab_recent = QWidget()
        self.tab_structure = QWidget()
        
        self.tab_widget.addTab(self.tab_assets, "📁 Assets")
        self.tab_widget.addTab(self.tab_units, "⚔️ Units")
        self.tab_widget.addTab(self.tab_new_unit, "✨ New Unit")
        self.tab_widget.addTab(self.tab_modinfo, "🔧 Settings")
        self.tab_widget.addTab(self.tab_summary, "📊 Overview")
        self.tab_widget.addTab(self.tab_recent, "🕒 Recent")
        self.tab_widget.addTab(self.tab_structure, "🏗️ Structure")
        
        # Initialize recent tree reference
        self.recent_tree = None
        
        # Build tab contents
        self._build_tab_assets()
        self._build_tab_units()
        self._build_tab_new_unit()
        self._build_tab_modinfo()
        self._build_tab_summary()
        self._build_tab_recent()
        self._build_tab_structure()
        
        # Store summary layout for refreshing
        self.summary_layout = None

    def _build_tab_assets(self):
        """Build the Assets browser tab."""
        try:
            layout = QVBoxLayout(self.tab_assets)
            layout.setContentsMargins(10, 10, 10, 10)
            
            # Toolbar
            toolbar = QFrame()
            toolbar.setStyleSheet("background-color: #383848; border-radius: 5px; padding: 5px;")
            toolbar_layout = QHBoxLayout(toolbar)
            
            # Search
            search_label = QLabel("🔍")
            search_label.setStyleSheet("font-size: 14px;")
            toolbar_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Filter files...")
            self.search_input.setStyleSheet("""
                QLineEdit {
                    background-color: #1a1a2a;
                    color: #ffffff;
                    border: 2px solid #6a6a8a;
                    border-radius: 5px;
                    padding: 5px;
                }
                QLineEdit:focus {
                    border-color: #7b5eff;
                }
            """)
            self.search_input.setMaximumWidth(300)
            toolbar_layout.addWidget(self.search_input)
            
            # Connect search input to filter
            self.search_input.textChanged.connect(self._on_search_changed)
            
            # Navigation buttons
            nav_button = QPushButton("📄 Templates")
            nav_button.setStyleSheet(self._get_button_style())
            nav_button.clicked.connect(lambda: self._navigate_to_folder("simulation/templates"))
            toolbar_layout.addWidget(nav_button)
            
            nav_button2 = QPushButton("🎨 Meshes")
            nav_button2.setStyleSheet(self._get_button_style())
            nav_button2.clicked.connect(lambda: self._navigate_to_folder("art/meshes"))
            toolbar_layout.addWidget(nav_button2)
            
            nav_button3 = QPushButton("🎵 Sounds")
            nav_button3.setStyleSheet(self._get_button_style())
            nav_button3.clicked.connect(lambda: self._navigate_to_folder("audio"))
            toolbar_layout.addWidget(nav_button3)
            
            browse_folder_btn = QPushButton("📂 Browse Folder")
            browse_folder_btn.setStyleSheet(self._get_button_style())
            browse_folder_btn.clicked.connect(self._browse_game_folder)
            toolbar_layout.addWidget(browse_folder_btn)
            
            toolbar_layout.addStretch()
            
            # Action buttons
            import_btn = QPushButton("📥 Import")
            import_btn.setStyleSheet(self._get_accent_button_style())
            toolbar_layout.addWidget(import_btn)
            
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setStyleSheet(self._get_button_style())
            toolbar_layout.addWidget(edit_btn)
            
            reload_btn = QPushButton("🔄 Reload")
            reload_btn.setStyleSheet(self._get_button_style())
            toolbar_layout.addWidget(reload_btn)
            
            # Connect reload button
            reload_btn.clicked.connect(self._reload_asset_tree)
            
            layout.addWidget(toolbar)
            
            # Tree view
            self.asset_tree = QTreeWidget()
            self.asset_tree.setHeaderLabels(["Name", "Type", "Size"])
            self.asset_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #1a1a2a;
                    color: #ffffff;
                    border: 2px solid #6a6a8a;
                    border-radius: 5px;
                    font-family: Consolas;
                    font-size: 10px;
                }
                QTreeWidget::item {
                    padding: 5px;
                    border-bottom: 1px solid #3a3a4a;
                }
                QTreeWidget::item:selected {
                    background-color: #7b5eff;
                    color: #ffffff;
                }
                QTreeWidget::header {
                    background-color: #383848;
                    color: #ffffff;
                    border-bottom: 2px solid #6a6a8a;
                    padding: 5px;
                    font-weight: bold;
                }
            """)
            self.asset_tree.itemExpanded.connect(self._on_tree_expand)
            layout.addWidget(self.asset_tree)
        except Exception as e:
            print(f"Error building assets tab: {e}")
            import traceback
            traceback.print_exc()

    def _build_tab_units(self):
        """Build the Units Editor tab."""
        try:
            layout = QVBoxLayout(self.tab_units)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Header
            title = QLabel("⚔️ Unit Editor")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
            layout.addWidget(title)
            
            subtitle = QLabel("Edit and modify unit templates from your loaded mod")
            subtitle.setStyleSheet("color: #c0c0d0; font-size: 12px;")
            layout.addWidget(subtitle)
            
            # Toolbar
            toolbar = QFrame()
            toolbar.setStyleSheet("background-color: #383848; border-radius: 5px; padding: 5px;")
            toolbar_layout = QHBoxLayout(toolbar)
            
            refresh_btn = QPushButton("🔄 Refresh")
            refresh_btn.setStyleSheet(self._get_button_style())
            refresh_btn.clicked.connect(self._load_unit_list)
            toolbar_layout.addWidget(refresh_btn)
            
            import_btn = QPushButton("📥 Import from Game")
            import_btn.setStyleSheet(self._get_button_style())
            import_btn.clicked.connect(self._import_unit_from_game)
            toolbar_layout.addWidget(import_btn)
            
            toolbar_layout.addStretch()
            layout.addWidget(toolbar)
            
            # Placeholder content
            if not self.project or not self.project.is_loaded:
                info_label = QLabel("⚠️ No mod loaded. Create or open a mod to edit units.")
                info_label.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
                info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(info_label)
            else:
                # Unit list
                self.unit_tree = QTreeWidget()
                self.unit_tree.setHeaderLabels(["Unit Name", "Parent", "Civ"])
                self.unit_tree.setStyleSheet("""
                    QTreeWidget {
                        background-color: #1a1a2a;
                        color: #ffffff;
                        border: 2px solid #6a6a8a;
                        border-radius: 5px;
                    }
                    QTreeWidget::item:selected {
                        background-color: #7b5eff;
                        color: #ffffff;
                    }
                    QTreeWidget::header {
                        background-color: #383848;
                        color: #ffffff;
                        border-bottom: 2px solid #6a6a8a;
                        padding: 5px;
                        font-weight: bold;
                    }
                """)
                self.unit_tree.itemDoubleClicked.connect(self._on_unit_double_click)
                layout.addWidget(self.unit_tree)
                
                # Unit editing area
                edit_frame = QFrame()
                edit_frame.setStyleSheet("""
                    QFrame {
                        background-color: #404050;
                        border: 2px solid #6a6a8a;
                        border-radius: 8px;
                        padding: 15px;
                    }
                """)
                edit_layout = QVBoxLayout(edit_frame)
                
                edit_title = QLabel("Unit Properties")
                edit_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #7b5eff;")
                edit_layout.addWidget(edit_title)
                
                info_label = QLabel("Select a unit to edit its properties")
                info_label.setStyleSheet("color: #c0c0d0; font-size: 12px;")
                edit_layout.addWidget(info_label)
                
                layout.addWidget(edit_frame)
                
                # Load units from project
                self._load_unit_list()
        except Exception as e:
            print(f"Error building units tab: {e}")
            import traceback
            traceback.print_exc()

    def _import_unit_from_game(self):
        """Import a unit template from game assets."""
        if not self.asset_source:
            QMessageBox.warning(self, "No Game Data", "Please set the game data folder first.")
            return
        
        # Create dialog to browse templates
        dialog = QDialog(self)
        dialog.setWindowTitle("Import Unit from Game")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Search
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍")
        search_label.setStyleSheet("font-size: 14px;")
        search_layout.addWidget(search_label)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Filter templates...")
        search_input.setStyleSheet(self._get_input_style())
        search_layout.addWidget(search_input)
        
        layout.addLayout(search_layout)
        
        # Template tree
        template_tree = QTreeWidget()
        template_tree.setHeaderLabels(["Template Name"])
        template_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1a1a2a;
                color: #ffffff;
                border: 2px solid #6a6a8a;
                border-radius: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #7b5eff;
                color: #ffffff;
            }
            QTreeWidget::header {
                background-color: #383848;
                color: #ffffff;
                border-bottom: 2px solid #6a6a8a;
                padding: 5px;
                font-weight: bold;
            }
        """)
        layout.addWidget(template_tree)
        
        # Populate with available templates
        try:
            templates = self.asset_source.list_unit_templates()
            for template in templates:
                item = QTreeWidgetItem(template_tree)
                item.setText(0, template.name)
                item.setData(0, Qt.ItemDataRole.UserRole, template.full_path)
                template_tree.addTopLevelItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load templates: {e}")
        
        # Buttons
        button_layout = QHBoxLayout()
        import_btn = QPushButton("📥 Import Selected")
        import_btn.setStyleSheet(self._get_accent_button_style())
        import_btn.clicked.connect(lambda: self._import_selected_unit(template_tree, dialog))
        button_layout.addWidget(import_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(self._get_button_style())
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        dialog.exec()

    def _import_selected_unit(self, template_tree: QTreeWidget, dialog: QDialog):
        """Import the selected unit template."""
        selected = template_tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a template first.")
            return
        
        if not self.project or not self.project.is_loaded:
            QMessageBox.warning(self, "No Mod", "Please create or open a mod first.")
            return
        
        try:
            template_path = selected[0].data(0, Qt.ItemDataRole.UserRole)
            if self.asset_source:
                # Read the template content
                content = self.asset_source.read_text(template_path)
                if content:
                    # Create unit path in mod
                    unit_name = Path(template_path).name
                    mod_unit_path = self.project.mod_dir / "simulation" / "templates" / "units" / unit_name
                    mod_unit_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write the template
                    mod_unit_path.write_text(content, encoding="utf-8")
                    
                    QMessageBox.information(self, "Success", f"Unit '{unit_name}' imported successfully!")
                    dialog.accept()
                    self._load_unit_list()
                else:
                    QMessageBox.warning(self, "Error", "Could not read template content.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import unit: {e}")

    def _on_unit_double_click(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on unit to edit."""
        if self.project and self.project.is_loaded:
            unit_name = item.text(0)
            QMessageBox.information(self, "Edit Unit", f"Edit functionality for '{unit_name}' coming soon!")

    def _build_tab_new_unit(self):
        """Build the New Unit Creator tab."""
        try:
            layout = QVBoxLayout(self.tab_new_unit)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Header
            title = QLabel("✨ New Unit Creator")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
            layout.addWidget(title)
            
            subtitle = QLabel("Create new unit templates based on existing parent templates")
            subtitle.setStyleSheet("color: #c0c0d0; font-size: 12px;")
            layout.addWidget(subtitle)
            
            # Form container
            form_frame = QFrame()
            form_frame.setStyleSheet("""
                QFrame {
                    background-color: #404050;
                    border: 2px solid #6a6a8a;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            form_layout = QFormLayout(form_frame)
            
            # Unit name
            name_input = QLineEdit()
            name_input.setPlaceholderText("e.g., my_spearman")
            name_input.setStyleSheet(self._get_input_style())
            form_layout.addRow("Unit Name:", name_input)
            
            # Parent template with browse button
            parent_layout = QHBoxLayout()
            parent_input = QLineEdit()
            parent_input.setPlaceholderText("template_unit_infantry_melee_spearman")
            parent_input.setStyleSheet(self._get_input_style())
            parent_layout.addWidget(parent_input)
            
            browse_btn = QPushButton("🔍 Browse")
            browse_btn.setStyleSheet(self._get_button_style())
            browse_btn.clicked.connect(lambda: self._browse_parent_template(parent_input))
            parent_layout.addWidget(browse_btn)
            
            form_layout.addRow("Parent Template:", parent_layout)
            
            # Civilization
            civ_combo = QLineEdit()
            civ_combo.setPlaceholderText("gaia")
            civ_combo.setStyleSheet(self._get_input_style())
            form_layout.addRow("Civilization:", civ_combo)
            
            # Display name
            display_input = QLineEdit()
            display_input.setPlaceholderText("My Spearman")
            display_input.setStyleSheet(self._get_input_style())
            form_layout.addRow("Display Name:", display_input)
            
            layout.addWidget(form_frame)
            
            # Create button
            create_btn = QPushButton("✨ Create Unit")
            create_btn.setStyleSheet(self._get_accent_button_style())
            layout.addWidget(create_btn)
            
            layout.addStretch()
        except Exception as e:
            print(f"Error building new unit tab: {e}")
            import traceback
            traceback.print_exc()

    def _browse_parent_template(self, parent_input: QLineEdit):
        """Browse for parent template from game assets."""
        if not self.asset_source:
            QMessageBox.warning(self, "No Game Data", "Please set the game data folder first.")
            return
        
        # Create a dialog to browse templates
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Parent Template")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Search
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍")
        search_label.setStyleSheet("font-size: 14px;")
        search_layout.addWidget(search_label)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Filter templates...")
        search_input.setStyleSheet(self._get_input_style())
        search_layout.addWidget(search_input)
        
        layout.addLayout(search_layout)
        
        # Template tree
        template_tree = QTreeWidget()
        template_tree.setHeaderLabels(["Template Name"])
        template_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1a1a2a;
                color: #ffffff;
                border: 2px solid #6a6a8a;
                border-radius: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #7b5eff;
                color: #ffffff;
            }
            QTreeWidget::header {
                background-color: #383848;
                color: #ffffff;
                border-bottom: 2px solid #6a6a8a;
                padding: 5px;
                font-weight: bold;
            }
        """)
        layout.addWidget(template_tree)
        
        # Populate with available templates
        try:
            templates = self.asset_source.list_unit_templates()
            for template in templates:
                item = QTreeWidgetItem(template_tree)
                item.setText(0, template.name)
                template_tree.addTopLevelItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load templates: {e}")
        
        # Buttons
        button_layout = QHBoxLayout()
        select_btn = QPushButton("Select")
        select_btn.setStyleSheet(self._get_accent_button_style())
        select_btn.clicked.connect(lambda: self._select_parent_template(template_tree, parent_input, dialog))
        button_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(self._get_button_style())
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        dialog.exec()

    def _select_parent_template(self, template_tree: QTreeWidget, parent_input: QLineEdit, dialog: QDialog):
        """Select a parent template and close dialog."""
        selected = template_tree.selectedItems()
        if selected:
            parent_input.setText(selected[0].text(0))
            dialog.accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a template first.")

    def _build_tab_structure(self):
        """Build the Structure tab - shows mod folder structure."""
        try:
            layout = QVBoxLayout(self.tab_structure)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Header
            title = QLabel("🏗️ Mod Structure")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
            layout.addWidget(title)
            
            subtitle = QLabel("View and manage your mod's folder structure")
            subtitle.setStyleSheet("color: #c0c0d0; font-size: 12px;")
            layout.addWidget(subtitle)
            
            if not self.project or not self.project.is_loaded:
                info_label = QLabel("⚠️ No mod loaded. Create or open a mod to view structure.")
                info_label.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
                info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(info_label)
            else:
                # Toolbar
                toolbar = QFrame()
                toolbar.setStyleSheet("background-color: #383848; border-radius: 5px; padding: 5px;")
                toolbar_layout = QHBoxLayout(toolbar)
                
                refresh_btn = QPushButton("🔄 Refresh")
                refresh_btn.setStyleSheet(self._get_button_style())
                refresh_btn.clicked.connect(self._refresh_structure)
                toolbar_layout.addWidget(refresh_btn)
                
                add_folder_btn = QPushButton("📁 Add Folder")
                add_folder_btn.setStyleSheet(self._get_button_style())
                toolbar_layout.addWidget(add_folder_btn)
                
                import_btn = QPushButton("📥 Import File")
                import_btn.setStyleSheet(self._get_button_style())
                toolbar_layout.addWidget(import_btn)
                
                toolbar_layout.addStretch()
                layout.addWidget(toolbar)
                
                # Folder structure tree
                self.structure_tree = QTreeWidget()
                self.structure_tree.setHeaderLabels(["Path", "Type"])
                self.structure_tree.setStyleSheet("""
                    QTreeWidget {
                        background-color: #1a1a2a;
                        color: #ffffff;
                        border: 2px solid #6a6a8a;
                        border-radius: 5px;
                    }
                    QTreeWidget::item:selected {
                        background-color: #7b5eff;
                        color: #ffffff;
                    }
                    QTreeWidget::header {
                        background-color: #383848;
                        color: #ffffff;
                        border-bottom: 2px solid #6a6a8a;
                        padding: 5px;
                        font-weight: bold;
                    }
                """)
                layout.addWidget(self.structure_tree)
                
                # Load initial structure
                self._refresh_structure()
                
                # Action buttons
                action_frame = QFrame()
                action_layout = QHBoxLayout(action_frame)
                
                delete_btn = QPushButton("🗑️ Delete Selected")
                delete_btn.setStyleSheet(self._get_button_style())
                action_layout.addWidget(delete_btn)
                
                action_layout.addStretch()
                layout.addWidget(action_frame)
        except Exception as e:
            print(f"Error building structure tab: {e}")
            import traceback
            traceback.print_exc()

    def _refresh_structure(self):
        """Refresh the structure tree with current mod files."""
        if not hasattr(self, 'structure_tree') or not self.project or not self.project.is_loaded:
            return
        
        try:
            self.structure_tree.clear()
            
            files = self.project.list_files()
            for file_path in files:
                relative_path = file_path.relative_to(self.project.mod_dir)
                item = QTreeWidgetItem(self.structure_tree)
                item.setText(0, str(relative_path))
                item.setText(1, "File" if file_path.is_file() else "Directory")
                self.structure_tree.addTopLevelItem(item)
                
            # Add mod.json
            mod_json = self.project.mod_dir / "mod.json"
            if mod_json.exists():
                item = QTreeWidgetItem(self.structure_tree)
                item.setText(0, "mod.json")
                item.setText(1, "Config")
                self.structure_tree.addTopLevelItem(item)
        except Exception as e:
            print(f"Error refreshing structure: {e}")

    def _build_tab_summary(self):
        """Build the Overview/Summary tab."""
        try:
            layout = QVBoxLayout(self.tab_summary)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Header
            title = QLabel("📊 Mod Overview")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
            layout.addWidget(title)
            
            subtitle = QLabel("Summary of your mod project and its contents")
            subtitle.setStyleSheet("color: #c0c0d0; font-size: 12px;")
            layout.addWidget(subtitle)
            
            if not self.project or not self.project.is_loaded:
                info_label = QLabel("⚠️ No mod loaded. Create or open a mod to see overview.")
                info_label.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
                info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(info_label)
            else:
                # Mod info card
                info_card = QFrame()
                info_card.setStyleSheet("""
                    QFrame {
                        background-color: #404050;
                        border: 2px solid #6a6a8a;
                        border-radius: 8px;
                        padding: 20px;
                    }
                """)
                info_layout = QVBoxLayout(info_card)
                
                # Mod details
                info_title = QLabel(f"📦 {self.project.info.label}")
                info_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
                info_layout.addWidget(info_title)
                
                details = QLabel(
                    f"Internal Name: {self.project.info.name}\n"
                    f"Version: {self.project.info.version}\n"
                    f"Type: {self.project.info.type}\n"
                    f"Dependencies: {', '.join(self.project.info.dependencies)}"
                )
                details.setStyleSheet("color: #c0c0d0; font-size: 12px;")
                info_layout.addWidget(details)
                
                layout.addWidget(info_card)
                
                # File count
                files = self.project.list_files()
                file_count_label = QLabel(f"📁 Total Files: {len(files)}")
                file_count_label.setStyleSheet("color: #4ade80; font-size: 14px; font-weight: bold;")
                layout.addWidget(file_count_label)
                
                # File list
                file_tree = QTreeWidget()
                file_tree.setHeaderLabels(["File Path"])
                file_tree.setStyleSheet("""
                    QTreeWidget {
                        background-color: #1a1a2a;
                        color: #ffffff;
                        border: 2px solid #6a6a8a;
                        border-radius: 5px;
                    }
                    QTreeWidget::item:selected {
                        background-color: #7b5eff;
                        color: #ffffff;
                    }
                    QTreeWidget::header {
                        background-color: #383848;
                        color: #ffffff;
                        border-bottom: 2px solid #6a6a8a;
                        padding: 5px;
                        font-weight: bold;
                    }
                """)
                
                for file_path in files:
                    item = QTreeWidgetItem(file_tree)
                    item.setText(0, str(file_path.relative_to(self.project.mod_dir)))
                    file_tree.addTopLevelItem(item)
                
                layout.addWidget(file_tree)
                
                # Build button
                build_btn = QPushButton("🔨 Build .pyromod")
                build_btn.setStyleSheet(self._get_accent_button_style())
                build_btn.clicked.connect(self.action_build)
                layout.addWidget(build_btn)
                
                layout.addStretch()
        except Exception as e:
            print(f"Error building summary tab: {e}")
            import traceback
            traceback.print_exc()

    def _get_input_style(self):
        """Get input field style."""
        return """
            QLineEdit {
                background-color: #1a1a2a;
                color: #ffffff;
                border: 2px solid #6a6a8a;
                border-radius: 5px;
                padding: 8px;
            }
            QLineEdit:focus {
                border-color: #7b5eff;
            }
        """

    def _load_unit_list(self):
        """Load unit templates from the project."""
        if not hasattr(self, 'unit_tree') or not self.unit_tree:
            return
        
        self.unit_tree.clear()
        
        if not self.project or not self.project.is_loaded:
            return
        
        try:
            units_dir = self.project.mod_dir / "simulation" / "templates" / "units"
            if not units_dir.exists():
                # Show message if no units directory
                item = QTreeWidgetItem(self.unit_tree)
                item.setText(0, "No units yet - Import from game or create new units")
                item.setText(1, "")
                item.setText(2, "")
                item.setForeground(0, QColor("#9090a0"))
                self.unit_tree.addTopLevelItem(item)
                return
            
            units = self.project.list_files("simulation/templates/units")
            if not units:
                # Show message if no units in directory
                item = QTreeWidgetItem(self.unit_tree)
                item.setText(0, "No units yet - Import from game or create new units")
                item.setText(1, "")
                item.setText(2, "")
                item.setForeground(0, QColor("#9090a0"))
                self.unit_tree.addTopLevelItem(item)
                return
            
            for unit_path in units:
                if unit_path.suffix == '.xml':
                    # Try to parse the unit template
                    try:
                        template = UnitTemplate.from_file(unit_path)
                        item = QTreeWidgetItem(self.unit_tree)
                        item.setText(0, unit_path.stem)
                        item.setText(1, template.parent_template)
                        item.setText(2, template.civ)
                        self.unit_tree.addTopLevelItem(item)
                    except Exception as e:
                        print(f"Error loading unit {unit_path}: {e}")
                        # Still add the item even if parsing fails
                        item = QTreeWidgetItem(self.unit_tree)
                        item.setText(0, unit_path.stem)
                        item.setText(1, "Unknown")
                        item.setText(2, "Unknown")
                        self.unit_tree.addTopLevelItem(item)
        except Exception as e:
            print(f"Error loading unit list: {e}")
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(f"Error loading unit list: {e}")

    def _refresh_summary(self):
        """Refresh the summary tab content."""
        # Simply switch to summary tab and let it rebuild when needed
        pass

    def _refresh_all_tabs(self):
        """Refresh all tabs to reflect current state."""
        # Only refresh if there's actually a project loaded
        if not self.project or not self.project.is_loaded:
            return
        
        # Just trigger a status update, tabs will refresh when visited
        self._update_status_bar()

    def _on_tab_changed(self, index: int):
        """Handle tab change events."""
        try:
            # Don't rebuild tabs that are already built
            if index == 0:  # Assets
                if not hasattr(self, 'asset_tree') or self.asset_tree is None:
                    self._build_tab_assets()
            elif index == 1:  # Units
                if not hasattr(self, 'unit_tree') or self.unit_tree is None:
                    self._build_tab_units()
                else:
                    # Just refresh the unit list
                    self._load_unit_list()
            elif index == 2:  # New Unit
                pass  # Static content, no rebuild needed
            elif index == 3:  # Settings
                if not hasattr(self, 'modinfo_inputs') or not self.modinfo_inputs:
                    self._build_tab_modinfo()
            elif index == 4:  # Overview
                # Always rebuild overview as it changes frequently
                if self.tab_summary.layout():
                    # Clear existing layout items safely
                    while self.tab_summary.layout().count():
                        item = self.tab_summary.layout().takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                self._build_tab_summary()
            elif index == 5:  # Recent
                if not hasattr(self, 'recent_tree') or self.recent_tree is None:
                    self._build_tab_recent()
                else:
                    # Just refresh the list
                    self._refresh_recent_list()
            elif index == 6:  # Structure
                if not hasattr(self, 'structure_tree') or self.structure_tree is None:
                    self._build_tab_structure()
                else:
                    # Just refresh the structure
                    self._refresh_structure()
        except Exception as e:
            print(f"Error changing tab: {e}")
            import traceback
            traceback.print_exc()

    def _build_tab_modinfo(self):
        """Build the Mod Info tab."""
        layout = QVBoxLayout(self.tab_modinfo)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🔧 Mod Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(title)
        
        subtitle = QLabel("Configure your mod's basic information and dependencies")
        subtitle.setStyleSheet("color: #c0c0d0; font-size: 12px;")
        layout.addWidget(subtitle)
        
        if not self.project or not self.project.is_loaded:
            info_label = QLabel("⚠️ No mod loaded. Create or open a mod to edit settings.")
            info_label.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info_label)
        else:
            # Form container with better visibility
            form_frame = QFrame()
            form_frame.setStyleSheet("""
                QFrame {
                    background-color: #404050;
                    border: 2px solid #6a6a8a;
                    border-radius: 8px;
                    padding: 20px;
                }
            """)
            form_layout = QVBoxLayout(form_frame)
            
            # Form fields with better styling
            fields = [
                ("Mod Name (internal)", "The technical identifier for your mod", self.project.info.name),
                ("Display Label", "The user-friendly name shown in game", self.project.info.label),
                ("Version", "Semantic versioning (e.g., 1.0.0)", self.project.info.version),
                ("Description", "Detailed description of your mod", self.project.info.description),
                ("Dependencies", "Comma-separated mod dependencies", ", ".join(self.project.info.dependencies)),
            ]
            
            self.modinfo_inputs = {}
            
            for label_text, help_text, default_value in fields:
                # Field header
                field_header = QLabel(f"{label_text} • {help_text}")
                field_header.setStyleSheet("color: #9090a0; font-size: 10px; margin-bottom: 5px;")
                form_layout.addWidget(field_header)
                
                # Input field with high visibility
                if label_text == "Description":
                    input_field = QTextEdit()
                    input_field.setPlainText(default_value)
                    input_field.setMaximumHeight(80)
                    input_field.setStyleSheet("""
                        QTextEdit {
                            background-color: #1a1a2a;
                            color: #ffffff;
                            border: 2px solid #7b5eff;
                            border-radius: 5px;
                            padding: 10px;
                            font-size: 12px;
                        }
                        QTextEdit:focus {
                            border-color: #9a7cff;
                            background-color: #252535;
                        }
                    """)
                else:
                    input_field = QLineEdit()
                    input_field.setText(default_value)
                    input_field.setStyleSheet("""
                        QLineEdit {
                            background-color: #1a1a2a;
                            color: #ffffff;
                            border: 2px solid #7b5eff;
                            border-radius: 5px;
                            padding: 10px;
                            font-size: 12px;
                        }
                        QLineEdit:focus {
                            border-color: #9a7cff;
                            background-color: #252535;
                        }
                    """)
                
                form_layout.addWidget(input_field)
                self.modinfo_inputs[label_text] = input_field
                
                form_layout.addSpacing(10)
            
            layout.addWidget(form_frame)
            
            # Save button
            save_btn = QPushButton("✨ Save Mod Info")
            save_btn.setStyleSheet(self._get_accent_button_style())
            save_btn.clicked.connect(self._save_mod_info)
            layout.addWidget(save_btn)
            
            layout.addStretch()

    def _save_mod_info(self):
        """Save the mod information from the settings form."""
        if not self.project or not self.project.is_loaded:
            QMessageBox.warning(self, "No Mod", "No mod is currently loaded.")
            return
        
        try:
            # Get values from input fields
            name = self.modinfo_inputs["Mod Name (internal)"].text().strip()
            label = self.modinfo_inputs["Display Label"].text().strip()
            version = self.modinfo_inputs["Version"].text().strip()
            description = self.modinfo_inputs["Description"].toPlainText().strip()
            deps_str = self.modinfo_inputs["Dependencies"].text().strip()
            
            # Update project info
            self.project.info.name = name
            self.project.info.label = label
            self.project.info.version = version
            self.project.info.description = description
            self.project.info.dependencies = [d.strip() for d in deps_str.split(",") if d.strip()]
            
            # Save to file
            self.project.save_info()
            
            # Update status bar
            self._update_status_bar()
            
            QMessageBox.information(self, "Success", "Mod metadata saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save mod info: {e}")

    def _build_tab_recent(self):
        """Build the Recent Projects tab."""
        try:
            layout = QVBoxLayout(self.tab_recent)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Header
            header_frame = QFrame()
            header_layout = QHBoxLayout(header_frame)
            
            title = QLabel("🕒 Recent Projects")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
            header_layout.addWidget(title)
            
            subtitle = QLabel("Quickly access your recently worked-on mods")
            subtitle.setStyleSheet("color: #c0c0d0; font-size: 12px;")
            header_layout.addWidget(subtitle)
            
            header_layout.addStretch()
            
            refresh_btn = QPushButton("🔄 Refresh")
            refresh_btn.setStyleSheet(self._get_button_style())
            header_layout.addWidget(refresh_btn)
            
            clear_btn = QPushButton("🗑️ Clear All")
            clear_btn.setStyleSheet(self._get_button_style())
            header_layout.addWidget(clear_btn)
            
            # Connect buttons
            refresh_btn.clicked.connect(self._refresh_recent_list)
            clear_btn.clicked.connect(self._clear_recent_projects)
            
            layout.addWidget(header_frame)
            
            # Recent projects tree
            self.recent_tree = QTreeWidget()
            self.recent_tree.setHeaderLabels(["📁 Mod Name", "📍 Location", "📅 Last Opened"])
            self.recent_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #1a1a2a;
                    color: #ffffff;
                    border: 2px solid #6a6a8a;
                    border-radius: 5px;
                }
                QTreeWidget::item:selected {
                    background-color: #7b5eff;
                    color: #ffffff;
                }
                QTreeWidget::header {
                    background-color: #383848;
                    color: #ffffff;
                    border-bottom: 2px solid #6a6a8a;
                    padding: 5px;
                    font-weight: bold;
                }
            """)
            layout.addWidget(self.recent_tree)
            
            # Action buttons
            button_frame = QFrame()
            button_layout = QHBoxLayout(button_frame)
            
            load_btn = QPushButton("📂 Load Selected")
            load_btn.setStyleSheet(self._get_accent_button_style())
            button_layout.addWidget(load_btn)
            
            locate_btn = QPushButton("🔍 Locate Missing")
            locate_btn.setStyleSheet(self._get_button_style())
            button_layout.addWidget(locate_btn)
            
            button_layout.addStretch()
            layout.addWidget(button_frame)
            
            # Load initial data
            self._refresh_recent_list()
        except Exception as e:
            print(f"Error building recent tab: {e}")
            import traceback
            traceback.print_exc()

    def _get_button_style(self):
        """Get standard button style."""
        return """
            QPushButton {
                background-color: #4d4d5d;
                color: #ffffff;
                border: 2px solid #6a6a8a;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a7a;
                border-color: #7b5eff;
            }
            QPushButton:pressed {
                background-color: #7b5eff;
            }
        """

    def _get_accent_button_style(self):
        """Get accent button style."""
        return """
            QPushButton {
                background-color: #7b5eff;
                color: #ffffff;
                border: 2px solid #7b5eff;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9a7cff;
                border-color: #9a7cff;
            }
            QPushButton:pressed {
                background-color: #6a4ce0;
            }
        """

    def _auto_detect_game(self):
        """Auto-detect game folder or load from settings."""
        # First try to load from saved settings
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
                    return  # Successfully loaded from settings
            except Exception as e:
                print(f"Failed to load from settings: {e}")
        
        # If settings failed, try auto-detection
        result = GameDataLocator.find_public_folder()
        if result:
            path, is_zip = result
            self._set_asset_source(path, is_zip=is_zip)
            self.settings.game_data_path = str(path)
            self.settings.game_data_is_zip = is_zip
            self.settings.save()
            
            source_type = "ZIP archive" if is_zip else "folder"
            self.lbl_game_status.setText(f"🎮 0 A.D. detected ({source_type})")
            self.lbl_game_status.setStyleSheet("color: #4ade80; font-size: 12px;")
        else:
            self.lbl_game_status.setText("⚠️ 0 A.D. not found — Set game data folder")
            self.lbl_game_status.setStyleSheet("color: #fbbf24; font-size: 12px;")

    def _set_asset_source(self, path: Path, is_zip: bool):
        try:
            self.asset_source = LocalAssetSource(path, is_zip=is_zip)
            if is_zip:
                self.lbl_game_status.setText(f"🎮 0 A.D. loaded: {path.name} (ZIP)")
            else:
                try:
                    install_dir = path.parent.parent.parent.parent
                except Exception:
                    install_dir = path
                self.lbl_game_status.setText(f"🎮 0 A.D. loaded: {install_dir.name}")
            
            self.lbl_game_status.setStyleSheet("color: #4ade80; font-size: 12px;")
            
            # Save to settings for auto-loading next time
            self.settings.game_data_path = str(path)
            self.settings.game_data_is_zip = is_zip
            self.settings.save()
            
            # Populate asset tree
            self._populate_asset_tree("")
            
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", f"Failed to load game data: {e}")

    def _populate_asset_tree(self, rel_path: str = "", parent_item: QTreeWidgetItem = None):
        """Populate the asset tree with files and folders."""
        if not self.asset_source:
            return
        
        try:
            entries = self.asset_source.list_dir(rel_path)
            filter_text = self.search_input.text().strip().lower()
            
            for entry in entries:
                name_lower = entry["name"].lower()
                
                # Apply filter
                if filter_text and filter_text not in name_lower:
                    continue
                
                if entry["type"] == "dir":
                    item = QTreeWidgetItem(parent_item) if parent_item else QTreeWidgetItem(self.asset_tree)
                    item.setText(0, f"📁 {entry['name']}")
                    item.setText(1, "dir")
                    item.setText(2, "")
                    
                    # Store the relative path for later expansion
                    item.setData(0, Qt.ItemDataRole.UserRole, entry["rel_path"])
                    
                    # Add a placeholder child to show expand arrow
                    placeholder = QTreeWidgetItem(item)
                    placeholder.setText(0, "Loading...")
                    placeholder.setDisabled(True)
                    
                    if not parent_item:
                        self.asset_tree.addTopLevelItem(item)
                else:
                    item = QTreeWidgetItem(parent_item) if parent_item else QTreeWidgetItem(self.asset_tree)
                    size_str = self._fmt_size(entry["size"])
                    ext = entry["name"].rsplit(".", 1)[-1].lower() if "." in entry["name"] else ""
                    icon = "📄"
                    if ext in ("xml", "json"): icon = "📋"
                    elif ext in ("png", "dds", "tga", "jpg"): icon = "🖼️"
                    elif ext in ("dae", "pmd", "psa"): icon = "📦"
                    elif ext in ("ogg", "mp3", "wav"): icon = "🎵"
                    
                    item.setText(0, f"{icon} {entry['name']}")
                    item.setText(1, ext)
                    item.setText(2, size_str)
                    
                    if not parent_item:
                        self.asset_tree.addTopLevelItem(item)
        except Exception as e:
            print(f"Error populating tree: {e}")

    def _on_tree_expand(self, item: QTreeWidgetItem):
        """Handle tree item expansion."""
        # Remove placeholder if exists
        for i in range(item.childCount()):
            child = item.child(i)
            if child.isDisabled() and child.text(0) == "Loading...":
                item.removeChild(child)
                break
        
        # Get the relative path from the item data
        rel_path = item.data(0, Qt.ItemDataRole.UserRole)
        if rel_path:
            self._populate_asset_tree(rel_path, item)

    def _reload_asset_tree(self):
        """Reload the asset tree."""
        self.asset_tree.clear()
        self._populate_asset_tree("")

    def _on_search_changed(self, text: str):
        """Handle search text changes."""
        self._reload_asset_tree()

    def _navigate_to_folder(self, folder_path: str):
        """Navigate to a specific folder in the asset tree."""
        if not self.asset_source:
            QMessageBox.warning(self, "No Game Data", "Please set the game data folder first.")
            return
        
        try:
            # Expand the tree to show the folder
            self.asset_tree.clear()
            self._populate_asset_tree(folder_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to navigate to folder: {e}")

    def _browse_game_folder(self):
        """Browse the game folder structure."""
        if not self.asset_source:
            QMessageBox.warning(self, "No Game Data", "Please set the game data folder first.")
            return
        
        # Create a dialog to browse the folder structure
        dialog = QDialog(self)
        dialog.setWindowTitle("Browse Game Folder")
        dialog.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Current path display
        self.browse_path_label = QLabel("simulation/templates")
        self.browse_path_label.setStyleSheet("color: #7b5eff; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.browse_path_label)
        
        # Folder tree
        self.browse_tree = QTreeWidget()
        self.browse_tree.setHeaderLabels(["Name", "Type", "Size"])
        self.browse_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1a1a2a;
                color: #ffffff;
                border: 2px solid #6a6a8a;
                border-radius: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #7b5eff;
                color: #ffffff;
            }
            QTreeWidget::header {
                background-color: #383848;
                color: #ffffff;
                border-bottom: 2px solid #6a6a8a;
                padding: 5px;
                font-weight: bold;
            }
        """)
        self.browse_tree.itemExpanded.connect(self._on_browse_expand)
        self.browse_tree.itemDoubleClicked.connect(self._on_browse_double_click)
        layout.addWidget(self.browse_tree)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        up_btn = QPushButton("⬆️ Up")
        up_btn.setStyleSheet(self._get_button_style())
        up_btn.clicked.connect(lambda: self._browse_up())
        nav_layout.addWidget(up_btn)
        
        home_btn = QPushButton("🏠 Root")
        home_btn.setStyleSheet(self._get_button_style())
        home_btn.clicked.connect(lambda: self._browse_to_root())
        nav_layout.addWidget(home_btn)
        
        nav_layout.addStretch()
        layout.addLayout(nav_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 Import Selected")
        import_btn.setStyleSheet(self._get_accent_button_style())
        import_btn.clicked.connect(lambda: self._import_browse_item(dialog))
        button_layout.addWidget(import_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(self._get_button_style())
        close_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Store current browse path
        self.current_browse_path = ""
        
        # Load root
        self._browse_to_root()
        
        dialog.exec()

    def _browse_to_root(self):
        """Navigate to root of game data."""
        self.current_browse_path = ""
        self.browse_path_label.setText("/")
        self.browse_tree.clear()
        self._populate_browse_tree("")

    def _browse_up(self):
        """Navigate up one directory level."""
        if self.current_browse_path:
            parent = str(Path(self.current_browse_path).parent)
            self.current_browse_path = parent if parent != "." else ""
            self.browse_path_label.setText(self.current_browse_path or "/")
            self.browse_tree.clear()
            self._populate_browse_tree(self.current_browse_path)

    def _populate_browse_tree(self, rel_path: str):
        """Populate the browse tree with files and folders."""
        if not self.asset_source:
            return
        
        try:
            entries = self.asset_source.list_dir(rel_path)
            
            for entry in entries:
                if entry["type"] == "dir":
                    item = QTreeWidgetItem(self.browse_tree)
                    item.setText(0, f"📁 {entry['name']}")
                    item.setText(1, "dir")
                    item.setText(2, "")
                    item.setData(0, Qt.ItemDataRole.UserRole, entry.get("rel_path", ""))
                    
                    # Add placeholder
                    placeholder = QTreeWidgetItem(item)
                    placeholder.setText(0, "Loading...")
                    placeholder.setDisabled(True)
                else:
                    item = QTreeWidgetItem(self.browse_tree)
                    size_str = self._fmt_size(entry["size"])
                    ext = entry["name"].rsplit(".", 1)[-1].lower() if "." in entry["name"] else ""
                    icon = "📄"
                    if ext in ("xml", "json"): icon = "📋"
                    elif ext in ("png", "dds", "tga", "jpg"): icon = "🖼️"
                    elif ext in ("dae", "pmd", "psa"): icon = "📦"
                    elif ext in ("ogg", "mp3", "wav"): icon = "🎵"
                    
                    item.setText(0, f"{icon} {entry['name']}")
                    item.setText(1, ext)
                    item.setText(2, size_str)
                    item.setData(0, Qt.ItemDataRole.UserRole, entry.get("rel_path", ""))
        except Exception as e:
            print(f"Error populating browse tree: {e}")

    def _on_browse_expand(self, item: QTreeWidgetItem):
        """Handle browse tree expansion."""
        # Remove placeholder
        for i in range(item.childCount()):
            child = item.child(i)
            if child.isDisabled() and child.text(0) == "Loading...":
                item.removeChild(child)
                break
        
        rel_path = item.data(0, Qt.ItemDataRole.UserRole)
        if rel_path:
            self._populate_browse_tree(rel_path, parent_item=item)

    def _on_browse_double_click(self, item: QTreeWidgetItem, column: int):
        """Handle double-click to navigate into folder."""
        if item.text(1) == "dir":
            rel_path = item.data(0, Qt.ItemDataRole.UserRole)
            if rel_path:
                self.current_browse_path = rel_path
                self.browse_path_label.setText(rel_path)
                self.browse_tree.clear()
                self._populate_browse_tree(rel_path)

    def _import_browse_item(self, dialog: QDialog):
        """Import the selected item to the mod."""
        selected = self.browse_tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select an item first.")
            return
        
        if not self.project or not self.project.is_loaded:
            QMessageBox.warning(self, "No Mod", "Please create or open a mod first.")
            return
        
        item = selected[0]
        rel_path = item.data(0, Qt.ItemDataRole.UserRole)
        
        if item.text(1) == "dir":
            QMessageBox.information(self, "Info", "Folder import not yet implemented. Please select a file.")
            return
        
        try:
            if self.asset_source:
                # Read the file content
                content = self.asset_source.read_text(rel_path)
                if content is None:
                    # Try binary
                    content = self.asset_source.read_binary(rel_path)
                    if content:
                        # Write binary file
                        dest_path = self.project.mod_dir / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        dest_path.write_bytes(content)
                        QMessageBox.information(self, "Success", f"File imported successfully to {dest_path}")
                        dialog.accept()
                    else:
                        QMessageBox.warning(self, "Error", "Could not read file content.")
                else:
                    # Write text file
                    dest_path = self.project.mod_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    dest_path.write_text(content, encoding="utf-8")
                    QMessageBox.information(self, "Success", f"File imported successfully to {dest_path}")
                    dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import file: {e}")

    def _fmt_size(self, size: int) -> str:
        """Format file size for display."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def _refresh_recent_list(self):
        """Refresh the recent projects list."""
        self.recent_tree.clear()
        
        for entry in self.settings.recent_projects:
            path = entry.get("path", "")
            exists = Path(path).is_dir() and (Path(path) / "mod.json").exists()
            
            timestamp = entry.get("timestamp", 0)
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp)) if timestamp > 0 else "Unknown"
            
            item = QTreeWidgetItem(self.recent_tree)
            item.setText(0, entry.get("label", "Unknown"))
            item.setText(1, path)
            item.setText(2, date_str)
            
            if not exists:
                item.setForeground(0, QColor("#707080"))
                item.setForeground(1, QColor("#707080"))

    def _clear_recent_projects(self):
        """Clear all recent projects."""
        reply = QMessageBox.question(
            self, "Clear Recent", 
            "Remove all entries from recent projects list?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.data["recent_projects"] = []
            self.settings.save()
            self._refresh_recent_list()

    def _update_status_bar(self):
        """Update the status bar with current mod information."""
        try:
            if self.project and self.project.is_loaded:
                status_text = f"✅ {self.project.info.label} v{self.project.info.version}"
                self.lbl_mod_status.setText(status_text)
                self.lbl_mod_status.setStyleSheet("color: #4ade80; font-size: 12px; font-weight: bold;")
                
                # Refresh other tabs if they exist
                if hasattr(self, 'unit_tree') and self.unit_tree:
                    self._load_unit_list()
            else:
                self.lbl_mod_status.setText("⚪ No mod loaded")
                self.lbl_mod_status.setStyleSheet("color: #c0c0d0; font-size: 12px;")
        except Exception as e:
            print(f"Error updating status bar: {e}")
            import traceback
            traceback.print_exc()

    def closeEvent(self, event):
        """Handle window close event."""
        width = self.width()
        height = self.height()
        
        if width >= WindowDefaults.MIN_WIDTH and height >= WindowDefaults.MIN_HEIGHT:
            self.settings.set("window_width", width)
            self.settings.set("window_height", height)
        
        self.settings.save()
        
        if hasattr(self, 'asset_source') and self.asset_source:
            try:
                self.asset_source.__del__()
            except:
                pass
        
        event.accept()

    # Action methods
    def action_new_mod(self):
        """Create a new mod project."""
        from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        
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
                mods_dir = GameDataLocator.get_user_mods_dir()
                mods_dir.mkdir(parents=True, exist_ok=True)
                mod_path = mods_dir / name
                
                # Check if mod directory already exists
                if mod_path.exists():
                    reply = QMessageBox.question(
                        self, "Mod Exists",
                        f"A mod with the name '{name}' already exists.\n\nDo you want to overwrite it?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.No:
                        return
                    
                    # Delete existing mod directory
                    import shutil
                    try:
                        shutil.rmtree(mod_path)
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to remove existing mod: {e}")
                        return
                
                self.project = ModProject(mod_path)
                self.project.create(
                    name=name, label=label, description=desc, version=version,
                    dependencies=["0ad=0.28.0"]
                )
                self.settings.last_mod_dir = str(self.project.mod_dir)
                self.settings.save()
                self._update_status_bar()
                QMessageBox.information(self, "Success", f"Mod '{label}' created successfully!")
                
                # Refresh all tabs to reflect the new mod
                self._refresh_all_tabs()
                
                self.tab_widget.setCurrentIndex(4)  # Switch to Overview tab (index 4)
            except ValueError as e:
                QMessageBox.warning(self, "Validation Error", str(e))
            except FileExistsError as e:
                QMessageBox.critical(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create mod: {e}")

    def action_open_mod(self):
        """Open an existing mod project."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Mod Directory", 
            self.settings.last_mod_dir or str(GameDataLocator.get_user_mods_dir())
        )
        
        if folder:
            try:
                self.project = ModProject.load(Path(folder))
                self.settings.last_mod_dir = str(self.project.mod_dir)
                self.settings.add_recent(str(self.project.mod_dir), self.project.info.label)
                self.settings.save()
                self._update_status_bar()
                QMessageBox.information(self, "Success", f"Mod '{self.project.info.label}' loaded successfully!")
            except FileNotFoundError as e:
                QMessageBox.critical(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load mod: {e}")

    def action_show_recent(self):
        """Show and switch to recent projects tab."""
        self.tab_widget.setCurrentIndex(5)  # Switch to Recent tab
        self._refresh_recent_list()

    def action_set_game_folder(self):
        """Set the game data folder manually."""
        # Allow both files and folders
        path, _ = QFileDialog.getOpenFileName(
            self, "Select 0 A.D. Data File (public.zip or folder)",
            self.settings.game_data_path or str(Path.home()),
            "ZIP Files (*.zip);;All Files (*)"
        )
        
        if not path:
            # If no file selected, try folder selection
            folder = QFileDialog.getExistingDirectory(
                self, "Select 0 A.D. Data Folder",
                self.settings.game_data_path or str(Path.home())
            )
            if folder:
                path = folder
        
        if path:
            path_obj = Path(path)
            
            # Check if it's a ZIP file
            if path_obj.is_file() and path_obj.suffix == '.zip':
                self._set_asset_source(path_obj, is_zip=True)
            # Check if it contains public.zip
            elif path_obj.is_dir():
                public_zip = path_obj / "public.zip"
                public_folder = path_obj / "binaries" / "data" / "mods" / "public"
                
                if public_zip.exists():
                    self._set_asset_source(public_zip, is_zip=True)
                elif public_folder.exists():
                    self._set_asset_source(public_folder, is_zip=False)
                else:
                    # Try to use the selected folder directly as the public folder
                    self._set_asset_source(path_obj, is_zip=False)
            else:
                QMessageBox.warning(self, "Invalid Selection", "Please select a valid 0 A.D. data folder or public.zip file")

    def action_build(self):
        """Build the current mod as a .pyromod file."""
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

    def action_about(self):
        QMessageBox.about(self, "About", "0 A.D. Mod Maker\n\nBuilt with PyQt6 for professional UI")


def run():
    """Entry point for the GUI application."""
    try:
        app = QApplication(sys.argv)
        
        # Show startup dialog for recent projects
        startup = StartupDialog()
        if startup.exec() == QDialog.DialogCode.Accepted:
            # User selected a project, load it
            selected_path = startup.selected_path
            if selected_path:
                # Create main window and load the selected project
                window = ModMakerGUI()
                window.show()
                # Load the selected project
                try:
                    window.project = ModProject.load(Path(selected_path))
                    window.settings.last_mod_dir = str(window.project.mod_dir)
                    window.settings.add_recent(str(window.project.mod_dir), window.project.info.label)
                    window.settings.save()
                    window._update_status_bar()
                except Exception as e:
                    QMessageBox.critical(None, "Error", f"Failed to load project: {e}")
                    # Show main window anyway
                    window.show()
            else:
                # User chose to create new mod, show main window
                window = ModMakerGUI()
                window.show()
                # Trigger new mod dialog
                window.action_new_mod()
        else:
            # User cancelled or chose to just open main window
            window = ModMakerGUI()
            window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()


class StartupDialog(QDialog):
    """Startup dialog for recent projects."""
    
    def __init__(self):
        super().__init__()
        self.selected_path = None
        self._setup_dialog()
    
    def _setup_dialog(self):
        self.setWindowTitle("0 A.D. Mod Maker - Welcome")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("🎮 0 A.D. Mod Maker")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #7b5eff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Select a recent project or create a new mod")
        subtitle.setStyleSheet("color: #c0c0d0; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Recent projects list
        recent_label = QLabel("🕒 Recent Projects")
        recent_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(recent_label)
        
        self.recent_tree = QTreeWidget()
        self.recent_tree.setHeaderLabels(["📁 Mod Name", "📍 Location", "📅 Last Opened"])
        self.recent_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1a1a2a;
                color: #ffffff;
                border: 2px solid #6a6a8a;
                border-radius: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #7b5eff;
                color: #ffffff;
            }
            QTreeWidget::header {
                background-color: #383848;
                color: #ffffff;
                border-bottom: 2px solid #6a6a8a;
                padding: 5px;
                font-weight: bold;
            }
        """)
        self.recent_tree.itemDoubleClicked.connect(self._on_recent_double_click)
        layout.addWidget(self.recent_tree)
        
        # Load recent projects
        self._load_recent_projects()
        
        layout.addSpacing(20)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        new_mod_btn = QPushButton("✨ Create New Mod")
        new_mod_btn.setStyleSheet("""
            QPushButton {
                background-color: #7b5eff;
                color: #ffffff;
                border: 2px solid #7b5eff;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #9a7cff;
                border-color: #9a7cff;
            }
        """)
        new_mod_btn.clicked.connect(self.accept)
        button_layout.addWidget(new_mod_btn)
        
        open_btn = QPushButton("📂 Open Other Mod")
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #4d4d5d;
                color: #ffffff;
                border: 2px solid #6a6a8a;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a5a7a;
                border-color: #7b5eff;
            }
        """)
        open_btn.clicked.connect(self._open_other_mod)
        button_layout.addWidget(open_btn)
        
        skip_btn = QPushButton("⏭️ Skip to Main Window")
        skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a4a;
                color: #c0c0d0;
                border: 2px solid #6a6a8a;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a4a5a;
                border-color: #7b5eff;
            }
        """)
        skip_btn.clicked.connect(self.reject)
        button_layout.addWidget(skip_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def _load_recent_projects(self):
        """Load recent projects from settings."""
        try:
            settings = AppSettings()
            for entry in settings.recent_projects:
                path = entry.get("path", "")
                exists = Path(path).is_dir() and (Path(path) / "mod.json").exists()
                
                timestamp = entry.get("timestamp", 0)
                date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp)) if timestamp > 0 else "Unknown"
                
                item = QTreeWidgetItem(self.recent_tree)
                item.setText(0, entry.get("label", "Unknown"))
                item.setText(1, path)
                item.setText(2, date_str)
                item.setData(0, Qt.ItemDataRole.UserRole, path)
                
                if not exists:
                    item.setForeground(0, QColor("#707080"))
                    item.setForeground(1, QColor("#707080"))
                
                self.recent_tree.addTopLevelItem(item)
        except Exception as e:
            print(f"Error loading recent projects: {e}")
    
    def _on_recent_double_click(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on recent project."""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path and Path(path).exists():
            self.selected_path = path
            self.accept()
    
    def _open_other_mod(self):
        """Open a different mod not in recent list."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Mod Directory",
            str(Path.home())
        )
        
        if folder:
            if (Path(folder) / "mod.json").exists():
                self.selected_path = folder
                self.accept()
            else:
                QMessageBox.warning(self, "Invalid Mod", "Selected directory is not a valid mod (no mod.json found).")


if __name__ == "__main__":
    run()