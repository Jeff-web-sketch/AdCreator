"""Tab widgets for the main application."""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QFrame, QTextEdit, QLineEdit,
    QFileDialog, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QSplitter, QScrollArea, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from assets import AssetSource, AssetEntry
from mod import ModProject
from styles import get_button_style, get_tree_style, get_line_edit_style, get_spin_box_style, get_text_edit_style


class BaseTab(QWidget):
    """Base class for all tabs."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._setup_ui()
    
    def _setup_ui(self):
        """Override to set up the tab UI."""
        pass
    
    def refresh(self):
        """Override to refresh tab content."""
        pass


class OverviewTab(BaseTab):
    """Overview tab showing project statistics and quick actions."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("📊 Project Overview")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        # Stats container
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        self.project_name_label = QLabel("No project loaded")
        self.project_name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        stats_layout.addWidget(self.project_name_label)
        
        self.file_count_label = QLabel("Files: 0")
        self.file_count_label.setStyleSheet("color: #c0c0d0; font-size: 14px;")
        stats_layout.addWidget(self.file_count_label)
        
        self.project_size_label = QLabel("Size: 0 KB")
        self.project_size_label.setStyleSheet("color: #c0c0d0; font-size: 14px;")
        stats_layout.addWidget(self.project_size_label)
        
        layout.addWidget(stats_frame)
        
        # Quick actions
        actions_frame = QFrame()
        actions_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        actions_layout = QVBoxLayout(actions_frame)
        
        actions_title = QLabel("⚡ Quick Actions")
        actions_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        actions_layout.addWidget(actions_title)
        
        new_mod_btn = QPushButton("✨ Create New Mod")
        new_mod_btn.setStyleSheet(get_button_style(accent=True))
        new_mod_btn.clicked.connect(self.main_window.action_new_mod)
        actions_layout.addWidget(new_mod_btn)
        
        open_mod_btn = QPushButton("📂 Open Existing Mod")
        open_mod_btn.setStyleSheet(get_button_style())
        open_mod_btn.clicked.connect(self.main_window.action_open_mod)
        actions_layout.addWidget(open_mod_btn)
        
        save_mod_btn = QPushButton("💾 Save Current Mod")
        save_mod_btn.setStyleSheet(get_button_style())
        save_mod_btn.clicked.connect(self.main_window.action_save_mod)
        actions_layout.addWidget(save_mod_btn)
        
        build_mod_btn = QPushButton("🔨 Build .pyromod")
        build_mod_btn.setStyleSheet(get_button_style(accent=True))
        build_mod_btn.clicked.connect(self.main_window.action_build_mod)
        actions_layout.addWidget(build_mod_btn)
        
        layout.addWidget(actions_frame)
        layout.addStretch()
    
    def refresh(self):
        """Refresh overview with current project data."""
        if self.main_window.project:
            project = self.main_window.project
            self.project_name_label.setText(f"📁 {project.project_name}")
            self.file_count_label.setText(f"Files: {len(project.files)}")
            
            # Calculate approximate size
            total_size = sum(len(f.content) for f in project.files.values())
            size_str = f"{total_size / 1024:.1f} KB" if total_size > 1024 else f"{total_size} B"
            self.project_size_label.setText(f"Size: {size_str}")
        else:
            self.project_name_label.setText("No project loaded")
            self.file_count_label.setText("Files: 0")
            self.project_size_label.setText("Size: 0 KB")


