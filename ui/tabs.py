"""Tab widgets for the main application - UPDATED VERSION."""

from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QFrame, QTextEdit, QLineEdit,
    QFileDialog, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QSplitter, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.assets import AssetSource, AssetEntry
from core.mod import ModProject
from ui.styles import get_tree_style, get_button_style, get_input_style


class AssetsTab(QWidget):
    """Assets browser tab."""
    
    def __init__(self, asset_source: Optional[AssetSource], project: Optional[ModProject]):
        super().__init__()
        self.asset_source = asset_source
        self.project = project
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("📁 Game Assets")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(title)
        
        # Quick navigation buttons
        nav_bar = QFrame()
        nav_bar.setStyleSheet("background-color: #383848; border-radius: 5px; padding: 5px;")
        nav_layout = QHBoxLayout(nav_bar)
        
        units_btn = QPushButton("⚔️ Units")
        units_btn.setStyleSheet(get_button_style())
        units_btn.clicked.connect(lambda: self._navigate_to("simulation/templates/units"))
        nav_layout.addWidget(units_btn)
        
        techs_btn = QPushButton("🔬 Techs")
        techs_btn.setStyleSheet(get_button_style())
        techs_btn.clicked.connect(lambda: self._navigate_to("simulation/data/technologies"))
        nav_layout.addWidget(techs_btn)
        
        structs_btn = QPushButton("🏛️ Structures")
        structs_btn.setStyleSheet(get_button_style())
        structs_btn.clicked.connect(lambda: self._navigate_to("simulation/templates/structures"))
        nav_layout.addWidget(structs_btn)
        
        nav_layout.addStretch()
        layout.addWidget(nav_bar)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #383848; border-radius: 5px; padding: 5px;")
        toolbar_layout = QHBoxLayout(toolbar)
        
        browse_btn = QPushButton("📂 Browse Folder")
        browse_btn.setStyleSheet(get_button_style())
        browse_btn.clicked.connect(self._browse_game_folder)
        toolbar_layout.addWidget(browse_btn)
        
        import_btn = QPushButton("📥 Import Selected")
        import_btn.setStyleSheet(get_button_style())
        import_btn.clicked.connect(self._import_selected_from_tree)
        toolbar_layout.addWidget(import_btn)
        
        toolbar_layout.addStretch()
        layout.addWidget(toolbar)
        
        # Tree
        self.asset_tree = QTreeWidget()
        self.asset_tree.setHeaderLabels(["Name", "Type", "Size"])
        self.asset_tree.setStyleSheet(get_tree_style())
        self.asset_tree.itemDoubleClicked.connect(self._on_asset_double_click)
        layout.addWidget(self.asset_tree)
        
        if not self.asset_source:
            info = QLabel("⚠️ No game data loaded. Set game data folder in File menu.")
            info.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info)
        else:
            self._load_root()
    
    def _load_root(self):
        """Load root directory."""
        self.asset_tree.clear()
        self._populate_tree("")
    
    def _navigate_to(self, path: str):
        """Navigate to specific path."""
        self.asset_tree.clear()
        self._populate_tree(path)
    
    def _populate_tree(self, path: str):
        """Populate tree with directory contents."""
        try:
            entries = self.asset_source.list_dir(path)
            for entry in entries:
                item = QTreeWidgetItem(self.asset_tree)
                icon = "📁" if entry.type == "dir" else "📄"
                item.setText(0, f"{icon} {entry.name}")
                item.setText(1, entry.type)
                item.setText(2, str(entry.size) if entry.size else "")
                item.setData(0, Qt.ItemDataRole.UserRole, entry.rel_path)
                self.asset_tree.addTopLevelItem(item)
        except Exception as e:
            print(f"Error populating tree: {e}")
    
    def _on_asset_double_click(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on asset."""
        if item.text(1) == "dir":
            # Navigate into directory
            rel_path = item.data(0, Qt.ItemDataRole.UserRole)
            if rel_path:
                self._populate_tree(rel_path)
        else:
            # Import file
            self._import_item(item)
    
    def _import_item(self, item: QTreeWidgetItem):
        """Import a single item."""
        if not self.project or not self.project.is_loaded:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return
        
        rel_path = item.data(0, Qt.ItemDataRole.UserRole)
        
        try:
            if self.asset_source:
                content = self.asset_source.read_text(rel_path)
                if content is not None:
                    self.project.add_file(content, rel_path)
                    self.project.save()
                    QMessageBox.information(self, "Success", f"File imported successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Could not read file content.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import file: {e}")
    
    def _import_selected_from_tree(self):
        """Import selected item from main tree."""
        selected = self.asset_tree.selectedItems()
        if selected:
            self._import_item(selected[0])
        else:
            QMessageBox.warning(self, "No Selection", "Please select a file first.")
    
    def _browse_game_folder(self):
        """Browse the game folder structure."""
        if not self.asset_source:
            QMessageBox.warning(self, "No Game Data", "Please set the game data folder first.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Browse Game Folder")
        dialog.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Current path label
        self.browse_path_label = QLabel("/")
        self.browse_path_label.setStyleSheet("color: #7b5eff; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.browse_path_label)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        up_btn = QPushButton("⬆️ Up")
        up_btn.setStyleSheet(get_button_style())
        up_btn.clicked.connect(lambda: self._browse_up(dialog))
        nav_layout.addWidget(up_btn)
        
        home_btn = QPushButton("🏠 Root")
        home_btn.setStyleSheet(get_button_style())
        home_btn.clicked.connect(lambda: self._browse_to_root(dialog))
        nav_layout.addWidget(home_btn)
        
        nav_layout.addStretch()
        layout.addLayout(nav_layout)
        
        # Tree
        self.browse_tree = QTreeWidget()
        self.browse_tree.setHeaderLabels(["Name", "Type", "Size"])
        self.browse_tree.setStyleSheet(get_tree_style())
        self.browse_tree.itemDoubleClicked.connect(self._on_browse_double_click)
        layout.addWidget(self.browse_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 Import Selected")
        import_btn.setStyleSheet(get_button_style(accent=True))
        import_btn.clicked.connect(lambda: self._import_selected(dialog))
        button_layout.addWidget(import_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(get_button_style())
        close_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Store current browse path
        self.current_browse_path = ""
        
        # Load root
        self._browse_to_root(dialog)
        
        dialog.exec()
    
    def _browse_to_root(self, dialog: QDialog):
        """Navigate to root."""
        self.current_browse_path = ""
        self.browse_path_label.setText("/")
        self.browse_tree.clear()
        self._populate_browse("", dialog)
    
    def _browse_up(self, dialog: QDialog):
        """Navigate up one level."""
        if self.current_browse_path:
            from pathlib import Path
            parent = str(Path(self.current_browse_path).parent)
            self.current_browse_path = parent if parent != "." else ""
            self.browse_path_label.setText(self.current_browse_path or "/")
            self.browse_tree.clear()
            self._populate_browse(self.current_browse_path, dialog)
    
    def _populate_browse(self, path: str, dialog: QDialog):
        """Populate browse tree."""
        try:
            entries = self.asset_source.list_dir(path)
            for entry in entries:
                item = QTreeWidgetItem(self.browse_tree)
                icon = "📁" if entry.type == "dir" else "📄"
                item.setText(0, f"{icon} {entry.name}")
                item.setText(1, entry.type)
                item.setText(2, str(entry.size) if entry.size else "")
                item.setData(0, Qt.ItemDataRole.UserRole, entry.rel_path)
                self.browse_tree.addTopLevelItem(item)
        except Exception as e:
            QMessageBox.warning(dialog, "Error", f"Failed to load folder: {e}")
    
    def _on_browse_double_click(self, item: QTreeWidgetItem, column: int):
        """Handle double-click to navigate into folder."""
        if item.text(1) == "dir":
            rel_path = item.data(0, Qt.ItemDataRole.UserRole)
            if rel_path:
                self.current_browse_path = rel_path
                self.browse_path_label.setText(rel_path)
                self.browse_tree.clear()
                self._populate_browse(rel_path, self.window())
    
    def _import_selected(self, dialog: QDialog):
        """Import selected file to project."""
        selected = self.browse_tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a file first.")
            return
        
        if not self.project or not self.project.is_loaded:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return
        
        item = selected[0]
        rel_path = item.data(0, Qt.ItemDataRole.UserRole)
        
        if item.text(1) == "dir":
            QMessageBox.information(self, "Info", "Folder import not yet implemented. Please select a file.")
            return
        
        try:
            if self.asset_source:
                content = self.asset_source.read_text(rel_path)
                if content is not None:
                    self.project.add_file(content, rel_path)
                    self.project.save()
                    QMessageBox.information(self, "Success", f"File imported successfully!")
                    dialog.accept()
                else:
                    QMessageBox.warning(self, "Error", "Could not read file content.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import file: {e}")
    
    def _browse_game_folder(self):
        """Browse the game folder structure."""
        if not self.asset_source:
            QMessageBox.warning(self, "No Game Data", "Please set the game data folder first.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Browse Game Folder")
        dialog.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Current path label
        self.browse_path_label = QLabel("/")
        self.browse_path_label.setStyleSheet("color: #7b5eff; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.browse_path_label)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        up_btn = QPushButton("⬆️ Up")
        up_btn.setStyleSheet(get_button_style())
        up_btn.clicked.connect(lambda: self._browse_up(dialog))
        nav_layout.addWidget(up_btn)
        
        home_btn = QPushButton("🏠 Root")
        home_btn.setStyleSheet(get_button_style())
        home_btn.clicked.connect(lambda: self._browse_to_root(dialog))
        nav_layout.addWidget(home_btn)
        
        nav_layout.addStretch()
        layout.addLayout(nav_layout)
        
        # Tree
        self.browse_tree = QTreeWidget()
        self.browse_tree.setHeaderLabels(["Name", "Type", "Size"])
        self.browse_tree.setStyleSheet(get_tree_style())
        self.browse_tree.itemDoubleClicked.connect(self._on_browse_double_click)
        layout.addWidget(self.browse_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 Import Selected")
        import_btn.setStyleSheet(get_button_style(accent=True))
        import_btn.clicked.connect(lambda: self._import_selected(dialog))
        button_layout.addWidget(import_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(get_button_style())
        close_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Store current browse path
        self.current_browse_path = ""
        
        # Load root
        self._browse_to_root(dialog)
        
        dialog.exec()
    
    def _browse_to_root(self, dialog: QDialog):
        """Navigate to root."""
        self.current_browse_path = ""
        self.browse_path_label.setText("/")
        self.browse_tree.clear()
        self._populate_browse("", dialog)
    
    def _browse_up(self, dialog: QDialog):
        """Navigate up one level."""
        if self.current_browse_path:
            from pathlib import Path
            parent = str(Path(self.current_browse_path).parent)
            self.current_browse_path = parent if parent != "." else ""
            self.browse_path_label.setText(self.current_browse_path or "/")
            self.browse_tree.clear()
            self._populate_browse(self.current_browse_path, dialog)
    
    def _populate_browse(self, path: str, dialog: QDialog):
        """Populate browse tree."""
        try:
            entries = self.asset_source.list_dir(path)
            for entry in entries:
                item = QTreeWidgetItem(self.browse_tree)
                icon = "📁" if entry.type == "dir" else "📄"
                item.setText(0, f"{icon} {entry.name}")
                item.setText(1, entry.type)
                item.setText(2, str(entry.size) if entry.size else "")
                item.setData(0, Qt.ItemDataRole.UserRole, entry.rel_path)
                self.browse_tree.addTopLevelItem(item)
        except Exception as e:
            QMessageBox.warning(dialog, "Error", f"Failed to load folder: {e}")
    
    def _on_browse_double_click(self, item: QTreeWidgetItem, column: int):
        """Handle double-click to navigate into folder."""
        if item.text(1) == "dir":
            rel_path = item.data(0, Qt.ItemDataRole.UserRole)
            if rel_path:
                self.current_browse_path = rel_path
                self.browse_path_label.setText(rel_path)
                self.browse_tree.clear()
                self._populate_browse(rel_path, self.window())
    
    def _import_selected(self, dialog: QDialog):
        """Import selected file to project."""
        selected = self.browse_tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a file first.")
            return
        
        if not self.project or not self.project.is_loaded:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return
        
        item = selected[0]
        rel_path = item.data(0, Qt.ItemDataRole.UserRole)
        
        if item.text(1) == "dir":
            QMessageBox.information(self, "Info", "Folder import not yet implemented. Please select a file.")
            return
        
        try:
            if self.asset_source:
                content = self.asset_source.read_text(rel_path)
                if content is not None:
                    self.project.add_file(content, rel_path)
                    self.project.save()
                    QMessageBox.information(self, "Success", f"File imported successfully!")
                    dialog.accept()
                else:
                    QMessageBox.warning(self, "Error", "Could not read file content.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import file: {e}")


class UnitsTab(QWidget):
    """Units editor tab."""
    
    def __init__(self, project: Optional[ModProject], asset_source: Optional[AssetSource]):
        super().__init__()
        self.project = project
        self.asset_source = asset_source
        self.selected_unit = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("⚔️ Units")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(title)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #383848; border-radius: 5px; padding: 5px;")
        toolbar_layout = QHBoxLayout(toolbar)
        
        import_btn = QPushButton("📥 Import from Game")
        import_btn.setStyleSheet(get_button_style())
        toolbar_layout.addWidget(import_btn)
        
        toolbar_layout.addStretch()
        layout.addWidget(toolbar)
        
        # Splitter for tree and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tree panel
        tree_panel = QFrame()
        tree_layout = QVBoxLayout(tree_panel)
        
        self.unit_tree = QTreeWidget()
        self.unit_tree.setHeaderLabels(["Unit Name", "Civ", "Type"])
        self.unit_tree.setStyleSheet(get_tree_style())
        self.unit_tree.itemClicked.connect(self._on_unit_selected)
        tree_layout.addWidget(self.unit_tree)
        
        splitter.addWidget(tree_panel)
        
        # Editor panel
        editor_panel = QFrame()
        editor_panel.setStyleSheet("""
            QFrame {
                background-color: #404050;
                border: 2px solid #6a6a8a;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        editor_layout = QVBoxLayout(editor_panel)
        
        editor_title = QLabel("Unit Properties")
        editor_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #7b5eff;")
        editor_layout.addWidget(editor_title)
        
        # Health input
        health_layout = QHBoxLayout()
        health_label = QLabel("Health:")
        health_label.setStyleSheet("color: #c0c0d0; font-size: 12px;")
        health_layout.addWidget(health_label)
        
        self.health_input = QLineEdit()
        self.health_input.setPlaceholderText("e.g., 100")
        self.health_input.setStyleSheet(get_input_style())
        health_layout.addWidget(self.health_input)
        
        save_health_btn = QPushButton("Save")
        save_health_btn.setStyleSheet(get_button_style())
        save_health_btn.clicked.connect(self._save_health)
        health_layout.addWidget(save_health_btn)
        
        editor_layout.addLayout(health_layout)
        
        # XML editor
        self.xml_editor = QTextEdit()
        self.xml_editor.setPlaceholderText("Select a unit to edit its XML")
        self.xml_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a2a;
                color: #ffffff;
                border: 2px solid #6a6a8a;
                border-radius: 5px;
                padding: 10px;
                font-family: Consolas;
                font-size: 11px;
            }
        """)
        editor_layout.addWidget(self.xml_editor)
        
        # Save XML button
        save_xml_btn = QPushButton("💾 Save XML")
        save_xml_btn.setStyleSheet(get_button_style(accent=True))
        save_xml_btn.clicked.connect(self._save_xml)
        editor_layout.addWidget(save_xml_btn)
        
        splitter.addWidget(editor_panel)
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        
        if not self.project or not self.project.is_loaded:
            info = QLabel("⚠️ No mod loaded. Create or open a mod to edit units.")
            info.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info)
        else:
            self._load_units()
    
    def _load_units(self):
        """Load units from project."""
        self.unit_tree.clear()
        
        unit_files = [f for f in self.project.list_files() if "units" in f and f.endswith('.xml')]
        
        if not unit_files:
            item = QTreeWidgetItem(self.unit_tree)
            item.setText(0, "No units yet - Import from game or create new units")
            item.setForeground(0, QColor("#9090a0"))
            self.unit_tree.addTopLevelItem(item)
            return
        
        for unit_file in unit_files:
            unit_data = self._parse_unit_file(unit_file)
            item = QTreeWidgetItem(self.unit_tree)
            item.setText(0, Path(unit_file).stem)
            item.setText(1, unit_data.get("civ", "Unknown"))
            item.setText(2, unit_data.get("type", "Unknown"))
            item.setData(0, Qt.ItemDataRole.UserRole, unit_file)
            self.unit_tree.addTopLevelItem(item)
    
    def _parse_unit_file(self, file_path: str) -> dict:
        """Parse unit XML file to extract info."""
        try:
            mod_file = self.project.get_file(file_path)
            if mod_file:
                root = ET.fromstring(mod_file.content)
                
                # Extract civ
                civ = "Unknown"
                identity = root.find(".//Identity")
                if identity is not None:
                    civ_elem = identity.find("Civ")
                    if civ_elem is not None:
                        civ = civ_elem.text or "Unknown"
                
                # Extract type
                unit_type = "Unknown"
                identity = root.find(".//Identity")
                if identity is not None:
                    type_elem = identity.find("Classes")
                    if type_elem is not None:
                        unit_type = type_elem.text or "Unknown"
                
                # Extract health
                health = None
                health_elem = root.find(".//Health")
                if health_elem is not None:
                    max_hp = health_elem.find("Max")
                    if max_hp is not None:
                        health = max_hp.text
                
                return {
                    "civ": civ,
                    "type": unit_type,
                    "health": health,
                    "xml": mod_file.content
                }
        except Exception as e:
            print(f"Error parsing unit {file_path}: {e}")
        
        return {"civ": "Unknown", "type": "Unknown", "health": None, "xml": ""}
    
    def _on_unit_selected(self, item: QTreeWidgetItem, column: int):
        """Handle unit selection."""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        unit_data = self._parse_unit_file(file_path)
        
        self.selected_unit = file_path
        
        # Show health
        if unit_data.get("health"):
            self.health_input.setText(unit_data["health"])
        else:
            self.health_input.clear()
        
        # Show XML
        self.xml_editor.setPlainText(unit_data.get("xml", ""))
    
    def _save_health(self):
        """Save health value to unit."""
        if not self.selected_unit:
            QMessageBox.warning(self, "No Selection", "Please select a unit first.")
            return
        
        health = self.health_input.text().strip()
        if not health:
            QMessageBox.warning(self, "Invalid Value", "Please enter a health value.")
            return
        
        try:
            mod_file = self.project.get_file(self.selected_unit)
            if mod_file:
                root = ET.fromstring(mod_file.content)
                
                # Find or create Health element
                health_elem = root.find(".//Health")
                if health_elem is None:
                    # Create Health element
                    # Find the root Entity
                    entity = root if root.tag == "Entity" else root.find(".//Entity")
                    if entity is not None:
                        health_elem = ET.SubElement(entity, "Health")
                    else:
                        # Add to root
                        health_elem = ET.SubElement(root, "Health")
                
                # Set Max
                max_hp = health_elem.find("Max")
                if max_hp is None:
                    max_hp = ET.SubElement(health_elem, "Max")
                max_hp.text = health
                
                # Save back
                self.project.update_file(ET.tostring(root, encoding='unicode'), self.selected_unit)
                self.project.save()
                
                # Refresh editor
                unit_data = self._parse_unit_file(self.selected_unit)
                self.xml_editor.setPlainText(unit_data.get("xml", ""))
                
                QMessageBox.information(self, "Success", "Health value saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save health: {e}")
    
    def _save_xml(self):
        """Save XML editor content."""
        if not self.selected_unit:
            QMessageBox.warning(self, "No Selection", "Please select a unit first.")
            return
        
        xml_content = self.xml_editor.toPlainText()
        if not xml_content:
            QMessageBox.warning(self, "Empty XML", "XML content is empty.")
            return
        
        try:
            # Validate XML
            ET.fromstring(xml_content)
            
            self.project.update_file(xml_content, self.selected_unit)
            self.project.save()
            
            # Refresh unit list
            self._load_units()
            
            QMessageBox.information(self, "Success", "XML saved successfully!")
        except ET.ParseError as e:
            QMessageBox.critical(self, "Invalid XML", f"XML parsing error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save XML: {e}")


class NewUnitTab(QWidget):
    """New unit creator tab."""
    
    def __init__(self, asset_source: Optional[AssetSource]):
        super().__init__()
        self.asset_source = asset_source
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("✨ New Unit")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(title)
        
        # Form
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
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., my_spearman")
        self.name_input.setStyleSheet(get_input_style())
        form_layout.addRow("Unit Name:", self.name_input)
        
        parent_layout = QHBoxLayout()
        self.parent_input = QLineEdit()
        self.parent_input.setPlaceholderText("template_unit_infantry_melee_spearman")
        self.parent_input.setStyleSheet(get_input_style())
        parent_layout.addWidget(self.parent_input)
        
        browse_btn = QPushButton("🔍 Browse")
        browse_btn.setStyleSheet(get_button_style())
        browse_btn.clicked.connect(self._browse_parent_template)
        parent_layout.addWidget(browse_btn)
        
        form_layout.addRow("Parent Template:", parent_layout)
        
        self.civ_input = QLineEdit()
        self.civ_input.setPlaceholderText("gaia")
        self.civ_input.setStyleSheet(get_input_style())
        form_layout.addRow("Civilization:", self.civ_input)
        
        self.display_input = QLineEdit()
        self.display_input.setPlaceholderText("My Spearman")
        self.display_input.setStyleSheet(get_input_style())
        form_layout.addRow("Display Name:", self.display_input)
        
        layout.addWidget(form_frame)
        
        # Create button
        create_btn = QPushButton("✨ Create Unit")
        create_btn.setStyleSheet(get_button_style(accent=True))
        create_btn.clicked.connect(self._create_unit)
        layout.addWidget(create_btn)
    
    def _browse_parent_template(self):
        """Browse for parent template from game assets."""
        if not self.asset_source:
            QMessageBox.warning(self, "No Game Data", "Please set the game data folder first.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Parent Template")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Template tree
        template_tree = QTreeWidget()
        template_tree.setHeaderLabels(["Template Name"])
        template_tree.setStyleSheet(get_tree_style())
        layout.addWidget(template_tree)
        
        # Populate with available templates
        try:
            templates = self.asset_source.list_unit_templates()
            for template in templates:
                item = QTreeWidgetItem(template_tree)
                item.setText(0, template.name)
                item.setData(0, Qt.ItemDataRole.UserRole, template.rel_path)
                template_tree.addTopLevelItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load templates: {e}")
        
        # Buttons
        button_layout = QHBoxLayout()
        select_btn = QPushButton("Select")
        select_btn.setStyleSheet(get_button_style(accent=True))
        select_btn.clicked.connect(lambda: self._select_template(template_tree, dialog))
        button_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(get_button_style())
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _select_template(self, template_tree: QTreeWidget, dialog: QDialog):
        """Select a template and fill the parent field."""
        selected = template_tree.selectedItems()
        if selected:
            self.parent_input.setText(selected[0].text(0))
            dialog.accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a template first.")
    
    def _create_unit(self):
        """Create a new unit."""
        name = self.name_input.text().strip()
        parent = self.parent_input.text().strip()
        civ = self.civ_input.text().strip()
        display = self.display_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Missing Name", "Unit name is required.")
            return
        
        # Get parent window to access project
        main_window = self.window()
        if not hasattr(main_window, 'project') or not main_window.project:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return
        
        # Create unit XML
        unit_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<Entity parent="{parent}">
  <Identity>
    <Civ>{civ or "gaia"}</Civ>
    <GenericName>{display or name}</GenericName>
  </Identity>
</Entity>'''
        
        # Add to project
        unit_path = f"simulation/templates/units/{name}.xml"
        main_window.project.add_file(unit_xml, unit_path)
        main_window.project.save()
        
        QMessageBox.information(self, "Success", f"Unit '{name}' created successfully!")
        
        # Clear form
        self.name_input.clear()
        self.parent_input.clear()
        self.civ_input.clear()
        self.display_input.clear()
        
        # Refresh the units tab
        main_window._create_tabs()


class SettingsTab(QWidget):
    """Mod settings tab."""
    
    def __init__(self, project: Optional[ModProject]):
        super().__init__()
        self.project = project
        self.inputs = {}
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("🔧 Mod Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(title)
        
        if not self.project or not self.project.is_loaded:
            info = QLabel("⚠️ No mod loaded. Create or open a mod to edit settings.")
            info.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info)
        else:
            # Form
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
            
            fields = [
                ("Mod Name (internal)", self.project.info.name),
                ("Display Label", self.project.info.label),
                ("Version", self.project.info.version),
                ("Description", self.project.info.description),
                ("Dependencies", ", ".join(self.project.info.dependencies)),
            ]
            
            for label_text, default_value in fields:
                field_header = QLabel(f"{label_text}")
                field_header.setStyleSheet("color: #9090a0; font-size: 10px; margin-bottom: 5px;")
                form_layout.addWidget(field_header)
                
                if label_text == "Description":
                    input_field = QTextEdit()
                    input_field.setPlainText(default_value)
                    input_field.setMaximumHeight(80)
                    input_field.setStyleSheet(get_input_style())
                else:
                    input_field = QLineEdit()
                    input_field.setText(default_value)
                    input_field.setStyleSheet(get_input_style())
                
                form_layout.addWidget(input_field)
                self.inputs[label_text] = input_field
            
            layout.addWidget(form_frame)
            
            # Save button
            save_btn = QPushButton("✨ Save Settings")
            save_btn.setStyleSheet(get_button_style(accent=True))
            save_btn.clicked.connect(self._save_settings)
            layout.addWidget(save_btn)
    
    def _save_settings(self):
        """Save the settings."""
        if not self.project or not self.project.is_loaded:
            return
        
        try:
            self.project.info.name = self.inputs["Mod Name (internal)"].text().strip()
            self.project.info.label = self.inputs["Display Label"].text().strip()
            self.project.info.version = self.inputs["Version"].text().strip()
            self.project.info.description = self.inputs["Description"].toPlainText().strip()
            deps_str = self.inputs["Dependencies"].text().strip()
            self.project.info.dependencies = [d.strip() for d in deps_str.split(",") if d.strip()]
            
            self.project.save()
            QMessageBox.information(self, "Success", "Settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")


class OverviewTab(QWidget):
    """Mod overview tab."""
    
    def __init__(self, project: Optional[ModProject]):
        super().__init__()
        self.project = project
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("📊 Mod Overview")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(title)
        
        if not self.project or not self.project.is_loaded:
            info = QLabel("⚠️ No mod loaded. Create or open a mod to view overview.")
            info.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info)
        else:
            # Info card
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
            
            # Build button
            build_btn = QPushButton("🔨 Build .pyromod")
            build_btn.setStyleSheet(get_button_style(accent=True))
            build_btn.clicked.connect(self._build_pyromod)
            layout.addWidget(build_btn)
    
    def _build_pyromod(self):
        """Build the project as a .pyromod file."""
        if not self.project or not self.project.is_loaded:
            return
        
        from PyQt6.QtWidgets import QFileDialog
        
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


class RecentTab(QWidget):
    """Recent projects tab."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._load_recent()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("🕒 Recent Projects")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(title)
        
        # Tree
        self.recent_tree = QTreeWidget()
        self.recent_tree.setHeaderLabels(["📁 Mod Name", "📍 Location", "📅 Last Opened"])
        self.recent_tree.setStyleSheet(get_tree_style())
        layout.addWidget(self.recent_tree)
    
    def _load_recent(self):
        from core.settings import AppSettings
        import time
        
        settings = AppSettings()
        for entry in settings.recent_projects:
            path = entry.get("path", "")
            exists = Path(path).exists() and path.endswith('.adcreator')
            
            timestamp = entry.get("timestamp", 0)
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp)) if timestamp > 0 else "Unknown"
            
            item = QTreeWidgetItem(self.recent_tree)
            item.setText(0, entry.get("label", "Unknown"))
            item.setText(1, path)
            item.setText(2, date_str)
            
            if not exists:
                item.setForeground(0, QColor("#707080"))
                item.setForeground(1, QColor("#707080"))


