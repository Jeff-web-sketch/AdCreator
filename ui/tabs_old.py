"""Tab widgets for the main application."""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QFrame, QTextEdit, QLineEdit,
    QFileDialog, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
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
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #383848; border-radius: 5px; padding: 5px;")
        toolbar_layout = QHBoxLayout(toolbar)
        
        browse_btn = QPushButton("📂 Browse Folder")
        browse_btn.setStyleSheet(get_button_style())
        toolbar_layout.addWidget(browse_btn)
        
        import_btn = QPushButton("📥 Import Selected")
        import_btn.setStyleSheet(get_button_style())
        toolbar_layout.addWidget(import_btn)
        
        toolbar_layout.addStretch()
        layout.addWidget(toolbar)
        
        # Tree
        self.asset_tree = QTreeWidget()
        self.asset_tree.setHeaderLabels(["Name", "Type", "Size"])
        self.asset_tree.setStyleSheet(get_tree_style())
        layout.addWidget(self.asset_tree)
        
        if not self.asset_source:
            info = QLabel("⚠️ No game data loaded. Set game data folder in File menu.")
            info.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info)


class UnitsTab(QWidget):
    """Units editor tab."""
    
    def __init__(self, project: Optional[ModProject], asset_source: Optional[AssetSource]):
        super().__init__()
        self.project = project
        self.asset_source = asset_source
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
        
        # Tree
        self.unit_tree = QTreeWidget()
        self.unit_tree.setHeaderLabels(["Unit Name", "Parent", "Civ"])
        self.unit_tree.setStyleSheet(get_tree_style())
        layout.addWidget(self.unit_tree)
        
        if not self.project or not self.project.is_loaded:
            info = QLabel("⚠️ No mod loaded. Create or open a mod to edit units.")
            info.setStyleSheet("color: #fbbf24; font-size: 14px; padding: 20px;")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info)


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
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("e.g., my_spearman")
        name_input.setStyleSheet(get_input_style())
        form_layout.addRow("Unit Name:", name_input)
        
        parent_layout = QHBoxLayout()
        parent_input = QLineEdit()
        parent_input.setPlaceholderText("template_unit_infantry_melee_spearman")
        parent_input.setStyleSheet(get_input_style())
        parent_layout.addWidget(parent_input)
        
        browse_btn = QPushButton("🔍 Browse")
        browse_btn.setStyleSheet(get_button_style())
        browse_btn.clicked.connect(self._browse_parent_template)
        parent_layout.addWidget(browse_btn)
        
        form_layout.addRow("Parent Template:", parent_layout)
        
        civ_input = QLineEdit()
        civ_input.setPlaceholderText("gaia")
        civ_input.setStyleSheet(get_input_style())
        form_layout.addRow("Civilization:", civ_input)
        
        display_input = QLineEdit()
        display_input.setPlaceholderText("My Spearman")
        display_input.setStyleSheet(get_input_style())
        form_layout.addRow("Display Name:", display_input)
        
        layout.addWidget(form_frame)
        
        # Create button
        create_btn = QPushButton("✨ Create Unit")
        create_btn.setStyleSheet(get_button_style(accent=True))
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
            # Find the parent input field and set its value
            for child in self.findChildren(QLineEdit):
                if child.placeholderText() == "template_unit_infantry_melee_spearman":
                    child.setText(selected[0].text(0))
                    break
            dialog.accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a template first.")


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
            layout.addWidget(save_btn)


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
            layout.addWidget(build_btn)


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
            relative_path = file_path.relative_to(self.project.mod_dir)
            item = QTreeWidgetItem(self.structure_tree)
            item.setText(0, str(relative_path))
            item.setText(1, "File" if file_path.is_file() else "Directory")