class AssetsTab(BaseTab):
    """Assets tab for browsing and managing game assets."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("📁 Asset Browser")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(get_button_style())
        refresh_btn.clicked.connect(self._refresh_tree)
        toolbar.addWidget(refresh_btn)
        
        toolbar.addStretch()
        
        # Navigation buttons
        up_btn = QPushButton("⬆️ Up")
        up_btn.setStyleSheet(get_button_style())
        up_btn.clicked.connect(self._navigate_up)
        toolbar.addWidget(up_btn)
        
        root_btn = QPushButton("🏠 Root")
        root_btn.setStyleSheet(get_button_style())
        root_btn.clicked.connect(self._navigate_to_root)
        toolbar.addWidget(root_btn)
        
        layout.addLayout(toolbar)
        
        # Path display
        self.path_label = QLabel("📍 Root")
        self.path_label.setStyleSheet("color: #c0c0d0; font-size: 13px;")
        layout.addWidget(self.path_label)
        
        # Asset tree
        self.asset_tree = QTreeWidget()
        self.asset_tree.setHeaderLabels(["📁 Name", "📊 Size", "🏷️ Type"])
        self.asset_tree.setStyleSheet(get_tree_style())
        self.asset_tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.asset_tree.setAlternatingRowColors(True)
        layout.addWidget(self.asset_tree)
        
        # Current path tracking
        self.current_path = ""
    
    def refresh(self):
        """Refresh the asset tree."""
        self._refresh_tree()
    
    def _refresh_tree(self):
        """Refresh the asset tree with current path."""
        self.asset_tree.clear()
        
        if not self.main_window.asset_source:
            return
        
        try:
            entries = self.main_window.asset_source.list_dir(self.current_path)
            
            for entry in entries:
                item = QTreeWidgetItem(self.asset_tree)
                item.setText(0, entry.name)
                item.setText(1, f"{entry.size / 1024:.1f} KB" if entry.size > 1024 else f"{entry.size} B")
                item.setText(2, entry.type)
                item.setData(0, Qt.ItemDataRole.UserRole, entry)
                
                if entry.type == "dir":
                    item.setForeground(0, QColor("#7b5eff"))
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load assets: {e}")
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on an item."""
        entry = item.data(0, Qt.ItemDataRole.UserRole)
        
        if entry.type == "dir":
            # Navigate into directory
            self.current_path = entry.rel_path
            self.path_label.setText(f"📍 {self.current_path or 'Root'}")
            self._refresh_tree()
        else:
            # Open file
            self._open_file(entry.rel_path)
    
    def _open_file(self, path: str):
        """Open a file for viewing/editing."""
        if not self.main_window.asset_source:
            return
        
        try:
            content = self.main_window.asset_source.read_text(path)
            if content:
                dialog = QDialog(self)
                dialog.setWindowTitle(f"View: {Path(path).name}")
                dialog.setMinimumSize(600, 400)
                
                layout = QVBoxLayout(dialog)
                
                text_edit = QTextEdit()
                text_edit.setPlainText(content)
                text_edit.setStyleSheet(get_text_edit_style())
                text_edit.setReadOnly(True)
                layout.addWidget(text_edit)
                
                dialog.exec()
            else:
                QMessageBox.information(self, "Info", "File is binary or could not be read as text.")
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open file: {e}")
    
    def _navigate_up(self):
        """Navigate to parent directory."""
        if self.current_path:
            parent = str(Path(self.current_path).parent)
            self.current_path = parent if parent != "." else ""
            self.path_label.setText(f"📍 {self.current_path or 'Root'}")
            self._refresh_tree()
    
    def _navigate_to_root(self):
        """Navigate to root directory."""
        self.current_path = ""
        self.path_label.setText("📍 Root")
        self._refresh_tree()


