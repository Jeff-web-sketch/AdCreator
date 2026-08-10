#!/usr/bin/env python3
"""
0 A.D. Unit Maker - PyQt6
===========================
A focused GUI for creating and editing 0 A.D. unit templates.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QFrame, QTabWidget,
    QScrollArea, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
    QFileDialog, QMessageBox, QSplitter, QTreeWidget, QTreeWidgetItem,
    QDialog, QDialogButtonBox, QFormLayout, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPalette


class UnitMaker(QMainWindow):
    """Main application window for unit creation."""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.setup_ui()
        self.setup_styling()
    
    def setup_ui(self):
        """Build the user interface."""
        self.setWindowTitle("0 A.D. Unit Maker")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
        sidebar = self.create_sidebar()
        layout.addWidget(sidebar)
        
        # Main content area
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #1a1a2a;")
        layout.addWidget(self.content_area, 1)
        
        # Create pages
        self.create_overview_page()
        self.create_unit_editor_page()
        self.create_settings_page()
        
        # Show overview by default
        self.content_area.setCurrentIndex(0)
    
    def setup_styling(self):
        """Apply dark theme styling."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1a1a2a"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#2d2d3d"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#383848"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#2d2d3d"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#7b5eff"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)
    
    def create_sidebar(self) -> QFrame:
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
        layout.setSpacing(12)
        
        # Title
        title = QLabel("🎮 Unit Maker")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Navigation buttons
        nav_items = [
            ("📊 Overview", 0),
            ("⚔️ Unit Editor", 1),
            ("⚙️ Settings", 2)
        ]
        
        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #c0c0d0;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 15px;
                    font-size: 13px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #383848;
                    color: #ffffff;
                }
                QPushButton:checked {
                    background-color: #7b5eff;
                    color: white;
                    font-weight: bold;
                }
            """)
            btn.setCheckable(True)
            btn.setChecked(index == 0)
            btn.clicked.connect(lambda checked, idx=index: self.navigate_to(idx))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # File info
        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("color: #9090a0; font-size: 11px;")
        self.file_label.setWordWrap(True)
        layout.addWidget(self.file_label)
        
        return sidebar
    
    def navigate_to(self, index: int):
        """Navigate to a specific page."""
        self.content_area.setCurrentIndex(index)
        
        # Update button states
        for i in range(3):
            for child in self.findChildren(QPushButton):
                if child.isChecked() and i != index:
                    child.setChecked(False)
                elif not child.isChecked() and i == index:
                    child.setChecked(True)
    
    def create_overview_page(self):
        """Create the overview page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header
        header = QLabel("📊 Overview")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        # Welcome card
        welcome = QFrame()
        welcome.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d2d3d, stop:1 #383848);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        welcome_layout = QVBoxLayout(welcome)
        
        welcome_title = QLabel("👋 Welcome to 0 A.D. Unit Maker")
        welcome_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #7b5eff;")
        welcome_layout.addWidget(welcome_title)
        
        welcome_desc = QLabel("Create and edit 0 A.D. unit templates with ease.")
        welcome_desc.setStyleSheet("color: #c0c0d0; font-size: 14px;")
        welcome_layout.addWidget(welcome_desc)
        
        layout.addWidget(welcome)
        
        # Quick actions
        actions = QFrame()
        actions.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        actions_layout = QVBoxLayout(actions)
        
        actions_title = QLabel("⚡ Quick Actions")
        actions_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        actions_layout.addWidget(actions_title)
        
        # Action buttons
        button_grid = QHBoxLayout()
        button_grid.setSpacing(15)
        
        new_btn = QPushButton("✨ New Unit")
        new_btn.setStyleSheet(self.get_button_style(accent=True))
        new_btn.clicked.connect(self.new_unit)
        new_btn.setMinimumHeight(50)
        button_grid.addWidget(new_btn)
        
        open_btn = QPushButton("📂 Open Unit")
        open_btn.setStyleSheet(self.get_button_style())
        open_btn.clicked.connect(self.open_unit)
        open_btn.setMinimumHeight(50)
        button_grid.addWidget(open_btn)
        
        save_btn = QPushButton("💾 Save Unit")
        save_btn.setStyleSheet(self.get_button_style())
        save_btn.clicked.connect(self.save_unit)
        save_btn.setMinimumHeight(50)
        button_grid.addWidget(save_btn)
        
        button_grid.addStretch()
        actions_layout.addLayout(button_grid)
        layout.addWidget(actions)
        
        # Recent files
        recent = QFrame()
        recent.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        recent_layout = QVBoxLayout(recent)
        
        recent_title = QLabel("🕒 Recent Files")
        recent_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        recent_layout.addWidget(recent_title)
        
        self.recent_list = QTreeWidget()
        self.recent_list.setHeaderLabels(["📁 File Name", "📍 Path"])
        self.recent_list.setStyleSheet(self.get_tree_style())
        self.recent_list.itemDoubleClicked.connect(self.open_recent)
        recent_layout.addWidget(self.recent_list)
        
        layout.addWidget(recent)
        layout.addStretch()
        
        self.content_area.addWidget(page)
    
    def create_unit_editor_page(self):
        """Create the unit editor page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("⚔️ Unit Editor")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        new_btn = QPushButton("✨ New")
        new_btn.setStyleSheet(self.get_button_style())
        new_btn.clicked.connect(self.new_unit)
        toolbar.addWidget(new_btn)
        
        open_btn = QPushButton("📂 Open")
        open_btn.setStyleSheet(self.get_button_style())
        open_btn.clicked.connect(self.open_unit)
        toolbar.addWidget(open_btn)
        
        save_btn = QPushButton("💾 Save")
        save_btn.setStyleSheet(self.get_button_style(accent=True))
        save_btn.clicked.connect(self.save_unit)
        toolbar.addWidget(save_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Splitter for unit list and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Unit list
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        list_layout = QVBoxLayout(list_frame)
        
        list_title = QLabel("📋 Unit List")
        list_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        list_layout.addWidget(list_title)
        
        self.unit_list = QTreeWidget()
        self.unit_list.setHeaderLabels(["📁 Name"])
        self.unit_list.setStyleSheet(self.get_tree_style())
        self.unit_list.itemClicked.connect(self.load_unit_to_editor)
        list_layout.addWidget(self.unit_list)
        
        splitter.addWidget(list_frame)
        
        # Editor area
        editor_frame = QFrame()
        editor_frame.setStyleSheet("""
            QFrame {
                background-color: #383848;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        editor_layout = QVBoxLayout(editor_frame)
        
        # Tab widget for editor sections
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: #2d2d3d;
                border: 2px solid #4a4a6a;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #383848;
                color: #c0c0d0;
                padding: 10px 20px;
                border: 2px solid #4a4a6a;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                margin-right: 4px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #7b5eff;
                color: white;
                border-color: #7b5eff;
            }
        """)
        
        self.create_editor_tabs()
        editor_layout.addWidget(self.editor_tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("✅ Apply Changes")
        apply_btn.setStyleSheet(self.get_button_style(accent=True))
        apply_btn.clicked.connect(self.apply_changes)
        button_layout.addWidget(apply_btn)
        
        reset_btn = QPushButton("🔄 Reset")
        reset_btn.setStyleSheet(self.get_button_style())
        reset_btn.clicked.connect(self.reset_editor)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        editor_layout.addLayout(button_layout)
        
        splitter.addWidget(editor_frame)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        layout.addWidget(splitter)
        
        self.content_area.addWidget(page)
    
    def create_editor_tabs(self):
        """Create the editor tab pages."""
        # Identity tab
        identity_tab = self.create_identity_tab()
        self.editor_tabs.addTab(identity_tab, "🏷️ Identity")
        
        # Stats tab
        stats_tab = self.create_stats_tab()
        self.editor_tabs.addTab(stats_tab, "📊 Stats")
        
        # Combat tab
        combat_tab = self.create_combat_tab()
        self.editor_tabs.addTab(combat_tab, "⚔️ Combat")
        
        # Movement tab
        movement_tab = self.create_movement_tab()
        self.editor_tabs.addTab(movement_tab, "🏃 Movement")
        
        # Vision tab
        vision_tab = self.create_vision_tab()
        self.editor_tabs.addTab(vision_tab, "👁️ Vision")
        
        # Resources tab
        resources_tab = self.create_resources_tab()
        self.editor_tabs.addTab(resources_tab, "💰 Resources")
        
        # Visual tab
        visual_tab = self.create_visual_tab()
        self.editor_tabs.addTab(visual_tab, "🎭 Visual")
    
    def create_identity_tab(self) -> QWidget:
        """Create identity properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Form
        form = QFrame()
        form.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form)
        
        # Form fields
        self.civ_input = self.create_form_field("Civilization:", "generic")
        form_layout.addLayout(self.civ_input['layout'])
        
        self.generic_input = self.create_form_field("Generic Name:", "Unit")
        form_layout.addLayout(self.generic_input['layout'])
        
        self.specific_input = self.create_form_field("Specific Name:", "Unit Name")
        form_layout.addLayout(self.specific_input['layout'])
        
        self.rank_input = self.create_combo_field("Rank:", ["Basic", "Advanced", "Elite"], "Basic")
        form_layout.addLayout(self.rank_input['layout'])
        
        self.classes_input = self.create_form_field("Classes:", "")
        form_layout.addLayout(self.classes_input['layout'])
        
        layout.addWidget(form)
        layout.addStretch()
        
        return tab
    
    def create_stats_tab(self) -> QWidget:
        """Create stats properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        form = QFrame()
        form.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form)
        
        self.health_input = self.create_number_field("Max Health:", 100)
        form_layout.addLayout(self.health_input['layout'])
        
        self.regen_rate_input = self.create_number_field("Regen Rate:", 0)
        form_layout.addLayout(self.regen_rate_input['layout'])
        
        self.regen_delay_input = self.create_number_field("Regen Delay:", 0)
        form_layout.addLayout(self.regen_delay_input['layout'])
        
        layout.addWidget(form)
        layout.addStretch()
        
        return tab
    
    def create_combat_tab(self) -> QWidget:
        """Create combat properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        form = QFrame()
        form.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form)
        
        # Melee
        melee_title = QLabel("🗡️ Melee Attack")
        melee_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #5eff7b;")
        form_layout.addWidget(melee_title)
        
        self.melee_hack_input = self.create_number_field("Hack Damage:", 0)
        form_layout.addLayout(self.melee_hack_input['layout'])
        
        self.melee_pierce_input = self.create_number_field("Pierce Damage:", 0)
        form_layout.addLayout(self.melee_pierce_input['layout'])
        
        self.melee_crush_input = self.create_number_field("Crush Damage:", 0)
        form_layout.addLayout(self.melee_crush_input['layout'])
        
        self.melee_range_input = self.create_number_field("Melee Range:", 3.0)
        form_layout.addLayout(self.melee_range_input['layout'])
        
        # Ranged
        form_layout.addSpacing(10)
        ranged_title = QLabel("🏹 Ranged Attack")
        ranged_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #5eff7b;")
        form_layout.addWidget(ranged_title)
        
        self.ranged_hack_input = self.create_number_field("Hack Damage:", 0)
        form_layout.addLayout(self.ranged_hack_input['layout'])
        
        self.ranged_pierce_input = self.create_number_field("Pierce Damage:", 0)
        form_layout.addLayout(self.ranged_pierce_input['layout'])
        
        self.ranged_crush_input = self.create_number_field("Crush Damage:", 0)
        form_layout.addLayout(self.ranged_crush_input['layout'])
        
        self.ranged_range_input = self.create_number_field("Ranged Range:", 0)
        form_layout.addLayout(self.ranged_range_input['layout'])
        
        self.ranged_prepare_time_input = self.create_number_field("Prepare Time:", 1.0)
        form_layout.addLayout(self.ranged_prepare_time_input['layout'])
        
        layout.addWidget(form)
        layout.addStretch()
        
        return tab
    
    def create_movement_tab(self) -> QWidget:
        """Create movement properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        form = QFrame()
        form.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form)
        
        self.walk_speed_input = self.create_number_field("Walk Speed:", 1.0)
        form_layout.addLayout(self.walk_speed_input['layout'])
        
        self.run_speed_input = self.create_number_field("Run Speed:", 0)
        form_layout.addLayout(self.run_speed_input['layout'])
        
        self.acceleration_input = self.create_number_field("Acceleration:", 2.0)
        form_layout.addLayout(self.acceleration_input['layout'])
        
        self.passability_input = self.create_combo_field("Passability:", ["default", "ship", "large"], "default")
        form_layout.addLayout(self.passability_input['layout'])
        
        layout.addWidget(form)
        layout.addStretch()
        
        return tab
    
    def create_vision_tab(self) -> QWidget:
        """Create vision properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        form = QFrame()
        form.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form)
        
        self.vision_range_input = self.create_number_field("Vision Range:", 32)
        form_layout.addLayout(self.vision_range_input['layout'])
        
        self.retain_fog_checkbox = self.create_checkbox_field("Retain in Fog", False)
        form_layout.addLayout(self.retain_fog_checkbox['layout'])
        
        layout.addWidget(form)
        layout.addStretch()
        
        return tab
    
    def create_resources_tab(self) -> QWidget:
        """Create resource properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Use scroll area for better visibility
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # Cost section
        cost_frame = QFrame()
        cost_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        cost_layout = QVBoxLayout(cost_frame)
        cost_layout.setSpacing(18)
        
        cost_title = QLabel("💰 Cost")
        cost_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #5eff7b;")
        cost_layout.addWidget(cost_title)
        
        self.build_time_input = self.create_number_field("Build Time:", 10)
        cost_layout.addLayout(self.build_time_input['layout'])
        
        self.population_input = self.create_number_field("Population:", 1)
        cost_layout.addLayout(self.population_input['layout'])
        
        self.food_cost_input = self.create_number_field("Food Cost:", 50)
        cost_layout.addLayout(self.food_cost_input['layout'])
        
        self.wood_cost_input = self.create_number_field("Wood Cost:", 0)
        cost_layout.addLayout(self.wood_cost_input['layout'])
        
        self.stone_cost_input = self.create_number_field("Stone Cost:", 0)
        cost_layout.addLayout(self.stone_cost_input['layout'])
        
        self.metal_cost_input = self.create_number_field("Metal Cost:", 0)
        cost_layout.addLayout(self.metal_cost_input['layout'])
        
        scroll_layout.addWidget(cost_frame)
        
        # Loot section
        loot_frame = QFrame()
        loot_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        loot_layout = QVBoxLayout(loot_frame)
        loot_layout.setSpacing(18)
        
        loot_title = QLabel("💎 Loot")
        loot_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #5eff7b;")
        loot_layout.addWidget(loot_title)
        
        self.xp_loot_input = self.create_number_field("XP Loot:", 10)
        loot_layout.addLayout(self.xp_loot_input['layout'])
        
        scroll_layout.addWidget(loot_frame)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return tab
    
    def create_visual_tab(self) -> QWidget:
        """Create visual properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        form = QFrame()
        form.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form)
        
        self.actor_input = self.create_form_field("Actor:", "props/units/hellenes/infantry_spearman.xml")
        form_layout.addLayout(self.actor_input['layout'])
        
        self.foundation_actor_input = self.create_form_field("Foundation Actor:", "")
        form_layout.addLayout(self.foundation_actor_input['layout'])
        
        self.selection_radius_input = self.create_number_field("Selection Radius:", 1.0)
        form_layout.addLayout(self.selection_radius_input['layout'])
        
        layout.addWidget(form)
        layout.addStretch()
        
        return tab
    
    def create_settings_page(self):
        """Create the settings page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        header = QLabel("⚙️ Settings")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        # Settings form
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        settings_layout = QVBoxLayout(settings_frame)
        
        # Default unit folder
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Default Unit Folder:")
        folder_label.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        folder_label.setFixedWidth(150)
        folder_layout.addWidget(folder_label)
        
        self.default_folder_input = QLineEdit()
        self.default_folder_input.setPlaceholderText("e.g., /path/to/0ad/data/mods/public/simulation/templates/units")
        self.default_folder_input.setStyleSheet(self.get_line_edit_style())
        folder_layout.addWidget(self.default_folder_input)
        
        browse_btn = QPushButton("📂 Browse")
        browse_btn.setStyleSheet(self.get_button_style())
        browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(browse_btn)
        
        settings_layout.addLayout(folder_layout)
        
        layout.addWidget(settings_frame)
        layout.addStretch()
        
        self.content_area.addWidget(page)
    
    # Helper methods for form fields
    def create_form_field(self, label: str, default: str) -> dict:
        """Create a text input field."""
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        label_widget.setFixedWidth(140)
        layout.addWidget(label_widget)
        
        input_widget = QLineEdit()
        input_widget.setText(default)
        input_widget.setStyleSheet(self.get_line_edit_style())
        layout.addWidget(input_widget)
        
        layout.addStretch()
        
        return {'layout': layout, 'input': input_widget}
    
    def create_number_field(self, label: str, default: float) -> dict:
        """Create a number input field."""
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        label_widget.setFixedWidth(140)
        layout.addWidget(label_widget)
        
        input_widget = QDoubleSpinBox()
        input_widget.setRange(0, 10000)
        input_widget.setValue(default)
        input_widget.setSingleStep(0.1)
        input_widget.setStyleSheet(self.get_spin_box_style())
        layout.addWidget(input_widget)
        
        layout.addStretch()
        
        return {'layout': layout, 'input': input_widget}
    
    def create_combo_field(self, label: str, options: list, default: str) -> dict:
        """Create a combo box field."""
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        label_widget.setFixedWidth(140)
        layout.addWidget(label_widget)
        
        input_widget = QComboBox()
        input_widget.addItems(options)
        input_widget.setCurrentText(default)
        input_widget.setStyleSheet(self.get_spin_box_style())
        layout.addWidget(input_widget)
        
        layout.addStretch()
        
        return {'layout': layout, 'input': input_widget}
    
    def create_checkbox_field(self, label: str, default: bool) -> dict:
        """Create a checkbox field."""
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        label_widget.setFixedWidth(140)
        layout.addWidget(label_widget)
        
        input_widget = QCheckBox("Enabled")
        input_widget.setChecked(default)
        input_widget.setStyleSheet("color: #c0c0d0; font-size: 13px;")
        layout.addWidget(input_widget)
        
        layout.addStretch()
        
        return {'layout': layout, 'input': input_widget}
    
    # Styling methods
    def get_button_style(self, accent: bool = False) -> str:
        """Get button CSS style."""
        if accent:
            return """
                QPushButton {
                    background-color: #7b5eff;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #8b6fff;
                }
                QPushButton:pressed {
                    background-color: #6b4eff;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #2d2d3d;
                    color: white;
                    border: 2px solid #4a4a6a;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #383848;
                    border-color: #7b5eff;
                }
                QPushButton:pressed {
                    background-color: #484858;
                }
            """
    
    def get_tree_style(self) -> str:
        """Get tree widget CSS style."""
        return """
            QTreeWidget {
                background-color: #1a1a2a;
                color: #ffffff;
                border: 2px solid #4a4a6a;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 6px;
                border-radius: 4px;
            }
            QTreeWidget::item:hover {
                background-color: #383848;
            }
            QTreeWidget::item:selected {
                background-color: #7b5eff;
                color: white;
            }
            QTreeWidget::header {
                background-color: #383848;
                color: #7b5eff;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #4a4a6a;
            }
        """
    
    def get_line_edit_style(self) -> str:
        """Get line edit CSS style."""
        return """
            QLineEdit {
                background-color: #1a1a2a;
                color: #ffffff;
                border: 2px solid #4a4a6a;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #7b5eff;
            }
        """
    
    def get_spin_box_style(self) -> str:
        """Get spin box CSS style."""
        return """
            QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #1a1a2a;
                color: #ffffff;
                border: 2px solid #4a4a6a;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border-color: #7b5eff;
            }
        """
    
    # Action methods
    def new_unit(self):
        """Create a new unit."""
        self.navigate_to(1)
        self.reset_editor()
        self.current_file = None
        self.file_label.setText("New unit (unsaved)")
    
    def open_unit(self):
        """Open an existing unit file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Unit File",
            "",
            "XML Files (*.xml);;All Files (*)"
        )
        
        if file_path:
            self.load_unit_file(file_path)
    
    def open_recent(self, item: QTreeWidgetItem, column: int):
        """Open a recent file."""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path and Path(file_path).exists():
            self.load_unit_file(file_path)
    
    def load_unit_file(self, file_path: str):
        """Load a unit file into the editor."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.current_file = file_path
            self.file_label.setText(Path(file_path).name)
            
            # Parse XML and populate fields
            self.populate_from_xml(content)
            
            # Navigate to editor
            self.navigate_to(1)
            
            QMessageBox.information(self, "Success", f"Loaded: {Path(file_path).name}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {e}")
    
    def populate_from_xml(self, xml_content: str):
        """Populate editor fields from XML content."""
        try:
            root = ET.fromstring(xml_content)
            
            # Identity
            identity = root.find(".//Identity")
            if identity is not None:
                self.civ_input['input'].setText(identity.get("Civ", "generic"))
                self.generic_input['input'].setText(identity.get("Generic", "Unit"))
                self.specific_input['input'].setText(identity.get("Specific", "Unit Name"))
                self.rank_input['input'].setCurrentText(identity.get("Rank", "Basic"))
                self.classes_input['input'].setText(identity.get("Classes", ""))
            
            # Health
            health = root.find(".//Health")
            if health is not None:
                self.health_input['input'].setValue(float(health.get("Max", "100")))
                self.regen_rate_input['input'].setValue(float(health.get("RegenRate", "0")))
                self.regen_delay_input['input'].setValue(float(health.get("RegenDelay", "0")))
            
            # Attack
            attack = root.find(".//Attack")
            if attack is not None:
                melee = attack.find("Melee")
                if melee is not None:
                    self.melee_hack_input['input'].setValue(float(melee.get("Hack", "0")))
                    self.melee_pierce_input['input'].setValue(float(melee.get("Pierce", "0")))
                    self.melee_crush_input['input'].setValue(float(melee.get("Crush", "0")))
                    self.melee_range_input['input'].setValue(float(melee.get("MaxRange", "3.0")))
                
                ranged = attack.find("Ranged")
                if ranged is not None:
                    self.ranged_hack_input['input'].setValue(float(ranged.get("Hack", "0")))
                    self.ranged_pierce_input['input'].setValue(float(ranged.get("Pierce", "0")))
                    self.ranged_crush_input['input'].setValue(float(ranged.get("Crush", "0")))
                    self.ranged_range_input['input'].setValue(float(ranged.get("MaxRange", "0")))
                    self.ranged_prepare_time_input['input'].setValue(float(ranged.get("PrepareTime", "1.0")))
            
            # Movement
            unit_motion = root.find(".//UnitMotion")
            if unit_motion is not None:
                self.walk_speed_input['input'].setValue(float(unit_motion.get("WalkSpeed", "1.0")))
                self.run_speed_input['input'].setValue(float(unit_motion.get("Run", "0")))
                self.acceleration_input['input'].setValue(float(unit_motion.get("Acceleration", "2.0")))
                self.passability_input['input'].setCurrentText(unit_motion.get("PassabilityClass", "default"))
            
            # Vision
            vision = root.find(".//Vision")
            if vision is not None:
                self.vision_range_input['input'].setValue(float(vision.get("Range", "32")))
                self.retain_fog_checkbox['input'].setChecked(vision.get("RetainInFog", "false").lower() == "true")
            
            # Cost
            cost = root.find(".//Cost")
            if cost is not None:
                self.build_time_input['input'].setValue(float(cost.get("BuildTime", "10")))
                self.population_input['input'].setValue(float(cost.get("Population", "1")))
                resources = cost.find("Resources")
                if resources is not None:
                    self.food_cost_input['input'].setValue(float(resources.get("food", "50")))
                    self.wood_cost_input['input'].setValue(float(resources.get("wood", "0")))
                    self.stone_cost_input['input'].setValue(float(resources.get("stone", "0")))
                    self.metal_cost_input['input'].setValue(float(resources.get("metal", "0")))
            
            # Loot
            loot = root.find(".//Loot")
            if loot is not None:
                self.xp_loot_input['input'].setValue(float(loot.get("xp", "10")))
            
            # Visual
            visual_actor = root.find(".//VisualActor")
            if visual_actor is not None:
                self.actor_input['input'].setText(visual_actor.get("Actor", ""))
                self.foundation_actor_input['input'].setText(visual_actor.get("FoundationActor", ""))
            
            # Selection
            selection = root.find(".//Selection")
            if selection is not None:
                self.selection_radius_input['input'].setValue(float(selection.get("Radius", "1.0")))
        
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to parse XML: {e}")
    
    def reset_editor(self):
        """Reset all editor fields to defaults."""
        # Identity
        self.civ_input['input'].setText("generic")
        self.generic_input['input'].setText("Unit")
        self.specific_input['input'].setText("Unit Name")
        self.rank_input['input'].setCurrentText("Basic")
        self.classes_input['input'].setText("")
        
        # Stats
        self.health_input['input'].setValue(100)
        self.regen_rate_input['input'].setValue(0)
        self.regen_delay_input['input'].setValue(0)
        
        # Combat
        self.melee_hack_input['input'].setValue(0)
        self.melee_pierce_input['input'].setValue(0)
        self.melee_crush_input['input'].setValue(0)
        self.melee_range_input['input'].setValue(3.0)
        
        self.ranged_hack_input['input'].setValue(0)
        self.ranged_pierce_input['input'].setValue(0)
        self.ranged_crush_input['input'].setValue(0)
        self.ranged_range_input['input'].setValue(0)
        self.ranged_prepare_time_input['input'].setValue(1.0)
        
        # Movement
        self.walk_speed_input['input'].setValue(1.0)
        self.run_speed_input['input'].setValue(0)
        self.acceleration_input['input'].setValue(2.0)
        self.passability_input['input'].setCurrentText("default")
        
        # Vision
        self.vision_range_input['input'].setValue(32)
        self.retain_fog_checkbox['input'].setChecked(False)
        
        # Resources
        self.build_time_input['input'].setValue(10)
        self.population_input['input'].setValue(1)
        self.food_cost_input['input'].setValue(50)
        self.wood_cost_input['input'].setValue(0)
        self.stone_cost_input['input'].setValue(0)
        self.metal_cost_input['input'].setValue(0)
        self.xp_loot_input['input'].setValue(10)
        
        # Visual
        self.actor_input['input'].setText("props/units/hellenes/infantry_spearman.xml")
        self.foundation_actor_input['input'].setText("")
        self.selection_radius_input['input'].setValue(1.0)
    
    def apply_changes(self):
        """Apply changes and generate XML."""
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "No file loaded. Use Save As instead.")
            return
        
        try:
            xml_content = self.generate_xml()
            
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            QMessageBox.information(self, "Success", "Changes saved successfully!")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")
    
    def save_unit(self):
        """Save the current unit."""
        if self.current_file:
            self.apply_changes()
        else:
            self.save_unit_as()
    
    def save_unit_as(self):
        """Save the unit to a new file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Unit As",
            "",
            "XML Files (*.xml);;All Files (*)"
        )
        
        if file_path:
            try:
                xml_content = self.generate_xml()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content)
                
                self.current_file = file_path
                self.file_label.setText(Path(file_path).name)
                
                QMessageBox.information(self, "Success", f"Saved to: {Path(file_path).name}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {e}")
    
    def generate_xml(self) -> str:
        """Generate XML from current field values."""
        xml_lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            '<Entity>',
            '  <Identity>',
            f'    <Civ>{self.civ_input["input"].text()}</Civ>',
            f'    <Generic>{self.generic_input["input"].text()}</Generic>',
            f'    <Specific>{self.specific_input["input"].text()}</Specific>',
            f'    <Rank>{self.rank_input["input"].currentText()}</Rank>',
            f'    <Classes>{self.classes_input["input"].text()}</Classes>',
            '  </Identity>',
            '  <Cost>',
            f'    <BuildTime>{self.build_time_input["input"].value()}</BuildTime>',
            f'    <Population>{self.population_input["input"].value()}</Population>',
            '    <Resources>',
            f'      <food>{self.food_cost_input["input"].value()}</food>',
            f'      <wood>{self.wood_cost_input["input"].value()}</wood>',
            f'      <stone>{self.stone_cost_input["input"].value()}</stone>',
            f'      <metal>{self.metal_cost_input["input"].value()}</metal>',
            '    </Resources>',
            '  </Cost>',
            '  <Health>',
            f'    <Max>{self.health_input["input"].value()}</Max>',
            f'    <RegenRate>{self.regen_rate_input["input"].value()}</RegenRate>',
            f'    <RegenDelay>{self.regen_delay_input["input"].value()}</RegenDelay>',
            '  </Health>',
            '  <Attack>'
        ]
        
        # Melee attack
        if self.melee_hack_input['input'].value() > 0 or self.melee_pierce_input['input'].value() > 0 or self.melee_crush_input['input'].value() > 0:
            xml_lines.extend([
                '    <Melee>',
                f'      <Hack>{self.melee_hack_input["input"].value()}</Hack>',
                f'      <Pierce>{self.melee_pierce_input["input"].value()}</Pierce>',
                f'      <Crush>{self.melee_crush_input["input"].value()}</Crush>',
                f'      <MaxRange>{self.melee_range_input["input"].value()}</MaxRange>',
                '    </Melee>'
            ])
        
        # Ranged attack
        if self.ranged_range_input['input'].value() > 0:
            xml_lines.extend([
                '    <Ranged>',
                f'      <Hack>{self.ranged_hack_input["input"].value()}</Hack>',
                f'      <Pierce>{self.ranged_pierce_input["input"].value()}</Pierce>',
                f'      <Crush>{self.ranged_crush_input["input"].value()}</Crush>',
                f'      <MaxRange>{self.ranged_range_input["input"].value()}</MaxRange>',
                f'      <PrepareTime>{self.ranged_prepare_time_input["input"].value()}</PrepareTime>',
                '    </Ranged>'
            ])
        
        xml_lines.extend([
            '  </Attack>',
            '  <Resistance>',
            f'    <Hack>5</Hack>',
            f'    <Pierce>5</Pierce>',
            f'    <Crush>5</Crush>',
            '  </Resistance>',
            '  <UnitMotion>',
            f'    <WalkSpeed>{self.walk_speed_input["input"].value()}</WalkSpeed>',
            f'    <Run>{self.run_speed_input["input"].value()}</Run>',
            f'    <Acceleration>{self.acceleration_input["input"].value()}</Acceleration>',
            f'    <PassabilityClass>{self.passability_input["input"].currentText()}</PassabilityClass>',
            '  </UnitMotion>',
            '  <Vision>',
            f'    <Range>{self.vision_range_input["input"].value()}</Range>',
            f'    <RetainInFog>{"true" if self.retain_fog_checkbox["input"].isChecked() else "false"}</RetainInFog>',
            '  </Vision>',
            '  <Loot>',
            f'    <xp>{self.xp_loot_input["input"].value()}</xp>',
            f'    <food>0</food>',
            f'    <wood>0</wood>',
            f'    <stone>0</stone>',
            f'    <metal>0</metal>',
            '  </Loot>',
            '  <VisualActor>',
            f'    <Actor>{self.actor_input["input"].text()}</Actor>',
            f'    <FoundationActor>{self.foundation_actor_input["input"].text()}</FoundationActor>',
            '  </VisualActor>',
            '  <Selection>',
            f'    <Radius>{self.selection_radius_input["input"].value()}</Radius>',
            '  </Selection>',
            '</Entity>'
        ])
        
        return '\n'.join(xml_lines)
    
    def browse_folder(self):
        """Browse for default unit folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Unit Folder")
        if folder:
            self.default_folder_input.setText(folder)
    
    def load_unit_to_editor(self, item: QTreeWidgetItem, column: int):
        """Load selected unit from list."""
        # This would load from a project or folder
        pass


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = UnitMaker()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()