class StructureTab(QWidget):
    """Mod structure tab."""
    
    def __init__(self, project: Optional[ModProject]):
        super().__init__()
        self.project = project
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("🏗️ Mod Structure")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(title)
        
        if not self.project or not self.project.is_loaded:
            info = QLabel("⚠️ No mod loaded. Create or open a mod to view structure.")
            info.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info)
        else:
            # Tree
            self.structure_tree = QTreeWidget()
            self.structure_tree.setHeaderLabels(["Path", "Type"])
            self.structure_tree.setStyleSheet(get_tree_style())
            layout.addWidget(self.structure_tree)
            
            # Load structure
            self._load_structure()
    
    def _load_structure(self):
        if not self.project:
            return
        
        files = self.project.list_files()
        for file_path in files:
            item = QTreeWidgetItem(self.structure_tree)
            item.setText(0, file_path)
            item.setText(1, "File")
            self.structure_tree.addTopLevelItem(item)


class TechsTab(QWidget):
    """Technologies editor tab."""
    
    def __init__(self, project: Optional[ModProject], asset_source: Optional[AssetSource]):
        super().__init__()
        self.project = project
        self.asset_source = asset_source
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("🔬 Technologies")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(title)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #383848; border-radius: 5px; padding: 5px;")
        toolbar_layout = QHBoxLayout(toolbar)
        
        browse_btn = QPushButton("📂 Browse Techs")
        browse_btn.setStyleSheet(get_button_style())
        browse_btn.clicked.connect(self._browse_techs)
        toolbar_layout.addWidget(browse_btn)
        
        create_btn = QPushButton("✨ Create Tech")
        create_btn.setStyleSheet(get_button_style(accent=True))
        toolbar_layout.addWidget(create_btn)
        
        import_btn = QPushButton("📥 Import from Game")
        import_btn.setStyleSheet(get_button_style())
        toolbar_layout.addWidget(import_btn)
        
        toolbar_layout.addStretch()
        layout.addWidget(toolbar)
        
        # Tree
        self.tech_tree = QTreeWidget()
        self.tech_tree.setHeaderLabels(["Tech Name", "Phase"])
        self.tech_tree.setStyleSheet(get_tree_style())
        self.tech_tree.itemDoubleClicked.connect(self._on_tech_double_click)
        layout.addWidget(self.tech_tree)
        
        if not self.project or not self.project.is_loaded:
            info = QLabel("⚠️ No mod loaded. Create or open a mod to edit technologies.")
            info.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info)
        else:
            self._load_techs()
    
    def _load_techs(self):
        """Load technologies from project."""
        self.tech_tree.clear()
        
        tech_files = [f for f in self.project.list_files() if "technologies" in f and f.endswith('.xml')]
        
        if not tech_files:
            item = QTreeWidgetItem(self.tech_tree)
            item.setText(0, "No technologies yet - Browse game or create new techs")
            item.setForeground(0, QColor("#9090a0"))
            self.tech_tree.addTopLevelItem(item)
            return
        
        for tech_file in tech_files:
            item = QTreeWidgetItem(self.tech_tree)
            item.setText(0, Path(tech_file).stem)
            item.setText(1, "Unknown")
            item.setData(0, Qt.ItemDataRole.UserRole, tech_file)
            self.tech_tree.addTopLevelItem(item)
    
    def _browse_techs(self):
        """Browse technologies from game data."""
        if not self.asset_source:
            QMessageBox.warning(self, "No Game Data", "Please set the game data folder first.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Browse Technologies")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Tree
        tech_tree = QTreeWidget()
        tech_tree.setHeaderLabels(["Tech Name"])
        tech_tree.setStyleSheet(get_tree_style())
        tech_tree.itemDoubleClicked.connect(lambda: self._import_game_tech(tech_tree, dialog))
        layout.addWidget(tech_tree)
        
        # Populate with techs
        try:
            entries = self.asset_source.list_dir("simulation/data/technologies")
            for entry in entries:
                if entry.type == "file" and entry.name.endswith('.xml'):
                    item = QTreeWidgetItem(tech_tree)
                    item.setText(0, entry.name)
                    item.setData(0, Qt.ItemDataRole.UserRole, entry.rel_path)
                    tech_tree.addTopLevelItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load techs: {e}")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 Import Selected")
        import_btn.setStyleSheet(get_button_style(accent=True))
        import_btn.clicked.connect(lambda: self._import_game_tech(tech_tree, dialog))
        button_layout.addWidget(import_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(get_button_style())
        close_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _import_game_tech(self, tree: QTreeWidget, dialog: QDialog):
        """Import tech from game data."""
        selected = tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a tech first.")
            return
        
        if not self.project or not self.project.is_loaded:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return
        
        item = selected[0]
        rel_path = item.data(0, Qt.ItemDataRole.UserRole)
        
        try:
            if self.asset_source:
                content = self.asset_source.read_text(rel_path)
                if content is not None:
                    self.project.add_file(content, rel_path)
                    self.project.save()
                    self._load_techs()
                    QMessageBox.information(self, "Success", f"Tech imported successfully!")
                    dialog.accept()
                else:
                    QMessageBox.warning(self, "Error", "Could not read tech content.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import tech: {e}")
    
    def _on_tech_double_click(self, item: QTreeWidgetItem, column: int):
        """Handle double-click to open tech in editor."""
        # Future: implement tech editor
        QMessageBox.information(self, "Info", "Tech editor coming soon!")


class StructuresTab(QWidget):
    """Structures editor tab."""
    
    def __init__(self, project: Optional[ModProject], asset_source: Optional[AssetSource]):
        super().__init__()
        self.project = project
        self.asset_source = asset_source
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("🏛️ Structures")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(title)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #383848; border-radius: 5px; padding: 5px;")
        toolbar_layout = QHBoxLayout(toolbar)
        
        browse_btn = QPushButton("📂 Browse Structures")
        browse_btn.setStyleSheet(get_button_style())
        browse_btn.clicked.connect(self._browse_structures)
        toolbar_layout.addWidget(browse_btn)
        
        create_btn = QPushButton("✨ Create Structure")
        create_btn.setStyleSheet(get_button_style(accent=True))
        toolbar_layout.addWidget(create_btn)
        
        import_btn = QPushButton("📥 Import from Game")
        import_btn.setStyleSheet(get_button_style())
        toolbar_layout.addWidget(import_btn)
        
        toolbar_layout.addStretch()
        layout.addWidget(toolbar)
        
        # Tree
        self.structure_tree = QTreeWidget()
        self.structure_tree.setHeaderLabels(["Structure Name", "Type"])
        self.structure_tree.setStyleSheet(get_tree_style())
        layout.addWidget(self.structure_tree)
        
        if not self.project or not self.project.is_loaded:
            info = QLabel("⚠️ No mod loaded. Create or open a mod to edit structures.")
            info.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info)
        else:
            self._load_structures()
    
    def _load_structures(self):
        """Load structures from project."""
        self.structure_tree.clear()
        
        struct_files = [f for f in self.project.list_files() if "structures" in f and f.endswith('.xml')]
        
        if not struct_files:
            item = QTreeWidgetItem(self.structure_tree)
            item.setText(0, "No structures yet - Browse game or create new structures")
            item.setForeground(0, QColor("#9090a0"))
            self.structure_tree.addTopLevelItem(item)
            return
        
        for struct_file in struct_files:
            item = QTreeWidgetItem(self.structure_tree)
            item.setText(0, Path(struct_file).stem)
            item.setText(1, "Unknown")
            item.setData(0, Qt.ItemDataRole.UserRole, struct_file)
            self.structure_tree.addTopLevelItem(item)
    
    def _browse_structures(self):
        """Browse structures from game data."""
        if not self.asset_source:
            QMessageBox.warning(self, "No Game Data", "Please set the game data folder first.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Browse Structures")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Tree
        struct_tree = QTreeWidget()
        struct_tree.setHeaderLabels(["Structure Name"])
        struct_tree.setStyleSheet(get_tree_style())
        struct_tree.itemDoubleClicked.connect(lambda: self._import_game_struct(struct_tree, dialog))
        layout.addWidget(struct_tree)
        
        # Populate with structures
        try:
            entries = self.asset_source.list_dir("simulation/templates/structures")
            for entry in entries:
                if entry.type == "file" and entry.name.endswith('.xml'):
                    item = QTreeWidgetItem(struct_tree)
                    item.setText(0, entry.name)
                    item.setData(0, Qt.ItemDataRole.UserRole, entry.rel_path)
                    struct_tree.addTopLevelItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load structures: {e}")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 Import Selected")
        import_btn.setStyleSheet(get_button_style(accent=True))
        import_btn.clicked.connect(lambda: self._import_game_struct(struct_tree, dialog))
        button_layout.addWidget(import_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(get_button_style())
        close_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _import_game_struct(self, tree: QTreeWidget, dialog: QDialog):
        """Import structure from game data."""
        selected = tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a structure first.")
            return
        
        if not self.project or not self.project.is_loaded:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return
        
        item = selected[0]
        rel_path = item.data(0, Qt.ItemDataRole.UserRole)
        
        try:
            if self.asset_source:
                content = self.asset_source.read_text(rel_path)
                if content is not None:
                    self.project.add_file(content, rel_path)
                    self.project.save()
                    self._load_structures()
                    QMessageBox.information(self, "Success", f"Structure imported successfully!")
                    dialog.accept()
                else:
                    QMessageBox.warning(self, "Error", "Could not read structure content.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import structure: {e}")


class AurasTab(QWidget):
    """Auras editor tab."""
    
    def __init__(self, project: Optional[ModProject], asset_source: Optional[AssetSource]):
        super().__init__()
        self.project = project
        self.asset_source = asset_source
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("✨ Auras")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(title)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #383848; border-radius: 5px; padding: 5px;")
        toolbar_layout = QHBoxLayout(toolbar)
        
        browse_btn = QPushButton("📂 Browse Auras")
        browse_btn.setStyleSheet(get_button_style())
        browse_btn.clicked.connect(self._browse_auras)
        toolbar_layout.addWidget(browse_btn)
        
        create_btn = QPushButton("✨ Create Aura")
        create_btn.setStyleSheet(get_button_style(accent=True))
        toolbar_layout.addWidget(create_btn)
        
        import_btn = QPushButton("📥 Import from Game")
        import_btn.setStyleSheet(get_button_style())
        toolbar_layout.addWidget(import_btn)
        
        toolbar_layout.addStretch()
        layout.addWidget(toolbar)
        
        # Tree
        self.aura_tree = QTreeWidget()
        self.aura_tree.setHeaderLabels(["Aura Name", "Type"])
        self.aura_tree.setStyleSheet(get_tree_style())
        layout.addWidget(self.aura_tree)
        
        if not self.project or not self.project.is_loaded:
            info = QLabel("⚠️ No mod loaded. Create or open a mod to edit auras.")
            info.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info)
        else:
            self._load_auras()
    
    def _load_auras(self):
        """Load auras from project."""
        self.aura_tree.clear()
        
        aura_files = [f for f in self.project.list_files() if "auras" in f and f.endswith('.xml')]
        
        if not aura_files:
            item = QTreeWidgetItem(self.aura_tree)
            item.setText(0, "No auras yet - Browse game or create new auras")
            item.setForeground(0, QColor("#9090a0"))
            self.aura_tree.addTopLevelItem(item)
            return
        
        for aura_file in aura_files:
            item = QTreeWidgetItem(self.aura_tree)
            item.setText(0, Path(aura_file).stem)
            item.setText(1, "Unknown")
            item.setData(0, Qt.ItemDataRole.UserRole, aura_file)
            self.aura_tree.addTopLevelItem(item)
    
    def _browse_auras(self):
        """Browse auras from game data."""
        if not self.asset_source:
            QMessageBox.warning(self, "No Game Data", "Please set the game data folder first.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Browse Auras")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Tree
        aura_tree = QTreeWidget()
        aura_tree.setHeaderLabels(["Aura Name"])
        aura_tree.setStyleSheet(get_tree_style())
        aura_tree.itemDoubleClicked.connect(lambda: self._import_game_aura(aura_tree, dialog))
        layout.addWidget(aura_tree)
        
        # Populate with auras
        try:
            entries = self.asset_source.list_dir("simulation/data/auras")
            for entry in entries:
                if entry.type == "file" and entry.name.endswith('.xml'):
                    item = QTreeWidgetItem(aura_tree)
                    item.setText(0, entry.name)
                    item.setData(0, Qt.ItemDataRole.UserRole, entry.rel_path)
                    aura_tree.addTopLevelItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load auras: {e}")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 Import Selected")
        import_btn.setStyleSheet(get_button_style(accent=True))
        import_btn.clicked.connect(lambda: self._import_game_aura(aura_tree, dialog))
        button_layout.addWidget(import_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(get_button_style())
        close_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _import_game_aura(self, tree: QTreeWidget, dialog: QDialog):
        """Import aura from game data."""
        selected = tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select an aura first.")
            return
        
        if not self.project or not self.project.is_loaded:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return
        
        item = selected[0]
        rel_path = item.data(0, Qt.ItemDataRole.UserRole)
        
        try:
            if self.asset_source:
                content = self.asset_source.read_text(rel_path)
                if content is not None:
                    self.project.add_file(content, rel_path)
                    self.project.save()
                    self._load_auras()
                    QMessageBox.information(self, "Success", f"Aura imported successfully!")
                    dialog.accept()
                else:
                    QMessageBox.warning(self, "Error", "Could not read aura content.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import aura: {e}")