class UnitsTab(BaseTab):
    """Units tab for viewing and editing unit templates."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("⚔️ Units")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(get_button_style())
        refresh_btn.clicked.connect(self._refresh_units)
        toolbar.addWidget(refresh_btn)
        
        toolbar.addStretch()
        
        # Import button removed as requested
        # import_btn = QPushButton("📥 Import from Game")
        # import_btn.setStyleSheet(get_button_style())
        # import_btn.clicked.connect(self._import_from_game)
        # toolbar.addWidget(import_btn)
        
        layout.addLayout(toolbar)
        
        # Splitter for units list and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Units list
        units_frame = QFrame()
        units_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        units_layout = QVBoxLayout(units_frame)
        
        units_title = QLabel("📋 Unit Templates")
        units_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        units_layout.addWidget(units_title)
        
        self.units_tree = QTreeWidget()
        self.units_tree.setHeaderLabels(["📁 Name"])
        self.units_tree.setStyleSheet(get_tree_style())
        self.units_tree.itemClicked.connect(self._on_unit_selected)
        units_layout.addWidget(self.units_tree)
        
        splitter.addWidget(units_frame)
        
        # Editor panel
        editor_panel = QFrame()
        editor_panel.setStyleSheet("""
            QFrame {
                background-color: #383848;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setSpacing(15)
        
        editor_title = QLabel("Unit Properties")
        editor_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        editor_layout.addWidget(editor_title)
        
        # Scroll area for properties
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
        scroll_layout.setSpacing(12)
        
        # Form layout for unit properties
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        
        # Combat Stats Section
        combat_title = QLabel("⚔️ Combat Stats")
        combat_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(combat_title)
        
        # Health
        health_row = self._create_property_row("Health:", "e.g., 100", "Maximum health points")
        self.health_input = health_row['input']
        form_layout.addLayout(health_row['layout'])
        
        # Attack
        attack_row = self._create_property_row("Attack:", "e.g., 10", "Base attack damage")
        self.attack_input = attack_row['input']
        form_layout.addLayout(attack_row['layout'])
        
        # Defense
        defense_row = self._create_property_row("Defense:", "e.g., 5", "Base defense value")
        self.defense_input = defense_row['input']
        form_layout.addLayout(defense_row['layout'])
        
        form_layout.addSpacing(10)
        
        # Movement Section
        movement_title = QLabel("🏃 Movement")
        movement_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(movement_title)
        
        # Speed
        speed_row = self._create_property_row("Speed:", "e.g., 1.2", "Movement speed multiplier")
        self.speed_input = speed_row['input']
        form_layout.addLayout(speed_row['layout'])
        
        form_layout.addSpacing(10)
        
        # Economy Section
        economy_title = QLabel("💰 Economy")
        economy_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(economy_title)
        
        # Gather Rate
        gather_row = self._create_property_row("Gather Rate:", "e.g., 1.0", "Resource gathering speed multiplier")
        self.gather_rate_input = gather_row['input']
        form_layout.addLayout(gather_row['layout'])
        
        # Can Gather (checkbox)
        can_gather_layout = QHBoxLayout()
        can_gather_label = QLabel("Can Gather:")
        can_gather_label.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        can_gather_label.setFixedWidth(120)
        can_gather_layout.addWidget(can_gather_label)
        
        self.can_gather_checkbox = QCheckBox("Unit can gather resources")
        self.can_gather_checkbox.setStyleSheet("color: #c0c0d0; font-size: 13px;")
        can_gather_layout.addWidget(self.can_gather_checkbox)
        can_gather_layout.addStretch()
        form_layout.addLayout(can_gather_layout)
        
        form_layout.addSpacing(10)
        
        # Unit Type Section
        type_title = QLabel("🏷️ Unit Type")
        type_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(type_title)
        
        # Is Champion (checkbox)
        is_champion_layout = QHBoxLayout()
        is_champion_label = QLabel("Is Champion:")
        is_champion_label.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        is_champion_label.setFixedWidth(120)
        is_champion_layout.addWidget(is_champion_label)
        
        self.is_champion_checkbox = QCheckBox("Unit is a champion (elite unit)")
        self.is_champion_checkbox.setStyleSheet("color: #c0c0d0; font-size: 13px;")
        is_champion_layout.addWidget(self.is_champion_checkbox)
        is_champion_layout.addStretch()
        form_layout.addLayout(is_champion_layout)
        
        scroll_layout.addWidget(form_container)
        scroll.setWidget(scroll_content)
        editor_layout.addWidget(scroll)
        
        # Save button
        save_btn = QPushButton("💾 Save Unit Properties")
        save_btn.setStyleSheet(get_button_style(accent=True))
        save_btn.clicked.connect(self._save_unit_properties)
        save_btn.setToolTip("Save all unit property changes")
        editor_layout.addWidget(save_btn)
        
        # XML editor (collapsible)
        self.xml_editor = QTextEdit()
        self.xml_editor.setPlaceholderText("Select a unit to edit its XML")
        self.xml_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a2a;
                color: #ffffff;
                border: 2px solid #6a6a8a;
                border-radius: 8px;
                padding: 12px;
                font-family: monospace;
                font-size: 12px;
            }
        """)
        self.xml_editor.setMaximumHeight(150)
        self.xml_editor.setVisible(False)
        editor_layout.addWidget(self.xml_editor)
        
        # XML toggle and save buttons
        xml_layout = QHBoxLayout()
        xml_layout.setSpacing(10)
        
        xml_toggle_btn = QPushButton("🔧 Show/Hide XML")
        xml_toggle_btn.setStyleSheet(get_button_style())
        xml_toggle_btn.clicked.connect(self._toggle_xml_editor)
        xml_layout.addWidget(xml_toggle_btn)
        
        save_xml_btn = QPushButton("💾 Save XML")
        save_xml_btn.setStyleSheet(get_button_style(accent=True))
        save_xml_btn.clicked.connect(self._save_xml)
        xml_layout.addWidget(save_xml_btn)
        
        xml_layout.addStretch()
        editor_layout.addLayout(xml_layout)
        
        splitter.addWidget(editor_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # Track selected unit
        self.selected_unit_path = None
        self.selected_unit_xml = None
    
    def _create_property_row(self, label: str, placeholder: str, tooltip: str) -> dict:
        """Create a property input row."""
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        label_widget.setFixedWidth(120)
        label_widget.setToolTip(tooltip)
        layout.addWidget(label_widget)
        
        input_widget = QLineEdit()
        input_widget.setPlaceholderText(placeholder)
        input_widget.setStyleSheet(get_line_edit_style())
        input_widget.setToolTip(tooltip)
        layout.addWidget(input_widget)
        
        layout.addStretch()
        
        return {'layout': layout, 'input': input_widget}
    
    def refresh(self):
        """Refresh the units list."""
        self._refresh_units()
    
    def _refresh_units(self):
        """Refresh the units tree from the project."""
        self.units_tree.clear()
        
        if not self.main_window.project:
            return
        
        try:
            units = [f for f in self.main_window.project.files.values() 
                     if f.path.startswith('simulation/templates/units/') and f.path.endswith('.xml')]
            
            for unit in sorted(units, key=lambda x: x.path):
                item = QTreeWidgetItem(self.units_tree)
                item.setText(0, Path(unit.path).stem)
                item.setData(0, Qt.ItemDataRole.UserRole, unit.path)
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load units: {e}")
    
    def _on_unit_selected(self, item: QTreeWidgetItem, column: int):
        """Handle unit selection."""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        self.selected_unit_path = path
        
        # Load unit XML
        if self.main_window.project:
            mod_file = self.main_window.project.get_file(path)
            if mod_file:
                self.selected_unit_xml = mod_file.content
                self.xml_editor.setPlainText(mod_file.content)
                self._populate_properties(mod_file.content)
    
    def _populate_properties(self, xml_content: str):
        """Populate property fields from XML content."""
        try:
            # Parse the current XML
            root = ET.fromstring(xml_content)
            
            # Health
            health = root.find(".//Health")
            if health is not None:
                max_health = health.get("Max", "")
                self.health_input.setText(max_health)
            else:
                self.health_input.setText("")
            
            # Attack
            attack = root.find(".//Attack")
            if attack is not None:
                melee = attack.get("Melee", "")
                self.attack_input.setText(melee)
            else:
                self.attack_input.setText("")
            
            # Defense
            resistance = root.find(".//Resistance")
            if resistance is not None:
                hack = resistance.get("Hack", "")
                pierce = resistance.get("Pierce", "")
                crush = resistance.get("Crush", "")
                # Use average for simple display
                if hack and pierce and crush:
                    avg = (float(hack) + float(pierce) + float(crush)) / 3
                    self.defense_input.setText(f"{avg:.1f}")
                else:
                    self.defense_input.setText("")
            else:
                self.defense_input.setText("")
            
            # Speed
            unit_motion = root.find(".//UnitMotion")
            if unit_motion is not None:
                walk_speed = unit_motion.get("WalkSpeed", "")
                self.speed_input.setText(walk_speed)
            else:
                self.speed_input.setText("")
            
            # Gather Rate
            resource_gatherer = root.find(".//ResourceGatherer")
            if resource_gatherer is not None:
                rates = resource_gatherer.get("Rates", "")
                if rates:
                    # Extract base rate from first value
                    parts = rates.split(".")
                    if len(parts) > 1:
                        try:
                            rate = float(parts[-1])
                            self.gather_rate_input.setText(str(rate))
                        except ValueError:
                            self.gather_rate_input.setText("")
                    else:
                        self.gather_rate_input.setText("")
                else:
                    self.gather_rate_input.setText("")
                self.can_gather_checkbox.setChecked(True)
            else:
                self.gather_rate_input.setText("")
                self.can_gather_checkbox.setChecked(False)
            
            # Champion status
            identity = root.find(".//Identity")
            if identity is not None:
                rank = identity.get("Rank", "")
                self.is_champion_checkbox.setChecked(rank.lower() == "elite")
            else:
                self.is_champion_checkbox.setChecked(False)
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to parse unit XML: {e}")
    
    def _save_unit_properties(self):
        """Save unit properties to the project."""
        if not self.selected_unit_path or not self.main_window.project:
            QMessageBox.warning(self, "Warning", "No unit selected")
            return
        
        try:
            # Parse current XML
            root = ET.fromstring(self.selected_unit_xml)
            
            # Update Health
            health = root.find(".//Health")
            if health is None:
                health = ET.SubElement(root, "Health")
            health.set("Max", self.health_input.text() or "100")
            
            # Update Attack
            attack = root.find(".//Attack")
            if attack is None:
                attack = ET.SubElement(root, "Attack")
            attack.set("Melee", self.attack_input.text() or "10")
            
            # Update Defense
            resistance = root.find(".//Resistance")
            if resistance is None:
                resistance = ET.SubElement(root, "Resistance")
            defense_value = self.defense_input.text() or "5"
            resistance.set("Hack", defense_value)
            resistance.set("Pierce", defense_value)
            resistance.set("Crush", defense_value)
            
            # Update Speed
            unit_motion = root.find(".//UnitMotion")
            if unit_motion is None:
                unit_motion = ET.SubElement(root, "UnitMotion")
            unit_motion.set("WalkSpeed", self.speed_input.text() or "1.0")
            
            # Update Gather Rate
            if self.can_gather_checkbox.isChecked():
                resource_gatherer = root.find(".//ResourceGatherer")
                if resource_gatherer is None:
                    resource_gatherer = ET.SubElement(root, "ResourceGatherer")
                gather_rate = self.gather_rate_input.text() or "1.0"
                resource_gatherer.set("Rates", f"food.{gather_rate}")
            else:
                resource_gatherer = root.find(".//ResourceGatherer")
                if resource_gatherer is not None:
                    root.remove(resource_gatherer)
            
            # Update Champion status
            identity = root.find(".//Identity")
            if identity is None:
                identity = ET.SubElement(root, "Identity")
            rank = "Elite" if self.is_champion_checkbox.isChecked() else "Basic"
            identity.set("Rank", rank)
            
            # Convert back to string
            new_xml = ET.tostring(root, encoding='unicode')
            
            # Update project
            self.main_window.project.update_file(new_xml, self.selected_unit_path)
            self.selected_unit_xml = new_xml
            self.xml_editor.setPlainText(new_xml)
            
            QMessageBox.information(self, "Success", "Unit properties saved successfully")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save unit properties: {e}")
    
    def _toggle_xml_editor(self):
        """Toggle XML editor visibility."""
        self.xml_editor.setVisible(not self.xml_editor.isVisible())
    
    def _save_xml(self):
        """Save raw XML content."""
        if not self.selected_unit_path or not self.main_window.project:
            QMessageBox.warning(self, "Warning", "No unit selected")
            return
        
        try:
            xml_content = self.xml_editor.toPlainText()
            self.main_window.project.update_file(xml_content, self.selected_unit_path)
            self.selected_unit_xml = xml_content
            self._populate_properties(xml_content)
            QMessageBox.information(self, "Success", "XML saved successfully")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save XML: {e}")


class NewUnitTab(BaseTab):
    """New Unit tab for creating new unit templates."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("➕ Create New Unit")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("Create a new unit template from scratch or duplicate an existing one.")
        instructions.setStyleSheet("color: #c0c0d0; font-size: 14px;")
        layout.addWidget(instructions)
        
        # Form
        form = QFrame()
        form.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form)
        
        # Unit name
        name_layout = QHBoxLayout()
        name_label = QLabel("Unit Name:")
        name_label.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        name_label.setFixedWidth(120)
        name_layout.addWidget(name_label)
        
        self.unit_name_input = QLineEdit()
        self.unit_name_input.setPlaceholderText("e.g., infantry_spearman")
        self.unit_name_input.setStyleSheet(get_line_edit_style())
        name_layout.addWidget(self.unit_name_input)
        form_layout.addLayout(name_layout)
        
        # Create button
        create_btn = QPushButton("✨ Create Unit")
        create_btn.setStyleSheet(get_button_style(accent=True))
        create_btn.clicked.connect(self._create_unit)
        form_layout.addWidget(create_btn)
        
        layout.addWidget(form)
        layout.addStretch()
    
    def refresh(self):
        """Refresh the tab."""
        pass
    
    def _create_unit(self):
        """Create a new unit template."""
        if not self.main_window.project:
            QMessageBox.warning(self, "Warning", "No project loaded")
            return
        
        unit_name = self.unit_name_input.text().strip()
        if not unit_name:
            QMessageBox.warning(self, "Warning", "Please enter a unit name")
            return
        
        try:
            # Basic unit template
            xml_content = f'''<?xml version="1.0" encoding="utf-8"?>
<Entity>
  <Template>{unit_name}</Template>
  <Identity>
    <Civ>generic</Civ>
    <Generic>Unit</Generic>
    <Specific>{unit_name}</Specific>
    <Rank>Basic</Rank>
  </Identity>
  <Cost>
    <BuildTime>10</BuildTime>
    <Resources>
      <food>50</food>
      <wood>0</wood>
      <stone>0</stone>
      <metal>0</metal>
    </Resources>
  </Cost>
  <Health>
    <Max>100</Max>
  </Health>
  <Attack>
    <Melee>10</Melee>
  </Attack>
  <Resistance>
    <Hack>5</Hack>
    <Pierce>5</Pierce>
    <Crush>5</Crush>
  </Resistance>
  <UnitMotion>
    <WalkSpeed>1.0</WalkSpeed>
  </UnitMotion>
  <VisualActor>
    <Actor>props/units/hellenes/infantry_spearman.xml</Actor>
  </VisualActor>
</Entity>'''
            
            path = f"simulation/templates/units/{unit_name}.xml"
            self.main_window.project.add_file(xml_content, path)
            
            QMessageBox.information(self, "Success", f"Unit '{unit_name}' created successfully")
            self.unit_name_input.clear()
            
            # Refresh units tab
            self.main_window.units_tab.refresh()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create unit: {e}")


class StructuresTab(BaseTab):
    """Structures tab for managing building templates."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header = QLabel("🏗️ Structures")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        info = QLabel("Manage building and structure templates.")
        info.setStyleSheet("color: #c0c0d0; font-size: 14px;")
        layout.addWidget(info)
        
        layout.addStretch()
    
    def refresh(self):
        """Refresh the tab."""
        pass


class TechsTab(BaseTab):
    """Technologies tab for managing research and upgrades."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header = QLabel("🔬 Technologies")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        info = QLabel("Manage technologies and research upgrades.")
        info.setStyleSheet("color: #c0c0d0; font-size: 14px;")
        layout.addWidget(info)
        
        layout.addStretch()
    
    def refresh(self):
        """Refresh the tab."""
        pass


class AurasTab(BaseTab):
    """Auras tab for managing unit and building auras."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header = QLabel("✨ Auras")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        info = QLabel("Manage auras and special effects.")
        info.setStyleSheet("color: #c0c0d0; font-size: 14px;")
        layout.addWidget(info)
        
        layout.addStretch()
    
    def refresh(self):
        """Refresh the tab."""
        pass


class SettingsTab(BaseTab):
    """Settings tab for application configuration."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header = QLabel("⚙️ Settings")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        # Game data path
        path_frame = QFrame()
        path_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        path_layout = QVBoxLayout(path_frame)
        
        path_title = QLabel("🎮 Game Data Path")
        path_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        path_layout.addWidget(path_title)
        
        path_info = QLabel("Configure the path to your 0 A.D. game data for importing assets.")
        path_info.setStyleSheet("color: #c0c0d0; font-size: 13px;")
        path_layout.addWidget(path_info)
        
        path_input_layout = QHBoxLayout()
        self.game_path_input = QLineEdit()
        self.game_path_input.setPlaceholderText("Path to 0 A.D. data folder")
        self.game_path_input.setStyleSheet(get_line_edit_style())
        path_input_layout.addWidget(self.game_path_input)
        
        browse_btn = QPushButton("📂 Browse")
        browse_btn.setStyleSheet(get_button_style())
        browse_btn.clicked.connect(self._browse_game_path)
        path_input_layout.addWidget(browse_btn)
        
        path_layout.addLayout(path_input_layout)
        
        save_path_btn = QPushButton("💾 Save Path")
        save_path_btn.setStyleSheet(get_button_style(accent=True))
        save_path_btn.clicked.connect(self._save_game_path)
        path_layout.addWidget(save_path_btn)
        
        layout.addWidget(path_frame)
        layout.addStretch()
    
    def refresh(self):
        """Refresh settings from storage."""
        if self.main_window.settings.game_data_path:
            self.game_path_input.setText(self.main_window.settings.game_data_path)
    
    def _browse_game_path(self):
        """Browse for game data path."""
        path = QFileDialog.getExistingDirectory(self, "Select 0 A.D. Data Folder")
        if path:
            self.game_path_input.setText(path)
    
    def _save_game_path(self):
        """Save the game data path."""
        path = self.game_path_input.text().strip()
        if path:
            self.main_window.settings.game_data_path = path
            self.main_window.settings.save()
            QMessageBox.information(self, "Success", "Game data path saved successfully")
        else:
            QMessageBox.warning(self, "Warning", "Please enter a valid path")


class RecentTab(BaseTab):
    """Recent projects tab."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header = QLabel("🕒 Recent Projects")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        info = QLabel("View and manage your recent projects.")
        info.setStyleSheet("color: #c0c0d0; font-size: 14px;")
        layout.addWidget(info)
        
        layout.addStretch()
    
    def refresh(self):
        """Refresh the tab."""
        pass
