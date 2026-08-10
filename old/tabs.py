"""Tab widgets for the main application."""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict
from collections import Counter

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QFrame, QTextEdit, QLineEdit,
    QFileDialog, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QSplitter, QScrollArea, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont

from assets import AssetSource, AssetEntry
from mod import ModProject
from styles import get_button_style, get_tree_style, get_line_edit_style, get_spin_box_style, get_text_edit_style


class PieChartWidget(QWidget):
    """Custom pie chart widget for displaying statistics."""
    
    def __init__(self, data: Dict[str, int], title: str = ""):
        super().__init__()
        self.data = data
        self.title = title
        self.setMinimumSize(300, 300)
        self.colors = [
            QColor("#7b5eff"),  # Purple
            QColor("#5eff7b"),  # Green
            QColor("#ff5e7b"),  # Red
            QColor("#ff7b5e"),  # Orange
            QColor("#5e7bff"),  # Blue
            QColor("#7bff5e"),  # Light Green
            QColor("#ff5eff"),  # Pink
            QColor("#5effff"),  # Cyan
        ]
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate total
        total = sum(self.data.values())
        if total == 0:
            self._draw_empty_chart(painter)
            return
        
        # Draw pie chart
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(center_x, center_y) - 60
        
        start_angle = 0
        color_index = 0
        
        for label, value in self.data.items():
            if value == 0:
                continue
            
            slice_angle = (value / total) * 360
            
            # Draw slice
            painter.setBrush(QBrush(self.colors[color_index % len(self.colors)]))
            painter.setPen(QPen(QColor("#1a1a2a"), 2))
            painter.drawPie(center_x - radius, center_y - radius, 
                           radius * 2, radius * 2, 
                           int(start_angle * 16), int(slice_angle * 16))
            
            start_angle += slice_angle
            color_index += 1
        
        # Draw title
        if self.title:
            painter.setPen(QColor("#ffffff"))
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.title)
        
        # Draw legend
        self._draw_legend(painter, center_x, center_y + radius + 30)
    
    def _draw_empty_chart(self, painter):
        """Draw empty state chart."""
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(center_x, center_y) - 60
        
        painter.setBrush(QBrush(QColor("#2d2d3d")))
        painter.setPen(QPen(QColor("#4a4a6a"), 2))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        painter.setPen(QColor("#707080"))
        painter.setFont(QFont("Arial", 11))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No data available")
    
    def _draw_legend(self, painter, x, y):
        """Draw legend for the pie chart."""
        color_index = 0
        legend_width = 200
        legend_height = 20
        items_per_row = 2
        
        for label, value in self.data.items():
            if value == 0:
                continue
            
            row = color_index // items_per_row
            col = color_index % items_per_row
            
            legend_x = x - legend_width // 2 + col * (legend_width // items_per_row)
            legend_y = y + row * legend_height
            
            # Draw color box
            painter.setBrush(QBrush(self.colors[color_index % len(self.colors)]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(legend_x, legend_y, 15, 15)
            
            # Draw label
            painter.setPen(QColor("#c0c0d0"))
            painter.setFont(QFont("Arial", 9))
            label_text = f"{label}: {value}"
            painter.drawText(legend_x + 20, legend_y + 12, label_text)
            
            color_index += 1
    
    def update_data(self, data: Dict[str, int]):
        """Update chart data."""
        self.data = data
        self.update()


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
    
    def get_help_text(self) -> str:
        """Override to provide context-specific help."""
        return "No specific help available for this tab."


class OverviewTab(BaseTab):
    """Overview tab showing project statistics and quick actions."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Welcome section
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d2d3d, stop:1 #383848);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_frame)
        
        welcome_title = QLabel("👋 Welcome to Your Project Dashboard")
        welcome_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #7b5eff;")
        welcome_layout.addWidget(welcome_title)
        
        welcome_desc = QLabel("View your project statistics and perform quick actions from here.")
        welcome_desc.setStyleSheet("color: #c0c0d0; font-size: 14px;")
        welcome_layout.addWidget(welcome_desc)
        
        layout.addWidget(welcome_frame)
        
        # Stats grid
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)
        
        # Stat cards
        stat_cards = [
            ("📁", "Project Name", "project_name_label"),
            ("📄", "Total Files", "file_count_label"),
            ("💾", "Project Size", "project_size_label")
        ]
        
        for icon, title, label_attr in stat_cards:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #1a1a2a;
                    border-radius: 10px;
                    padding: 15px;
                }
            """)
            card_layout = QVBoxLayout(card)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 28px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(icon_label)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("color: #707080; font-size: 12px; font-weight: bold;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(title_label)
            
            value_label = QLabel("—" if label_attr == "project_name_label" else "0")
            value_label.setStyleSheet("color: #7b5eff; font-size: 18px; font-weight: bold;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setWordWrap(True)
            card_layout.addWidget(value_label)
            
            setattr(self, label_attr, value_label)
            stats_layout.addWidget(card)
        
        layout.addWidget(stats_frame)
        
        # Charts section
        charts_frame = QFrame()
        charts_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        charts_layout = QVBoxLayout(charts_frame)
        
        charts_title = QLabel("📊 Content Distribution")
        charts_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        charts_layout.addWidget(charts_title)
        
        # Charts grid
        charts_grid = QHBoxLayout()
        charts_grid.setSpacing(20)
        
        # File type distribution chart
        self.file_type_chart = PieChartWidget({}, "File Types")
        charts_grid.addWidget(self.file_type_chart)
        
        # Unit type distribution chart
        self.unit_type_chart = PieChartWidget({}, "Unit Types")
        charts_grid.addWidget(self.unit_type_chart)
        
        # Structure type distribution chart
        self.structure_type_chart = PieChartWidget({}, "Structure Types")
        charts_grid.addWidget(self.structure_type_chart)
        
        charts_layout.addLayout(charts_grid)
        layout.addWidget(charts_frame)
        
        # Quick actions section
        actions_frame = QFrame()
        actions_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        actions_layout = QVBoxLayout(actions_frame)
        
        actions_title = QLabel("⚡ Quick Actions")
        actions_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        actions_layout.addWidget(actions_title)
        
        # Action buttons grid
        actions_grid = QHBoxLayout()
        actions_grid.setSpacing(15)
        
        action_buttons = [
            ("✨ Create New Mod", "accent", self.main_window.action_new_mod, "Start a fresh mod project"),
            ("📂 Open Existing Mod", "normal", self.main_window.action_open_mod, "Load an existing .adcreator file"),
            ("💾 Save Current Mod", "normal", self.main_window.action_save_mod, "Save your current work"),
            ("🔨 Build .pyromod", "accent", self.main_window.action_build_mod, "Export your mod as .pyromod")
        ]
        
        for text, style, callback, tooltip in action_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(get_button_style(accent=(style == "accent")))
            btn.clicked.connect(callback)
            btn.setToolTip(tooltip)
            btn.setMinimumHeight(45)
            actions_grid.addWidget(btn)
        
        actions_layout.addLayout(actions_grid)
        layout.addWidget(actions_frame)
        
        # Getting started guide
        guide_frame = QFrame()
        guide_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        guide_layout = QVBoxLayout(guide_frame)
        
        guide_title = QLabel("🚀 Getting Started")
        guide_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        guide_layout.addWidget(guide_title)
        
        guide_text = QLabel(
            "1. Create a new mod or open an existing one\n"
            "2. Browse assets from the Assets tab\n"
            "3. Edit units and structures in their respective tabs\n"
            "4. Configure technologies and auras\n"
            "5. Build your mod as a .pyromod file when ready"
        )
        guide_text.setStyleSheet("color: #c0c0d0; font-size: 14px; line-height: 1.6;")
        guide_layout.addWidget(guide_text)
        
        layout.addWidget(guide_frame)
        layout.addStretch()
    
    def refresh(self):
        """Refresh overview with current project data."""
        if self.main_window.project:
            project = self.main_window.project
            self.project_name_label.setText(project.project_name)
            self.file_count_label.setText(str(len(project.files)))
            
            # Calculate approximate size
            total_size = sum(len(f.content) for f in project.files.values())
            if total_size > 1024 * 1024:
                size_str = f"{total_size / (1024 * 1024):.1f} MB"
            elif total_size > 1024:
                size_str = f"{total_size / 1024:.1f} KB"
            else:
                size_str = f"{total_size} B"
            self.project_size_label.setText(size_str)
            
            # Update charts
            self._update_charts(project)
        else:
            self.project_name_label.setText("No project")
            self.file_count_label.setText("0")
            self.project_size_label.setText("0 B")
            
            # Clear charts
            self.file_type_chart.update_data({})
            self.unit_type_chart.update_data({})
            self.structure_type_chart.update_data({})
    
    def _update_charts(self, project: ModProject):
        """Update all charts with project data."""
        # File type distribution
        file_types = Counter()
        unit_types = Counter()
        structure_types = Counter()
        
        for file_path in project.files.keys():
            # Count file types
            if file_path.endswith('.xml'):
                file_types['XML'] += 1
            elif file_path.endswith('.png') or file_path.endswith('.jpg'):
                file_types['Images'] += 1
            elif file_path.endswith('.js'):
                file_types['Scripts'] += 1
            elif file_path.endswith('.json'):
                file_types['JSON'] += 1
            else:
                file_types['Other'] += 1
            
            # Count unit types
            if 'units/' in file_path and file_path.endswith('.xml'):
                unit_type = self._classify_unit_type(file_path)
                unit_types[unit_type] += 1
            
            # Count structure types
            if 'structures/' in file_path and file_path.endswith('.xml'):
                structure_type = self._classify_structure_type(file_path)
                structure_types[structure_type] += 1
        
        # Update charts
        self.file_type_chart.update_data(dict(file_types))
        self.unit_type_chart.update_data(dict(unit_types))
        self.structure_type_chart.update_data(dict(structure_types))
    
    def _classify_unit_type(self, file_path: str) -> str:
        """Classify unit type based on file path."""
        if 'infantry' in file_path.lower():
            return 'Infantry'
        elif 'cavalry' in file_path.lower():
            return 'Cavalry'
        elif 'champion' in file_path.lower():
            return 'Champion'
        elif 'hero' in file_path.lower():
            return 'Hero'
        elif 'support' in file_path.lower():
            return 'Support'
        elif 'siege' in file_path.lower():
            return 'Siege'
        elif ' naval' in file_path.lower():
            return 'Naval'
        else:
            return 'Other'
    
    def _classify_structure_type(self, file_path: str) -> str:
        """Classify structure type based on file path."""
        if 'civil' in file_path.lower() or 'house' in file_path.lower():
            return 'Civil'
        elif 'military' in file_path.lower() or 'barracks' in file_path.lower():
            return 'Military'
        elif 'economic' in file_path.lower() or 'farm' in file_path.lower():
            return 'Economic'
        elif 'defensive' in file_path.lower() or 'tower' in file_path.lower() or 'wall' in file_path.lower():
            return 'Defensive'
        elif 'wonder' in file_path.lower():
            return 'Wonder'
        else:
            return 'Other'
    
    def get_help_text(self) -> str:
        """Provide help for the Overview tab."""
        return (
            "Overview Tab Help:\n\n"
            "This tab shows your project statistics and provides quick actions.\n\n"
            "📊 Statistics:\n"
            "• Project Name: Current mod name\n"
            "• Total Files: Number of files in your mod\n"
            "• Project Size: Total size of all files\n\n"
            "📈 Charts:\n"
            "• File Types: Distribution of file types (XML, Images, Scripts, etc.)\n"
            "• Unit Types: Distribution of unit categories (Infantry, Cavalry, etc.)\n"
            "• Structure Types: Distribution of building categories\n\n"
            "⚡ Quick Actions:\n"
            "• Create New Mod: Start a fresh project\n"
            "• Open Existing Mod: Load a saved .adcreator file\n"
            "• Save Current Mod: Save your current work\n"
            "• Build .pyromod: Export your mod for use in 0 A.D.\n\n"
            "🚀 Getting Started:\n"
            "Follow the numbered guide to begin creating your mod!"
        )


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
    """Comprehensive units tab for viewing and editing unit templates."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("⚔️ Units Editor")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(get_button_style())
        refresh_btn.clicked.connect(self._refresh_units)
        toolbar.addWidget(refresh_btn)
        
        toolbar.addStretch()
        
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
        
        # Comprehensive editor panel with tabs
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
        
        editor_title = QLabel("Unit Properties Editor")
        editor_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        editor_layout.addWidget(editor_title)
        
        # Create tab widget for different property categories
        from PyQt6.QtWidgets import QTabWidget
        self.property_tabs = QTabWidget()
        self.property_tabs.setStyleSheet("""
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
            QTabBar::tab:hover:!selected {
                background-color: #484858;
                border-color: #7b5eff;
            }
        """)
        
        # Create property category tabs
        self._create_identity_tab()
        self._create_cost_tab()
        self._create_health_tab()
        self._create_attack_tab()
        self._create_defense_tab()
        self._create_movement_tab()
        self._create_vision_tab()
        self._create_gather_tab()
        self._create_builder_tab()
        self._create_garrison_tab()
        self._create_promotion_tab()
        self._create_loot_tab()
        self._create_selection_tab()
        self._create_sound_tab()
        self._create_actor_tab()
        
        editor_layout.addWidget(self.property_tabs)
        
        # Save buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save All Changes")
        save_btn.setStyleSheet(get_button_style(accent=True))
        save_btn.clicked.connect(self._save_unit_properties)
        save_btn.setToolTip("Save all property changes to the unit")
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("🔄 Reset to Original")
        reset_btn.setStyleSheet(get_button_style())
        reset_btn.clicked.connect(self._reset_properties)
        reset_btn.setToolTip("Reset all fields to the original XML values")
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        editor_layout.addLayout(button_layout)
        
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
        splitter.setStretchFactor(1, 3)
        
        layout.addWidget(splitter)
        
        # Track selected unit
        self.selected_unit_path = None
        self.selected_unit_xml = None
    
    def _create_identity_tab(self):
        """Create identity properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("🏷️ Identity Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        # Form fields
        self.civ_input = self._create_form_field("Civilization:", "generic", "e.g., athen, spart, rome")
        form_layout.addLayout(self.civ_input['layout'])
        
        self.generic_input = self._create_form_field("Generic Name:", "Unit", "e.g., Infantry, Cavalry")
        form_layout.addLayout(self.generic_input['layout'])
        
        self.specific_input = self._create_form_field("Specific Name:", "Unit Name", "e.g., Hoplite, Citizen")
        form_layout.addLayout(self.specific_input['layout'])
        
        self.rank_input = self._create_combo_field("Rank:", ["Basic", "Advanced", "Elite"], "Basic", "Unit rank/cost tier")
        form_layout.addLayout(self.rank_input['layout'])
        
        self.classes_input = self._create_form_field("Classes:", "", "e.g., Infantry Melee Citizen")
        form_layout.addLayout(self.classes_input['layout'])
        
        self.visible_classes_input = self._create_form_field("Visible Classes:", "", "e.g., Infantry, Melee")
        form_layout.addLayout(self.visible_classes_input['layout'])
        
        self.icon_input = self._create_form_field("Icon:", "", "e.g., units/athen_infantry_spearman.png")
        form_layout.addLayout(self.icon_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "🏷️ Identity")
    
    def _create_cost_tab(self):
        """Create cost properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("💰 Cost Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.build_time_input = self._create_number_field("Build Time:", 10, "Time to train/build in seconds")
        form_layout.addLayout(self.build_time_input['layout'])
        
        self.food_cost_input = self._create_number_field("Food Cost:", 0, "Food resource cost")
        form_layout.addLayout(self.food_cost_input['layout'])
        
        self.wood_cost_input = self._create_number_field("Wood Cost:", 0, "Wood resource cost")
        form_layout.addLayout(self.wood_cost_input['layout'])
        
        self.stone_cost_input = self._create_number_field("Stone Cost:", 0, "Stone resource cost")
        form_layout.addLayout(self.stone_cost_input['layout'])
        
        self.metal_cost_input = self._create_number_field("Metal Cost:", 0, "Metal resource cost")
        form_layout.addLayout(self.metal_cost_input['layout'])
        
        self.population_cost_input = self._create_number_field("Population Cost:", 1, "Population slots used")
        form_layout.addLayout(self.population_cost_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "💰 Cost")
    
    def _create_health_tab(self):
        """Create health properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("❤️ Health Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.max_health_input = self._create_number_field("Max Health:", 100, "Maximum hit points")
        form_layout.addLayout(self.max_health_input['layout'])
        
        self.regen_rate_input = self._create_number_field("Regen Rate:", 0, "Health regeneration per second")
        form_layout.addLayout(self.regen_rate_input['layout'])
        
        self.regen_delay_input = self._create_number_field("Regen Delay:", 0, "Seconds before regeneration starts")
        form_layout.addLayout(self.regen_delay_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "❤️ Health")
    
    def _create_attack_tab(self):
        """Create attack properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("⚔️ Attack Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        # Melee attack
        melee_title = QLabel("🗡️ Melee Attack")
        melee_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #5eff7b;")
        form_layout.addWidget(melee_title)
        
        self.melee_hack_input = self._create_number_field("Hack Damage:", 0, "Hack damage for melee")
        form_layout.addLayout(self.melee_hack_input['layout'])
        
        self.melee_pierce_input = self._create_number_field("Pierce Damage:", 0, "Pierce damage for melee")
        form_layout.addLayout(self.melee_pierce_input['layout'])
        
        self.melee_crush_input = self._create_number_field("Crush Damage:", 0, "Crush damage for melee")
        form_layout.addLayout(self.melee_crush_input['layout'])
        
        self.melee_range_input = self._create_number_field("Melee Range:", 3.0, "Range for melee attack")
        form_layout.addLayout(self.melee_range_input['layout'])
        
        # Ranged attack
        form_layout.addSpacing(10)
        ranged_title = QLabel("🏹 Ranged Attack")
        ranged_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #5eff7b;")
        form_layout.addWidget(ranged_title)
        
        self.ranged_hack_input = self._create_number_field("Hack Damage:", 0, "Hack damage for ranged")
        form_layout.addLayout(self.ranged_hack_input['layout'])
        
        self.ranged_pierce_input = self._create_number_field("Pierce Damage:", 0, "Pierce damage for ranged")
        form_layout.addLayout(self.ranged_pierce_input['layout'])
        
        self.ranged_crush_input = self._create_number_field("Crush Damage:", 0, "Crush damage for ranged")
        form_layout.addLayout(self.ranged_crush_input['layout'])
        
        self.ranged_range_input = self._create_number_field("Ranged Range:", 0, "Range for ranged attack")
        form_layout.addLayout(self.ranged_range_input['layout'])
        
        self.ranged_prepare_time_input = self._create_number_field("Prepare Time:", 1.0, "Time to prepare ranged attack")
        form_layout.addLayout(self.ranged_prepare_time_input['layout'])
        
        # Capture attack
        form_layout.addSpacing(10)
        capture_title = QLabel("🏰 Capture Attack")
        capture_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #5eff7b;")
        form_layout.addWidget(capture_title)
        
        self.capture_strength_input = self._create_number_field("Capture Strength:", 1, "Capture attack strength")
        form_layout.addLayout(self.capture_strength_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "⚔️ Attack")
    
    def _create_defense_tab(self):
        """Create defense properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("🛡️ Defense Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.hack_resistance_input = self._create_number_field("Hack Resistance:", 5, "Resistance to hack damage")
        form_layout.addLayout(self.hack_resistance_input['layout'])
        
        self.pierce_resistance_input = self._create_number_field("Pierce Resistance:", 5, "Resistance to pierce damage")
        form_layout.addLayout(self.pierce_resistance_input['layout'])
        
        self.crush_resistance_input = self._create_number_field("Crush Resistance:", 5, "Resistance to crush damage")
        form_layout.addLayout(self.crush_resistance_input['layout'])
        
        form_layout.addSpacing(10)
        
        self.capture_resistance_input = self._create_number_field("Capture Resistance:", 0, "Resistance to capture")
        form_layout.addLayout(self.capture_resistance_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "🛡️ Defense")
    
    def _create_movement_tab(self):
        """Create movement properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("🏃 Movement Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.walk_speed_input = self._create_number_field("Walk Speed:", 1.0, "Normal walking speed")
        form_layout.addLayout(self.walk_speed_input['layout'])
        
        self.run_speed_input = self._create_number_field("Run Speed:", 0, "Running speed multiplier")
        form_layout.addLayout(self.run_speed_input['layout'])
        
        self.acceleration_input = self._create_number_field("Acceleration:", 2.0, "Movement acceleration")
        form_layout.addLayout(self.acceleration_input['layout'])
        
        self.passability_class_input = self._create_combo_field("Passability:", ["default", "ship", "large"], "default", "Terrain passability class")
        form_layout.addLayout(self.passability_class_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "🏃 Movement")
    
    def _create_vision_tab(self):
        """Create vision properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("👁️ Vision Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.vision_range_input = self._create_number_field("Vision Range:", 32, "Distance unit can see")
        form_layout.addLayout(self.vision_range_input['layout'])
        
        self.retain_in_fog_checkbox = self._create_checkbox_field("Retain in Fog", False, "Unit remains visible in fog of war")
        form_layout.addLayout(self.retain_in_fog_checkbox['layout'])
        
        self.always_visible_checkbox = self._create_checkbox_field("Always Visible", False, "Unit is always visible to all players")
        form_layout.addLayout(self.always_visible_checkbox['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "👁️ Vision")
    
    def _create_gather_tab(self):
        """Create resource gathering properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("🌾 Resource Gathering")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.can_gather_checkbox = self._create_checkbox_field("Can Gather Resources", False, "Unit can gather resources")
        form_layout.addLayout(self.can_gather_checkbox['layout'])
        
        self.food_rate_input = self._create_number_field("Food Rate:", 1.0, "Food gathering rate")
        form_layout.addLayout(self.food_rate_input['layout'])
        
        self.wood_rate_input = self._create_number_field("Wood Rate:", 1.0, "Wood gathering rate")
        form_layout.addLayout(self.wood_rate_input['layout'])
        
        self.stone_rate_input = self._create_number_field("Stone Rate:", 1.0, "Stone gathering rate")
        form_layout.addLayout(self.stone_rate_input['layout'])
        
        self.metal_rate_input = self._create_number_field("Metal Rate:", 1.0, "Metal gathering rate")
        form_layout.addLayout(self.metal_rate_input['layout'])
        
        self.gather_capacity_input = self._create_number_field("Gather Capacity:", 20, "Max resources unit can carry")
        form_layout.addLayout(self.gather_capacity_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "🌾 Gather")
    
    def _create_builder_tab(self):
        """Create builder properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("🔨 Builder Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.can_build_checkbox = self._create_checkbox_field("Can Build", False, "Unit can construct buildings")
        form_layout.addLayout(self.can_build_checkbox['layout'])
        
        self.build_rate_input = self._create_number_field("Build Rate:", 1.0, "Construction speed multiplier")
        form_layout.addLayout(self.build_rate_input['layout'])
        
        self.buildable_entities_input = self._create_form_field("Buildable Entities:", "", "e.g., structures/{civ}_house, structures/{civ}_barracks")
        form_layout.addLayout(self.buildable_entities_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "🔨 Builder")
    
    def _create_garrison_tab(self):
        """Create garrison properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("🏰 Garrison Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.garrison_capacity_input = self._create_number_field("Garrison Capacity:", 0, "Number of units that can garrison")
        form_layout.addLayout(self.garrison_capacity_input['layout'])
        
        self.garrison_size_input = self._create_number_field("Garrison Size:", 10, "Size of garrison slot")
        form_layout.addLayout(self.garrison_size_input['layout'])
        
        self.allow_garrisoning_checkbox = self._create_checkbox_field("Allow Garrisoning", False, "Units can garrison in this structure")
        form_layout.addLayout(self.allow_garrisoning_checkbox['layout'])
        
        self.list_garrisoners_checkbox = self._create_checkbox_field("List Garrisoners", False, "Show garrisoned units in tooltip")
        form_layout.addLayout(self.list_garrisoners_checkbox['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "🏰 Garrison")
    
    def _create_promotion_tab(self):
        """Create promotion properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("⭐ Promotion Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.required_xp_input = self._create_number_field("Required XP:", 1000, "XP needed for promotion")
        form_layout.addLayout(self.required_xp_input['layout'])
        
        self.promote_to_input = self._create_form_field("Promote To:", "", "e.g., units/{civ}_infantry_spearman_b")
        form_layout.addLayout(self.promote_to_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "⭐ Promotion")
    
    def _create_loot_tab(self):
        """Create loot properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("💎 Loot Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.xp_loot_input = self._create_number_field("XP Loot:", 10, "XP given when killed")
        form_layout.addLayout(self.xp_loot_input['layout'])
        
        self.food_loot_input = self._create_number_field("Food Loot:", 0, "Food resources given when killed")
        form_layout.addLayout(self.food_loot_input['layout'])
        
        self.wood_loot_input = self._create_number_field("Wood Loot:", 0, "Wood resources given when killed")
        form_layout.addLayout(self.wood_loot_input['layout'])
        
        self.stone_loot_input = self._create_number_field("Stone Loot:", 0, "Stone resources given when killed")
        form_layout.addLayout(self.stone_loot_input['layout'])
        
        self.metal_loot_input = self._create_number_field("Metal Loot:", 0, "Metal resources given when killed")
        form_layout.addLayout(self.metal_loot_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "💎 Loot")
    
    def _create_selection_tab(self):
        """Create selection properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("🎯 Selection Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.selection_radius_input = self._create_number_field("Selection Radius:", 1.0, "Radius for selection circle")
        form_layout.addLayout(self.selection_radius_input['layout'])
        
        self.selection_shape_input = self._create_combo_field("Selection Shape:", ["circle", "square"], "circle", "Shape of selection area")
        form_layout.addLayout(self.selection_shape_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "🎯 Selection")
    
    def _create_sound_tab(self):
        """Create sound properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("🔊 Sound Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.sound_group_input = self._create_form_field("Sound Group:", "", "e.g., voice/{civ}/citizen_male")
        form_layout.addLayout(self.sound_group_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "🔊 Sound")
    
    def _create_actor_tab(self):
        """Create visual actor properties tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("🎭 Visual Actor")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.actor_input = self._create_form_field("Actor:", "", "e.g., units/hellenes/infantry_spearman.xml")
        form_layout.addLayout(self.actor_input['layout'])
        
        self.foundation_actor_input = self._create_form_field("Foundation Actor:", "", "Actor for construction state")
        form_layout.addLayout(self.foundation_actor_input['layout'])
        
        self.silhouette_input = self._create_form_field("Silhouette:", "", "e.g., units/hellenes/infantry_spearman.png")
        form_layout.addLayout(self.silhouette_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.property_tabs.addTab(tab, "🎭 Actor")
    
    # Helper methods for form field creation
    def _create_form_field(self, label: str, default: str, tooltip: str) -> dict:
        """Create a text input form field."""
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        label_widget.setFixedWidth(140)
        label_widget.setToolTip(tooltip)
        layout.addWidget(label_widget)
        
        input_widget = QLineEdit()
        input_widget.setPlaceholderText(default)
        input_widget.setStyleSheet(get_line_edit_style())
        input_widget.setToolTip(tooltip)
        layout.addWidget(input_widget)
        
        layout.addStretch()
        
        return {'layout': layout, 'input': input_widget}
    
    # Helper methods for form fields
    def _create_number_field(self, label: str, default: float, tooltip: str) -> dict:
        """Create a number input field."""
        from PyQt6.QtWidgets import QDoubleSpinBox
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        label_widget.setFixedWidth(140)
        label_widget.setToolTip(tooltip)
        layout.addWidget(label_widget)
        
        input_widget = QDoubleSpinBox()
        input_widget.setRange(0, 10000)
        input_widget.setValue(default)
        input_widget.setSingleStep(0.1)
        input_widget.setStyleSheet(get_spin_box_style())
        input_widget.setToolTip(tooltip)
        layout.addWidget(input_widget)
        
        layout.addStretch()
        
        return {'layout': layout, 'input': input_widget}
    
    def _create_combo_field(self, label: str, options: list, default: str, tooltip: str) -> dict:
        """Create a combo box field."""
        from PyQt6.QtWidgets import QComboBox
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        label_widget.setFixedWidth(140)
        label_widget.setToolTip(tooltip)
        layout.addWidget(label_widget)
        
        input_widget = QComboBox()
        input_widget.addItems(options)
        input_widget.setCurrentText(default)
        input_widget.setStyleSheet(get_spin_box_style())
        input_widget.setToolTip(tooltip)
        layout.addWidget(input_widget)
        
        layout.addStretch()
        
        return {'layout': layout, 'input': input_widget}
    
    def _create_checkbox_field(self, label: str, default: bool, tooltip: str) -> dict:
        """Create a checkbox field."""
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        label_widget.setFixedWidth(140)
        label_widget.setToolTip(tooltip)
        layout.addWidget(label_widget)
        
        input_widget = QCheckBox("Enabled")
        input_widget.setChecked(default)
        input_widget.setStyleSheet("color: #c0c0d0; font-size: 13px;")
        input_widget.setToolTip(tooltip)
        layout.addWidget(input_widget)
        
        layout.addStretch()
        
        return {'layout': layout, 'input': input_widget}
    
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
    
    # Helper methods for form fields
    def _create_number_field(self, label: str, default: float, tooltip: str) -> dict:
        """Create a number input field."""
        from PyQt6.QtWidgets import QDoubleSpinBox
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        label_widget.setFixedWidth(140)
        label_widget.setToolTip(tooltip)
        layout.addWidget(label_widget)
        
        input_widget = QDoubleSpinBox()
        input_widget.setRange(0, 10000)
        input_widget.setValue(default)
        input_widget.setSingleStep(0.1)
        input_widget.setStyleSheet(get_spin_box_style())
        input_widget.setToolTip(tooltip)
        layout.addWidget(input_widget)
        
        layout.addStretch()
        
        return {'layout': layout, 'input': input_widget}
    
    def _create_combo_field(self, label: str, options: list, default: str, tooltip: str) -> dict:
        """Create a combo box field."""
        from PyQt6.QtWidgets import QComboBox
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        label_widget.setFixedWidth(140)
        label_widget.setToolTip(tooltip)
        layout.addWidget(label_widget)
        
        input_widget = QComboBox()
        input_widget.addItems(options)
        input_widget.setCurrentText(default)
        input_widget.setStyleSheet(get_spin_box_style())
        input_widget.setToolTip(tooltip)
        layout.addWidget(input_widget)
        
        layout.addStretch()
        
        return {'layout': layout, 'input': input_widget}
    
    def _create_checkbox_field(self, label: str, default: bool, tooltip: str) -> dict:
        """Create a checkbox field."""
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        label_widget.setFixedWidth(140)
        label_widget.setToolTip(tooltip)
        layout.addWidget(label_widget)
        
        input_widget = QCheckBox("Enabled")
        input_widget.setChecked(default)
        input_widget.setStyleSheet("color: #c0c0d0; font-size: 13px;")
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
                self._populate_all_properties(mod_file.content)
    
    def _populate_all_properties(self, xml_content: str):
        """Populate all property fields from XML content."""
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
                self.visible_classes_input['input'].setText(identity.get("VisibleClasses", ""))
                self.icon_input['input'].setText(identity.get("Icon", ""))
            
            # Cost
            cost = root.find(".//Cost")
            if cost is not None:
                self.build_time_input['input'].setValue(float(cost.get("BuildTime", "10")))
                resources = cost.find("Resources")
                if resources is not None:
                    self.food_cost_input['input'].setValue(float(resources.get("food", "0")))
                    self.wood_cost_input['input'].setValue(float(resources.get("wood", "0")))
                    self.stone_cost_input['input'].setValue(float(resources.get("stone", "0")))
                    self.metal_cost_input['input'].setValue(float(resources.get("metal", "0")))
                self.population_cost_input['input'].setValue(float(cost.get("Population", "1")))
            
            # Health
            health = root.find(".//Health")
            if health is not None:
                self.max_health_input['input'].setValue(float(health.get("Max", "100")))
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
                
                capture = attack.find("Capture")
                if capture is not None:
                    self.capture_strength_input['input'].setValue(float(capture.get("Strength", "1")))
            
            # Defense
            resistance = root.find(".//Resistance")
            if resistance is not None:
                self.hack_resistance_input['input'].setValue(float(resistance.get("Hack", "5")))
                self.pierce_resistance_input['input'].setValue(float(resistance.get("Pierce", "5")))
                self.crush_resistance_input['input'].setValue(float(resistance.get("Crush", "5")))
            
            capture_resistance = root.find(".//CaptureResistance")
            if capture_resistance is not None:
                self.capture_resistance_input['input'].setValue(float(capture_resistance.get("Capture", "0")))
            
            # Movement
            unit_motion = root.find(".//UnitMotion")
            if unit_motion is not None:
                self.walk_speed_input['input'].setValue(float(unit_motion.get("WalkSpeed", "1.0")))
                self.run_speed_input['input'].setValue(float(unit_motion.get("Run", "0")))
                self.acceleration_input['input'].setValue(float(unit_motion.get("Acceleration", "2.0")))
                self.passability_class_input['input'].setCurrentText(unit_motion.get("PassabilityClass", "default"))
            
            # Vision
            vision = root.find(".//Vision")
            if vision is not None:
                self.vision_range_input['input'].setValue(float(vision.get("Range", "32")))
                self.retain_in_fog_checkbox['input'].setChecked(vision.get("RetainInFog", "false").lower() == "true")
                self.always_visible_checkbox['input'].setChecked(vision.get("AlwaysVisible", "false").lower() == "true")
            
            # Resource Gathering
            resource_gatherer = root.find(".//ResourceGatherer")
            if resource_gatherer is not None:
                self.can_gather_checkbox['input'].setChecked(True)
                rates = resource_gatherer.get("Rates", "")
                if rates:
                    self.food_rate_input['input'].setValue(float(rates.split(".")[1]) if "food." in rates else 1.0)
                    self.wood_rate_input['input'].setValue(float(rates.split(".")[1]) if "wood." in rates else 1.0)
                    self.stone_rate_input['input'].setValue(float(rates.split(".")[1]) if "stone." in rates else 1.0)
                    self.metal_rate_input['input'].setValue(float(rates.split(".")[1]) if "metal." in rates else 1.0)
                self.gather_capacity_input['input'].setValue(float(resource_gatherer.get("MaxCapacity", "20")))
            else:
                self.can_gather_checkbox['input'].setChecked(False)
            
            # Builder
            builder = root.find(".//Builder")
            if builder is not None:
                self.can_build_checkbox['input'].setChecked(True)
                self.build_rate_input['input'].setValue(float(builder.get("Rate", "1.0")))
                entities = builder.find("Entities")
                if entities is not None:
                    self.buildable_entities_input['input'].setText(entities.text or "")
            else:
                self.can_build_checkbox['input'].setChecked(False)
            
            # Garrison
            garrison_holder = root.find(".//GarrisonHolder")
            if garrison_holder is not None:
                self.garrison_capacity_input['input'].setValue(float(garrison_holder.get("Max", "0")))
                self.garrison_size_input['input'].setValue(float(garrison_holder.get("Size", "10")))
                self.allow_garrisoning_checkbox['input'].setChecked(garrison_holder.get("AllowGarrisoning", "false").lower() == "true")
                self.list_garrisoners_checkbox['input'].setChecked(garrison_holder.get("List", "false").lower() == "true")
            
            # Promotion
            promotion = root.find(".//Promotion")
            if promotion is not None:
                self.required_xp_input['input'].setValue(float(promotion.get("RequiredXp", "1000")))
                self.promote_to_input['input'].setText(promotion.get("Entity", ""))
            
            # Loot
            loot = root.find(".//Loot")
            if loot is not None:
                self.xp_loot_input['input'].setValue(float(loot.get("xp", "10")))
                self.food_loot_input['input'].setValue(float(loot.get("food", "0")))
                self.wood_loot_input['input'].setValue(float(loot.get("wood", "0")))
                self.stone_loot_input['input'].setValue(float(loot.get("stone", "0")))
                self.metal_loot_input['input'].setValue(float(loot.get("metal", "0")))
            
            # Selection
            selection = root.find(".//Selection")
            if selection is not None:
                self.selection_radius_input['input'].setValue(float(selection.get("Radius", "1.0")))
                self.selection_shape_input['input'].setCurrentText(selection.get("Shape", "circle"))
            
            # Sound
            sound = root.find(".//Sound")
            if sound is not None:
                groups = sound.find("SoundGroups")
                if groups is not None:
                    self.sound_group_input['input'].setText(groups.text or "")
            
            # Visual Actor
            visual_actor = root.find(".//VisualActor")
            if visual_actor is not None:
                self.actor_input['input'].setText(visual_actor.get("Actor", ""))
                self.foundation_actor_input['input'].setText(visual_actor.get("FoundationActor", ""))
                self.silhouette_input['input'].setText(visual_actor.get("Silhouette", ""))
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to parse unit XML: {e}")
    
    def _save_unit_properties(self):
        """Save all unit properties to the project."""
        if not self.selected_unit_path or not self.main_window.project:
            QMessageBox.warning(self, "Warning", "No unit selected")
            return
        
        try:
            root = ET.fromstring(self.selected_unit_xml)
            
            # Update Identity
            identity = root.find(".//Identity")
            if identity is None:
                identity = ET.SubElement(root, "Identity")
            identity.set("Civ", self.civ_input['input'].text() or "generic")
            identity.set("Generic", self.generic_input['input'].text() or "Unit")
            identity.set("Specific", self.specific_input['input'].text() or "Unit Name")
            identity.set("Rank", self.rank_input['input'].currentText())
            identity.set("Classes", self.classes_input['input'].text())
            identity.set("VisibleClasses", self.visible_classes_input['input'].text())
            identity.set("Icon", self.icon_input['input'].text())
            
            # Update Cost
            cost = root.find(".//Cost")
            if cost is None:
                cost = ET.SubElement(root, "Cost")
            cost.set("BuildTime", str(self.build_time_input['input'].value()))
            cost.set("Population", str(self.population_cost_input['input'].value()))
            
            resources = cost.find("Resources")
            if resources is None:
                resources = ET.SubElement(cost, "Resources")
            resources.set("food", str(self.food_cost_input['input'].value()))
            resources.set("wood", str(self.wood_cost_input['input'].value()))
            resources.set("stone", str(self.stone_cost_input['input'].value()))
            resources.set("metal", str(self.metal_cost_input['input'].value()))
            
            # Update Health
            health = root.find(".//Health")
            if health is None:
                health = ET.SubElement(root, "Health")
            health.set("Max", str(self.max_health_input['input'].value()))
            health.set("RegenRate", str(self.regen_rate_input['input'].value()))
            health.set("RegenDelay", str(self.regen_delay_input['input'].value()))
            
            # Update Attack
            attack = root.find(".//Attack")
            if attack is None:
                attack = ET.SubElement(root, "Attack")
            
            # Melee
            melee = attack.find("Melee")
            if melee is None:
                melee = ET.SubElement(attack, "Melee")
            melee.set("Hack", str(self.melee_hack_input['input'].value()))
            melee.set("Pierce", str(self.melee_pierce_input['input'].value()))
            melee.set("Crush", str(self.melee_crush_input['input'].value()))
            melee.set("MaxRange", str(self.melee_range_input['input'].value()))
            
            # Ranged
            if self.ranged_range_input['input'].value() > 0:
                ranged = attack.find("Ranged")
                if ranged is None:
                    ranged = ET.SubElement(attack, "Ranged")
                ranged.set("Hack", str(self.ranged_hack_input['input'].value()))
                ranged.set("Pierce", str(self.ranged_pierce_input['input'].value()))
                ranged.set("Crush", str(self.ranged_crush_input['input'].value()))
                ranged.set("MaxRange", str(self.ranged_range_input['input'].value()))
                ranged.set("PrepareTime", str(self.ranged_prepare_time_input['input'].value()))
            
            # Capture
            if self.capture_strength_input['input'].value() > 0:
                capture = attack.find("Capture")
                if capture is None:
                    capture = ET.SubElement(attack, "Capture")
                capture.set("Strength", str(self.capture_strength_input['input'].value()))
            
            # Update Defense
            resistance = root.find(".//Resistance")
            if resistance is None:
                resistance = ET.SubElement(root, "Resistance")
            resistance.set("Hack", str(self.hack_resistance_input['input'].value()))
            resistance.set("Pierce", str(self.pierce_resistance_input['input'].value()))
            resistance.set("Crush", str(self.crush_resistance_input['input'].value()))
            
            # Capture Resistance
            if self.capture_resistance_input['input'].value() > 0:
                capture_resistance = root.find(".//CaptureResistance")
                if capture_resistance is None:
                    capture_resistance = ET.SubElement(root, "CaptureResistance")
                capture_resistance.set("Capture", str(self.capture_resistance_input['input'].value()))
            
            # Update Movement
            unit_motion = root.find(".//UnitMotion")
            if unit_motion is None:
                unit_motion = ET.SubElement(root, "UnitMotion")
            unit_motion.set("WalkSpeed", str(self.walk_speed_input['input'].value()))
            unit_motion.set("Run", str(self.run_speed_input['input'].value()))
            unit_motion.set("Acceleration", str(self.acceleration_input['input'].value()))
            unit_motion.set("PassabilityClass", self.passability_class_input['input'].currentText())
            
            # Update Vision
            vision = root.find(".//Vision")
            if vision is None:
                vision = ET.SubElement(root, "Vision")
            vision.set("Range", str(self.vision_range_input['input'].value()))
            vision.set("RetainInFog", "true" if self.retain_in_fog_checkbox['input'].isChecked() else "false")
            vision.set("AlwaysVisible", "true" if self.always_visible_checkbox['input'].isChecked() else "false")
            
            # Update Resource Gathering
            if self.can_gather_checkbox['input'].isChecked():
                resource_gatherer = root.find(".//ResourceGatherer")
                if resource_gatherer is None:
                    resource_gatherer = ET.SubElement(root, "ResourceGatherer")
                
                rates_parts = []
                if self.food_rate_input['input'].value() > 0:
                    rates_parts.append(f"food.{self.food_rate_input['input'].value()}")
                if self.wood_rate_input['input'].value() > 0:
                    rates_parts.append(f"wood.{self.wood_rate_input['input'].value()}")
                if self.stone_rate_input['input'].value() > 0:
                    rates_parts.append(f"stone.{self.stone_rate_input['input'].value()}")
                if self.metal_rate_input['input'].value() > 0:
                    rates_parts.append(f"metal.{self.metal_rate_input['input'].value()}")
                
                resource_gatherer.set("Rates", " ".join(rates_parts) if rates_parts else "")
                resource_gatherer.set("MaxCapacity", str(self.gather_capacity_input['input'].value()))
            else:
                resource_gatherer = root.find(".//ResourceGatherer")
                if resource_gatherer is not None:
                    root.remove(resource_gatherer)
            
            # Update Builder
            if self.can_build_checkbox['input'].isChecked():
                builder = root.find(".//Builder")
                if builder is None:
                    builder = ET.SubElement(root, "Builder")
                builder.set("Rate", str(self.build_rate_input['input'].value()))
                
                entities = builder.find("Entities")
                if entities is None:
                    entities = ET.SubElement(builder, "Entities")
                entities.text = self.buildable_entities_input['input'].text()
            else:
                builder = root.find(".//Builder")
                if builder is not None:
                    root.remove(builder)
            
            # Update Garrison
            if self.garrison_capacity_input['input'].value() > 0:
                garrison_holder = root.find(".//GarrisonHolder")
                if garrison_holder is None:
                    garrison_holder = ET.SubElement(root, "GarrisonHolder")
                garrison_holder.set("Max", str(self.garrison_capacity_input['input'].value()))
                garrison_holder.set("Size", str(self.garrison_size_input['input'].value()))
                garrison_holder.set("AllowGarrisoning", "true" if self.allow_garrisoning_checkbox['input'].isChecked() else "false")
                garrison_holder.set("List", "true" if self.list_garrisoners_checkbox['input'].isChecked() else "false")
            else:
                garrison_holder = root.find(".//GarrisonHolder")
                if garrison_holder is not None:
                    root.remove(garrison_holder)
            
            # Update Promotion
            if self.promote_to_input['input'].text():
                promotion = root.find(".//Promotion")
                if promotion is None:
                    promotion = ET.SubElement(root, "Promotion")
                promotion.set("RequiredXp", str(self.required_xp_input['input'].value()))
                promotion.set("Entity", self.promote_to_input['input'].text())
            else:
                promotion = root.find(".//Promotion")
                if promotion is not None:
                    root.remove(promotion)
            
            # Update Loot
            loot = root.find(".//Loot")
            if loot is None:
                loot = ET.SubElement(root, "Loot")
            loot.set("xp", str(self.xp_loot_input['input'].value()))
            loot.set("food", str(self.food_loot_input['input'].value()))
            loot.set("wood", str(self.wood_loot_input['input'].value()))
            loot.set("stone", str(self.stone_loot_input['input'].value()))
            loot.set("metal", str(self.metal_loot_input['input'].value()))
            
            # Update Selection
            selection = root.find(".//Selection")
            if selection is None:
                selection = ET.SubElement(root, "Selection")
            selection.set("Radius", str(self.selection_radius_input['input'].value()))
            selection.set("Shape", self.selection_shape_input['input'].currentText())
            
            # Update Sound
            if self.sound_group_input['input'].text():
                sound = root.find(".//Sound")
                if sound is None:
                    sound = ET.SubElement(root, "Sound")
                groups = sound.find("SoundGroups")
                if groups is None:
                    groups = ET.SubElement(sound, "SoundGroups")
                groups.text = self.sound_group_input['input'].text()
            else:
                sound = root.find(".//Sound")
                if sound is not None:
                    root.remove(sound)
            
            # Update Visual Actor
            visual_actor = root.find(".//VisualActor")
            if visual_actor is None:
                visual_actor = ET.SubElement(root, "VisualActor")
            visual_actor.set("Actor", self.actor_input['input'].text())
            visual_actor.set("FoundationActor", self.foundation_actor_input['input'].text())
            visual_actor.set("Silhouette", self.silhouette_input['input'].text())
            
            # Convert back to string
            new_xml = ET.tostring(root, encoding='unicode')
            
            # Update project
            self.main_window.project.update_file(new_xml, self.selected_unit_path)
            self.selected_unit_xml = new_xml
            self.xml_editor.setPlainText(new_xml)
            
            QMessageBox.information(self, "Success", "All unit properties saved successfully")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save unit properties: {e}")
    
    def _reset_properties(self):
        """Reset all properties to original XML values."""
        if self.selected_unit_xml:
            self._populate_all_properties(self.selected_unit_xml)
            QMessageBox.information(self, "Reset", "Properties reset to original values")
    
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
            self._populate_all_properties(xml_content)
            QMessageBox.information(self, "Success", "XML saved successfully")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save XML: {e}")
    
    def get_help_text(self) -> str:
        """Provide help for the Units tab."""
        return (
            "Units Editor Help:\n\n"
            "This comprehensive editor allows you to modify almost all unit properties.\n\n"
            "📋 Unit List:\n"
            "• Select a unit from the list to edit its properties\n"
            "• Units are loaded from your current project\n\n"
            "🏷️ Identity Tab:\n"
            "• Civilization, names, classes, and ranks\n"
            "• Icon path and classification\n\n"
            "💰 Cost Tab:\n"
            "• Build time and resource costs\n"
            "• Population requirements\n\n"
            "❤️ Health Tab:\n"
            "• Maximum health and regeneration\n"
            "• Regeneration delay settings\n\n"
            "⚔️ Attack Tab:\n"
            "• Melee and ranged damage values\n"
            "• Damage types: Hack, Pierce, Crush\n"
            "• Attack ranges and preparation times\n\n"
            "🛡️ Defense Tab:\n"
            "• Resistance to different damage types\n"
            "• Capture resistance\n\n"
            "🏃 Movement Tab:\n"
            "• Walk and run speeds\n"
            "• Acceleration and terrain passability\n\n"
            "👁️ Vision Tab:\n"
            "• Vision range and fog of war settings\n\n"
            "🌾 Gather Tab:\n"
            "• Resource gathering rates\n"
            "• Gathering capacity\n\n"
            "🔨 Builder Tab:\n"
            "• Construction abilities and rates\n"
            "• Buildable structure types\n\n"
            "🏰 Garrison Tab:\n"
            "• Garrison capacity and size\n"
            "• Garrison visibility settings\n\n"
            "⭐ Promotion Tab:\n"
            "• Experience requirements\n"
            "• Promotion target entity\n\n"
            "💎 Loot Tab:\n"
            "• Resources and XP given when killed\n\n"
            "🎯 Selection Tab:\n"
            "• Selection radius and shape\n\n"
            "🔊 Sound Tab:\n"
            "• Sound group assignments\n\n"
            "🎭 Actor Tab:\n"
            "• Visual model and actor settings\n\n"
            "💾 Saving:\n"
            "• 'Save All Changes' saves all form fields\n"
            "• 'Reset to Original' reverts to original XML\n"
            "• 'Save XML' saves raw XML editor content\n\n"
            "🔧 XML Editor:\n"
            "• Toggle XML editor for direct XML editing\n"
            "• Useful for advanced users and custom properties"
        )


class NewUnitTab(BaseTab):
    """Simplified unit creator with basic functionality."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("➕ Create New Unit")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        # Description
        description = QLabel("Create a new unit template with basic settings. You can edit it in the Units tab after creation.")
        description.setStyleSheet("color: #c0c0d0; font-size: 14px;")
        layout.addWidget(description)
        
        # Basic information form
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        
        # Unit name
        name_row = QHBoxLayout()
        name_label = QLabel("Unit Name:")
        name_label.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        name_label.setFixedWidth(120)
        name_row.addWidget(name_label)
        
        self.unit_name_input = QLineEdit()
        self.unit_name_input.setPlaceholderText("e.g., infantry_spearman")
        self.unit_name_input.setStyleSheet(get_line_edit_style())
        name_row.addWidget(self.unit_name_input)
        form_layout.addLayout(name_row)
        
        # Display name
        display_row = QHBoxLayout()
        display_label = QLabel("Display Name:")
        display_label.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        display_label.setFixedWidth(120)
        display_row.addWidget(display_label)
        
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("e.g., Spearman")
        self.display_name_input.setStyleSheet(get_line_edit_style())
        display_row.addWidget(self.display_name_input)
        form_layout.addLayout(display_row)
        
        # Civilization
        civ_row = QHBoxLayout()
        civ_label = QLabel("Civilization:")
        civ_label.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        civ_label.setFixedWidth(120)
        civ_row.addWidget(civ_label)
        
        self.civ_input = QLineEdit()
        self.civ_input.setPlaceholderText("e.g., athen, spart")
        self.civ_input.setStyleSheet(get_line_edit_style())
        civ_row.addWidget(self.civ_input)
        form_layout.addLayout(civ_row)
        
        layout.addWidget(form_frame)
        
        # Quick stats
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("📊 Basic Stats")
        stats_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        stats_layout.addWidget(stats_title)
        
        # Stats grid
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(15)
        
        # Health
        health_card = self._create_stat_card("❤️ Health", "100")
        self.health_input = health_card['input']
        stats_grid.addWidget(health_card['card'])
        
        # Attack
        attack_card = self._create_stat_card("⚔️ Attack", "10")
        self.attack_input = attack_card['input']
        stats_grid.addWidget(attack_card['card'])
        
        # Defense
        defense_card = self._create_stat_card("🛡️ Defense", "5")
        self.defense_input = defense_card['input']
        stats_grid.addWidget(defense_card['card'])
        
        # Speed
        speed_card = self._create_stat_card("🏃 Speed", "1.0")
        self.speed_input = speed_card['input']
        stats_grid.addWidget(speed_card['card'])
        
        stats_layout.addLayout(stats_grid)
        layout.addWidget(stats_frame)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        create_btn = QPushButton("✨ Create Unit")
        create_btn.setStyleSheet(get_button_style(accent=True))
        create_btn.clicked.connect(self._create_unit)
        create_btn.setMinimumHeight(50)
        button_layout.addWidget(create_btn)
        
        reset_btn = QPushButton("🔄 Reset Form")
        reset_btn.setStyleSheet(get_button_style())
        reset_btn.clicked.connect(self._reset_form)
        reset_btn.setMinimumHeight(50)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
    
    def _create_stat_card(self, icon: str, default: str) -> dict:
        """Create a stat input card."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1a1a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        card_layout = QVBoxLayout(card)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)
        
        input_widget = QLineEdit()
        input_widget.setText(default)
        input_widget.setStyleSheet(get_line_edit_style())
        input_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(input_widget)
        
        return {'card': card, 'input': input_widget}
    
    def _reset_form(self):
        """Reset form to defaults."""
        self.unit_name_input.clear()
        self.display_name_input.clear()
        self.civ_input.clear()
        self.health_input.setText("100")
        self.attack_input.setText("10")
        self.defense_input.setText("5")
        self.speed_input.setText("1.0")
    
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
            display_name = self.display_name_input.text().strip() or unit_name
            civ = self.civ_input.text().strip() or "generic"
            health = self.health_input.text() or "100"
            attack = self.attack_input.text() or "10"
            defense = self.defense_input.text() or "5"
            speed = self.speed_input.text() or "1.0"
            
            xml_content = f'''<?xml version="1.0" encoding="utf-8"?>
<Entity>
  <Template>{unit_name}</Template>
  <Identity>
    <Civ>{civ}</Civ>
    <Generic>Unit</Generic>
    <Specific>{display_name}</Specific>
    <Rank>Basic</Rank>
  </Identity>
  <Cost>
    <BuildTime>10</BuildTime>
    <Population>1</Population>
    <Resources>
      <food>50</food>
      <wood>0</wood>
      <stone>0</stone>
      <metal>0</metal>
    </Resources>
  </Cost>
  <Health>
    <Max>{health}</Max>
  </Health>
  <Attack>
    <Melee>
      <Hack>{attack}</Hack>
      <Pierce>0</Pierce>
      <Crush>0</Crush>
      <MaxRange>3.0</MaxRange>
    </Melee>
  </Attack>
  <Resistance>
    <Hack>{defense}</Hack>
    <Pierce>{defense}</Pierce>
    <Crush>{defense}</Crush>
  </Resistance>
  <UnitMotion>
    <WalkSpeed>{speed}</WalkSpeed>
    <Run>0</Run>
  </UnitMotion>
  <Vision>
    <Range>32</Range>
  </Vision>
  <Loot>
    <xp>10</xp>
    <food>0</food>
    <wood>0</wood>
    <stone>0</stone>
    <metal>0</metal>
  </Loot>
  <VisualActor>
    <Actor>props/units/hellenes/infantry_spearman.xml</Actor>
  </VisualActor>
</Entity>'''
            
            path = f"simulation/templates/units/{unit_name}.xml"
            self.main_window.project.add_file(xml_content, path)
            
            QMessageBox.information(self, "Success", f"Unit '{unit_name}' created successfully! You can now edit it in the Units tab.")
            self._reset_form()
            
            # Refresh units tab
            self.main_window.units_tab.refresh()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create unit: {e}")
    
    def refresh(self):
        """Refresh the tab."""
        pass
    
    def get_help_text(self) -> str:
        """Provide help for the Unit Creator tab."""
        return (
            "Unit Creator Help:\n\n"
            "📋 Basic Information:\n"
            "• Unit Name: Internal name (no spaces, use underscores)\n"
            "• Display Name: Name shown to players\n"
            "• Civilization: Civ code (e.g., athen, spart)\n\n"
            "📊 Basic Stats:\n"
            "• Health: Maximum hit points\n"
            "• Attack: Base attack damage\n"
            "• Defense: Base resistance value\n"
            "• Speed: Movement speed\n\n"
            "✨ Create Unit:\n"
            "• Creates a basic unit template\n"
            "• Unit will be saved to simulation/templates/units/\n"
            "• Use the Units tab for advanced editing\n\n"
            "🔄 Reset Form:\n"
            "• Clear all fields and reset to defaults"
        )
    """Comprehensive new unit creator with templates and full customization."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("➕ Unit Creator")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(header)
        
        # Description
        description = QLabel("Create a new unit template with comprehensive customization options or start from a preset.")
        description.setStyleSheet("color: #c0c0d0; font-size: 14px;")
        layout.addWidget(description)
        
        # Template selection section
        template_frame = QFrame()
        template_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d2d3d, stop:1 #383848);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        template_layout = QVBoxLayout(template_frame)
        
        template_title = QLabel("🎨 Choose a Template")
        template_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        template_layout.addWidget(template_title)
        
        # Template grid
        template_grid = QHBoxLayout()
        template_grid.setSpacing(15)
        
        templates = [
            ("👤", "Basic Unit", "Standard combat unit with basic stats"),
            ("🏹", "Archer", "Ranged unit with attack damage"),
            ("🗡️", "Melee Fighter", "Close combat specialist"),
            ("🐴", "Cavalry", "Mounted unit with speed bonus"),
            ("🏰", "Structure", "Building or structure"),
            ("👷", "Worker", "Resource gathering unit"),
            ("🛡️", "Support", "Healer or support unit"),
            ("⚔️", "Hero", "Powerful hero unit")
        ]
        
        for icon, name, desc in templates:
            template_btn = QPushButton(f"{icon}\n{name}")
            template_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a2a;
                    color: #c0c0d0;
                    border: 2px solid #4a4a6a;
                    border-radius: 10px;
                    padding: 15px;
                    font-size: 14px;
                    font-weight: bold;
                    min-height: 80px;
                }
                QPushButton:hover {
                    background-color: #383848;
                    border-color: #7b5eff;
                    color: #ffffff;
                }
                QPushButton:checked {
                    background-color: #7b5eff;
                    border-color: #7b5eff;
                    color: white;
                }
            """)
            template_btn.setCheckable(True)
            template_btn.setToolTip(desc)
            template_btn.clicked.connect(lambda checked, n=name: self._select_template(n))
            template_grid.addWidget(template_btn)
        
        template_layout.addLayout(template_grid)
        layout.addWidget(template_frame)
        
        # Basic information section
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("📋 Basic Information")
        info_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        info_layout.addWidget(info_title)
        
        # Unit name row
        name_row = QHBoxLayout()
        name_label = QLabel("Unit Internal Name:")
        name_label.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        name_label.setFixedWidth(150)
        name_row.addWidget(name_label)
        
        self.unit_name_input = QLineEdit()
        self.unit_name_input.setPlaceholderText("e.g., athen_infantry_spearman")
        self.unit_name_input.setStyleSheet(get_line_edit_style())
        self.unit_name_input.setToolTip("Internal name used in code (no spaces, use underscores)")
        name_row.addWidget(self.unit_name_input)
        info_layout.addLayout(name_row)
        
        # Display name row
        display_row = QHBoxLayout()
        display_label = QLabel("Display Name:")
        display_label.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        display_label.setFixedWidth(150)
        display_row.addWidget(display_label)
        
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("e.g., Athenian Spearman")
        self.display_name_input.setStyleSheet(get_line_edit_style())
        self.display_name_input.setToolTip("Name shown to players")
        display_row.addWidget(self.display_name_input)
        info_layout.addLayout(display_row)
        
        # Generic name row
        generic_row = QHBoxLayout()
        generic_label = QLabel("Generic Type:")
        generic_label.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        generic_label.setFixedWidth(150)
        generic_row.addWidget(generic_label)
        
        self.generic_name_input = QLineEdit()
        self.generic_name_input.setPlaceholderText("e.g., Infantry")
        self.generic_name_input.setStyleSheet(get_line_edit_style())
        self.generic_name_input.setToolTip("Generic unit type (e.g., Infantry, Cavalry)")
        generic_row.addWidget(self.generic_name_input)
        info_layout.addLayout(generic_row)
        
        # Civilization row
        civ_row = QHBoxLayout()
        civ_label = QLabel("Civilization:")
        civ_label.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
        civ_label.setFixedWidth(150)
        civ_row.addWidget(civ_label)
        
        self.civ_input = QLineEdit()
        self.civ_input.setPlaceholderText("e.g., athen, spart, rome")
        self.civ_input.setStyleSheet(get_line_edit_style())
        self.civ_input.setToolTip("Civilization code")
        civ_row.addWidget(self.civ_input)
        info_layout.addLayout(civ_row)
        
        layout.addWidget(info_frame)
        
        # Quick stats section
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("📊 Quick Stats")
        stats_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        stats_layout.addWidget(stats_title)
        
        # Stats grid
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(20)
        
        # Health
        health_card = self._create_stat_card("❤️ Health", "100", "Maximum hit points")
        self.health_input = health_card['input']
        stats_grid.addWidget(health_card['card'])
        
        # Attack
        attack_card = self._create_stat_card("⚔️ Attack", "10", "Base attack damage")
        self.attack_input = attack_card['input']
        stats_grid.addWidget(attack_card['card'])
        
        # Defense
        defense_card = self._create_stat_card("🛡️ Defense", "5", "Base defense value")
        self.defense_input = defense_card['input']
        stats_grid.addWidget(defense_card['card'])
        
        # Speed
        speed_card = self._create_stat_card("🏃 Speed", "1.0", "Movement speed")
        self.speed_input = speed_card['input']
        stats_grid.addWidget(speed_card['card'])
        
        stats_layout.addLayout(stats_grid)
        layout.addWidget(stats_frame)
        
        # Advanced options toggle
        self.advanced_visible = False
        advanced_toggle = QPushButton("🔧 Show Advanced Options")
        advanced_toggle.setStyleSheet(get_button_style())
        advanced_toggle.clicked.connect(self._toggle_advanced)
        layout.addWidget(advanced_toggle)
        
        # Advanced options section (hidden by default)
        self.advanced_frame = QFrame()
        self.advanced_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        advanced_layout = QVBoxLayout(self.advanced_frame)
        
        advanced_title = QLabel("⚙️ Advanced Configuration")
        advanced_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        advanced_layout.addWidget(advanced_title)
        
        # Create advanced tabs
        from PyQt6.QtWidgets import QTabWidget
        self.advanced_tabs = QTabWidget()
        self.advanced_tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: #1a1a2a;
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
        
        # Simplified version - skip advanced tabs for now
        # self._add_helper_methods()
        # self._create_advanced_cost_tab()
        # self._create_advanced_combat_tab()
        # self._create_advanced_movement_tab()
        # self._create_advanced_vision_tab()
        # self._create_advanced_gather_tab()
        # self._create_advanced_garrison_tab()
        
        # Just add basic helper methods inline
        def _create_number_field(label: str, default: float, tooltip: str) -> dict:
            from PyQt6.QtWidgets import QDoubleSpinBox
            layout = QHBoxLayout()
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
            label_widget.setFixedWidth(150)
            label_widget.setToolTip(tooltip)
            layout.addWidget(label_widget)
            
            input_widget = QDoubleSpinBox()
            input_widget.setRange(0, 10000)
            input_widget.setValue(default)
            input_widget.setSingleStep(0.1)
            input_widget.setStyleSheet(get_spin_box_style())
            input_widget.setToolTip(tooltip)
            layout.addWidget(input_widget)
            
            layout.addStretch()
            
            return {'layout': layout, 'input': input_widget}
        
        def _create_combo_field(label: str, options: list, default: str, tooltip: str) -> dict:
            from PyQt6.QtWidgets import QComboBox
            layout = QHBoxLayout()
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
            label_widget.setFixedWidth(150)
            label_widget.setToolTip(tooltip)
            layout.addWidget(label_widget)
            
            input_widget = QComboBox()
            input_widget.addItems(options)
            input_widget.setCurrentText(default)
            input_widget.setStyleSheet(get_spin_box_style())
            input_widget.setToolTip(tooltip)
            layout.addWidget(input_widget)
            
            layout.addStretch()
            
            return {'layout': layout, 'input': input_widget}
        
        def _create_checkbox_field(label: str, default: bool, tooltip: str) -> dict:
            layout = QHBoxLayout()
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
            label_widget.setFixedWidth(150)
            label_widget.setToolTip(tooltip)
            layout.addWidget(label_widget)
            
            input_widget = QCheckBox("Enabled")
            input_widget.setChecked(default)
            input_widget.setStyleSheet("color: #c0c0d0; font-size: 13px;")
            input_widget.setToolTip(tooltip)
            layout.addWidget(input_widget)
            
            layout.addStretch()
            
            return {'layout': layout, 'input': input_widget}
        
        # Bind methods to class
        self._create_number_field = _create_number_field
        self._create_combo_field = _create_combo_field
        self._create_checkbox_field = _create_checkbox_field
        
        # For now, skip advanced tabs to avoid complexity
        # Just use simple basic options
        return
        """Add helper methods for form field creation."""
        def _create_number_field(label: str, default: float, tooltip: str) -> dict:
            from PyQt6.QtWidgets import QDoubleSpinBox
            layout = QHBoxLayout()
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
            label_widget.setFixedWidth(150)
            label_widget.setToolTip(tooltip)
            layout.addWidget(label_widget)
            
            input_widget = QDoubleSpinBox()
            input_widget.setRange(0, 10000)
            input_widget.setValue(default)
            input_widget.setSingleStep(0.1)
            input_widget.setStyleSheet(get_spin_box_style())
            input_widget.setToolTip(tooltip)
            layout.addWidget(input_widget)
            
            layout.addStretch()
            
            return {'layout': layout, 'input': input_widget}
        
        def _create_combo_field(label: str, options: list, default: str, tooltip: str) -> dict:
            from PyQt6.QtWidgets import QComboBox
            layout = QHBoxLayout()
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
            label_widget.setFixedWidth(150)
            label_widget.setToolTip(tooltip)
            layout.addWidget(label_widget)
            
            input_widget = QComboBox()
            input_widget.addItems(options)
            input_widget.setCurrentText(default)
            input_widget.setStyleSheet(get_spin_box_style())
            input_widget.setToolTip(tooltip)
            layout.addWidget(input_widget)
            
            layout.addStretch()
            
            return {'layout': layout, 'input': input_widget}
        
        def _create_checkbox_field(label: str, default: bool, tooltip: str) -> dict:
            layout = QHBoxLayout()
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #7b5eff; font-size: 13px; font-weight: bold;")
            label_widget.setFixedWidth(150)
            label_widget.setToolTip(tooltip)
            layout.addWidget(label_widget)
            
            input_widget = QCheckBox("Enabled")
            input_widget.setChecked(default)
            input_widget.setStyleSheet("color: #c0c0d0; font-size: 13px;")
            input_widget.setToolTip(tooltip)
            layout.addWidget(input_widget)
            
            layout.addStretch()
            
            return {'layout': layout, 'input': input_widget}
        
        # Bind methods to class
        self._create_number_field = _create_number_field
        self._create_combo_field = _create_combo_field
        self._create_checkbox_field = _create_checkbox_field
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        create_btn = QPushButton("✨ Create Unit")
        create_btn.setStyleSheet(get_button_style(accent=True))
        create_btn.clicked.connect(self._create_unit)
        create_btn.setMinimumHeight(50)
        button_layout.addWidget(create_btn)
        
        preview_btn = QPushButton("👁️ Preview XML")
        preview_btn.setStyleSheet(get_button_style())
        preview_btn.clicked.connect(self._preview_xml)
        preview_btn.setMinimumHeight(50)
        button_layout.addWidget(preview_btn)
        
        reset_btn = QPushButton("🔄 Reset Form")
        reset_btn.setStyleSheet(get_button_style())
        reset_btn.clicked.connect(self._reset_form)
        reset_btn.setMinimumHeight(50)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
        # Current template tracking
        self.current_template = None
    
    def _create_stat_card(self, icon: str, default: str, tooltip: str) -> dict:
        """Create a stat input card."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1a1a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        card_layout = QVBoxLayout(card)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)
        
        input_widget = QLineEdit()
        input_widget.setText(default)
        input_widget.setStyleSheet(get_line_edit_style())
        input_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_widget.setToolTip(tooltip)
        card_layout.addWidget(input_widget)
        
        return {'card': card, 'input': input_widget}
    
    def _create_advanced_cost_tab(self):
        """Create advanced cost configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("💰 Advanced Cost Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.build_time_input = self._create_number_field("Build Time:", 10, "Time to train in seconds")
        form_layout.addLayout(self.build_time_input['layout'])
        
        self.population_input = self._create_number_field("Population:", 1, "Population slots used")
        form_layout.addLayout(self.population_input['layout'])
        
        self.food_cost_input = self._create_number_field("Food Cost:", 50, "Food resource cost")
        form_layout.addLayout(self.food_cost_input['layout'])
        
        self.wood_cost_input = self._create_number_field("Wood Cost:", 0, "Wood resource cost")
        form_layout.addLayout(self.wood_cost_input['layout'])
        
        self.stone_cost_input = self._create_number_field("Stone Cost:", 0, "Stone resource cost")
        form_layout.addLayout(self.stone_cost_input['layout'])
        
        self.metal_cost_input = self._create_number_field("Metal Cost:", 0, "Metal resource cost")
        form_layout.addLayout(self.metal_cost_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.advanced_tabs.addTab(tab, "💰 Cost")
    
    def _create_advanced_combat_tab(self):
        """Create advanced combat configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("⚔️ Advanced Combat Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.melee_range_input = self._create_number_field("Melee Range:", 3.0, "Range for melee attacks")
        form_layout.addLayout(self.melee_range_input['layout'])
        
        self.ranged_damage_input = self._create_number_field("Ranged Damage:", 0, "Ranged attack damage (0 = no ranged)")
        form_layout.addLayout(self.ranged_damage_input['layout'])
        
        self.ranged_range_input = self._create_number_field("Ranged Range:", 0, "Range for ranged attacks")
        form_layout.addLayout(self.ranged_range_input['layout'])
        
        self.capture_attack_input = self._create_number_field("Capture Attack:", 0, "Capture attack strength")
        form_layout.addLayout(self.capture_attack_input['layout'])
        
        self.xp_loot_input = self._create_number_field("XP Loot:", 10, "XP given when killed")
        form_layout.addLayout(self.xp_loot_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.advanced_tabs.addTab(tab, "⚔️ Combat")
    
    def _create_advanced_movement_tab(self):
        """Create advanced movement configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("🏃 Advanced Movement Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.acceleration_input = self._create_number_field("Acceleration:", 2.0, "Movement acceleration")
        form_layout.addLayout(self.acceleration_input['layout'])
        
        self.passability_input = self._create_combo_field("Passability:", ["default", "ship", "large"], "default", "Terrain passability")
        form_layout.addLayout(self.passability_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.advanced_tabs.addTab(tab, "🏃 Movement")
    
    def _create_advanced_vision_tab(self):
        """Create advanced vision configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("👁️ Advanced Vision Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.vision_range_input = self._create_number_field("Vision Range:", 32, "Distance unit can see")
        form_layout.addLayout(self.vision_range_input['layout'])
        
        self.retain_fog_checkbox = self._create_checkbox_field("Retain in Fog", False, "Unit remains visible in fog")
        form_layout.addLayout(self.retain_fog_checkbox['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.advanced_tabs.addTab(tab, "👁️ Vision")
    
    def _create_advanced_gather_tab(self):
        """Create advanced resource gathering configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("🌾 Advanced Gathering Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.can_gather_checkbox = self._create_checkbox_field("Can Gather Resources", False, "Unit can gather resources")
        form_layout.addLayout(self.can_gather_checkbox['layout'])
        
        self.gather_rate_input = self._create_number_field("Gather Rate:", 1.0, "Resource gathering rate")
        form_layout.addLayout(self.gather_rate_input['layout'])
        
        self.gather_capacity_input = self._create_number_field("Gather Capacity:", 20, "Max resources unit can carry")
        form_layout.addLayout(self.gather_capacity_input['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.advanced_tabs.addTab(tab, "🌾 Gather")
    
    def _create_advanced_garrison_tab(self):
        """Create advanced garrison configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d3d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(container)
        
        title = QLabel("🏰 Advanced Garrison Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b5eff;")
        form_layout.addWidget(title)
        
        self.garrison_capacity_input = self._create_number_field("Garrison Capacity:", 0, "Units that can garrison")
        form_layout.addLayout(self.garrison_capacity_input['layout'])
        
        self.allow_garrison_checkbox = self._create_checkbox_field("Allow Garrisoning", False, "Units can garrison here")
        form_layout.addLayout(self.allow_garrison_checkbox['layout'])
        
        layout.addWidget(container)
        layout.addStretch()
        
        self.advanced_tabs.addTab(tab, "🏰 Garrison")
    
    def _select_template(self, template_name: str):
        """Apply a template preset."""
        self.current_template = template_name
        
        # Reset form
        self._reset_form()
        
        # Apply template-specific defaults
        templates = {
            "Basic Unit": {
                "health": "100", "attack": "10", "defense": "5", "speed": "1.0",
                "generic": "Infantry", "melee_range": "3.0", "vision_range": "32"
            },
            "Archer": {
                "health": "80", "attack": "5", "defense": "3", "speed": "1.0",
                "generic": "Ranged", "ranged_damage": "15", "ranged_range": "30", "vision_range": "40"
            },
            "Melee Fighter": {
                "health": "120", "attack": "15", "defense": "8", "speed": "1.1",
                "generic": "Infantry", "melee_range": "3.0", "vision_range": "32"
            },
            "Cavalry": {
                "health": "150", "attack": "12", "defense": "6", "speed": "1.5",
                "generic": "Cavalry", "melee_range": "4.0", "vision_range": "36"
            },
            "Structure": {
                "health": "1000", "attack": "0", "defense": "20", "speed": "0",
                "generic": "Structure", "garrison_capacity": "10", "vision_range": "40"
            },
            "Worker": {
                "health": "50", "attack": "3", "defense": "2", "speed": "1.0",
                "generic": "Citizen", "can_gather": True, "vision_range": "30"
            },
            "Support": {
                "health": "80", "attack": "0", "defense": "3", "speed": "1.0",
                "generic": "Support", "vision_range": "32"
            },
            "Hero": {
                "health": "300", "attack": "25", "defense": "12", "speed": "1.2",
                "generic": "Hero", "melee_range": "3.5", "vision_range": "50", "xp_loot": "100"
            }
        }
        
        if template_name in templates:
            template = templates[template_name]
            
            # Apply basic stats
            if "health" in template:
                self.health_input.setText(template["health"])
            if "attack" in template:
                self.attack_input.setText(template["attack"])
            if "defense" in template:
                self.defense_input.setText(template["defense"])
            if "speed" in template:
                self.speed_input.setText(template["speed"])
            if "generic" in template:
                self.generic_name_input.setText(template["generic"])
            
            # Apply advanced stats if visible
            if self.advanced_visible:
                if "melee_range" in template:
                    self.melee_range_input['input'].setValue(float(template["melee_range"]))
                if "ranged_damage" in template:
                    self.ranged_damage_input['input'].setValue(float(template["ranged_damage"]))
                if "ranged_range" in template:
                    self.ranged_range_input['input'].setValue(float(template["ranged_range"]))
                if "vision_range" in template:
                    self.vision_range_input['input'].setValue(float(template["vision_range"]))
                if "garrison_capacity" in template:
                    self.garrison_capacity_input['input'].setValue(float(template["garrison_capacity"]))
                if "can_gather" in template:
                    self.can_gather_checkbox['input'].setChecked(template["can_gather"])
                if "xp_loot" in template:
                    self.xp_loot_input['input'].setValue(float(template["xp_loot"]))
    
    def _toggle_advanced(self):
        """Toggle advanced options visibility."""
        self.advanced_visible = not self.advanced_visible
        self.advanced_frame.setVisible(self.advanced_visible)
        
        # If showing advanced and template is selected, apply advanced template values
        if self.advanced_visible and self.current_template:
            self._select_template(self.current_template)
    
    def _reset_form(self):
        """Reset all form fields to defaults."""
        self.unit_name_input.clear()
        self.display_name_input.clear()
        self.generic_name_input.clear()
        self.civ_input.clear()
        
        self.health_input.setText("100")
        self.attack_input.setText("10")
        self.defense_input.setText("5")
        self.speed_input.setText("1.0")
        
        # Reset advanced fields
        self.build_time_input['input'].setValue(10)
        self.population_input['input'].setValue(1)
        self.food_cost_input['input'].setValue(50)
        self.wood_cost_input['input'].setValue(0)
        self.stone_cost_input['input'].setValue(0)
        self.metal_cost_input['input'].setValue(0)
        
        self.melee_range_input['input'].setValue(3.0)
        self.ranged_damage_input['input'].setValue(0)
        self.ranged_range_input['input'].setValue(0)
        self.capture_attack_input['input'].setValue(0)
        self.xp_loot_input['input'].setValue(10)
        
        self.acceleration_input['input'].setValue(2.0)
        self.passability_input['input'].setCurrentText("default")
        
        self.vision_range_input['input'].setValue(32)
        self.retain_fog_checkbox['input'].setChecked(False)
        
        self.can_gather_checkbox['input'].setChecked(False)
        self.gather_rate_input['input'].setValue(1.0)
        self.gather_capacity_input['input'].setValue(20)
        
        self.garrison_capacity_input['input'].setValue(0)
        self.allow_garrison_checkbox['input'].setChecked(False)
        
        self.current_template = None
    
    def _generate_xml(self) -> str:
        """Generate XML from form values."""
        try:
            # Get basic values
            unit_name = self.unit_name_input.text().strip() or "new_unit"
            display_name = self.display_name_input.text().strip() or unit_name
            generic_name = self.generic_name_input.text().strip() or "Unit"
            civ = self.civ_input.text().strip() or "generic"
            
            health = self.health_input.text() or "100"
            attack = self.attack_input.text() or "10"
            defense = self.defense_input.text() or "5"
            speed = self.speed_input.text() or "1.0"
            
            # Get advanced values
            build_time = str(self.build_time_input['input'].value())
            population = str(self.population_input['input'].value())
            food_cost = str(self.food_cost_input['input'].value())
            wood_cost = str(self.wood_cost_input['input'].value())
            stone_cost = str(self.stone_cost_input['input'].value())
            metal_cost = str(self.metal_cost_input['input'].value())
            
            melee_range = str(self.melee_range_input['input'].value())
            ranged_damage = str(self.ranged_damage_input['input'].value())
            ranged_range = str(self.ranged_range_input['input'].value())
            capture_attack = str(self.capture_attack_input['input'].value())
            xp_loot = str(self.xp_loot_input['input'].value())
            
            acceleration = str(self.acceleration_input['input'].value())
            passability = self.passability_input['input'].currentText()
            
            vision_range = str(self.vision_range_input['input'].value())
            retain_fog = "true" if self.retain_fog_checkbox['input'].isChecked() else "false"
            
            can_gather = self.can_gather_checkbox['input'].isChecked()
            gather_rate = str(self.gather_rate_input['input'].value())
            gather_capacity = str(self.gather_capacity_input['input'].value())
            
            garrison_capacity = str(self.garrison_capacity_input['input'].value())
            allow_garrison = "true" if self.allow_garrison_checkbox['input'].isChecked() else "false"
            
            # Build XML
            xml_lines = [
                '<?xml version="1.0" encoding="utf-8"?>',
                '<Entity>',
                f'  <Template>{unit_name}</Template>',
                '  <Identity>',
                f'    <Civ>{civ}</Civ>',
                f'    <Generic>{generic_name}</Generic>',
                f'    <Specific>{display_name}</Specific>',
                '    <Rank>Basic</Rank>',
                '  </Identity>',
                '  <Cost>',
                f'    <BuildTime>{build_time}</BuildTime>',
                f'    <Population>{population}</Population>',
                '    <Resources>',
                f'      <food>{food_cost}</food>',
                f'      <wood>{wood_cost}</wood>',
                f'      <stone>{stone_cost}</stone>',
                f'      <metal>{metal_cost}</metal>',
                '    </Resources>',
                '  </Cost>',
                '  <Health>',
                f'    <Max>{health}</Max>',
                '  </Health>',
                '  <Attack>'
            ]
            
            # Add melee attack
            if float(attack) > 0:
                xml_lines.extend([
                    '    <Melee>',
                    f'      <Hack>{attack}</Hack>',
                    f'      <Pierce>0</Pierce>',
                    f'      <Crush>0</Crush>',
                    f'      <MaxRange>{melee_range}</MaxRange>',
                    '    </Melee>'
                ])
            
            # Add ranged attack
            if float(ranged_damage) > 0:
                xml_lines.extend([
                    '    <Ranged>',
                    f'      <Hack>{ranged_damage}</Hack>',
                    f'      <Pierce>0</Pierce>',
                    f'      <Crush>0</Crush>',
                    f'      <MaxRange>{ranged_range}</MaxRange>',
                    '      <PrepareTime>1.0</PrepareTime>',
                    '    </Ranged>'
                ])
            
            # Add capture attack
            if float(capture_attack) > 0:
                xml_lines.extend([
                    '    <Capture>',
                    f'      <Strength>{capture_attack}</Strength>',
                    '    </Capture>'
                ])
            
            xml_lines.extend([
                '  </Attack>',
                '  <Resistance>',
                f'    <Hack>{defense}</Hack>',
                f'    <Pierce>{defense}</Pierce>',
                f'    <Crush>{defense}</Crush>',
                '  </Resistance>'
            ])
            
            # Add movement if not structure
            if float(speed) > 0:
                xml_lines.extend([
                    '  <UnitMotion>',
                    f'    <WalkSpeed>{speed}</WalkSpeed>',
                    f'    <Run>0</Run>',
                    f'    <Acceleration>{acceleration}</Acceleration>',
                    f'    <PassabilityClass>{passability}</PassabilityClass>',
                    '  </UnitMotion>'
                ])
            
            # Add vision
            xml_lines.extend([
                '  <Vision>',
                f'    <Range>{vision_range}</Range>',
                f'    <RetainInFog>{retain_fog}</RetainInFog>',
                '  </Vision>'
            ])
            
            # Add resource gathering
            if can_gather:
                xml_lines.extend([
                    '  <ResourceGatherer>',
                    f'    <Rates>food.{gather_rate} wood.{gather_rate} stone.{gather_rate} metal.{gather_rate}</Rates>',
                    f'    <MaxCapacity>{gather_capacity}</MaxCapacity>',
                    '  </ResourceGatherer>'
                ])
            
            # Add garrison
            if float(garrison_capacity) > 0:
                xml_lines.extend([
                    '  <GarrisonHolder>',
                    f'    <Max>{garrison_capacity}</Max>',
                    f'    <Size>10</Size>',
                    f'    <AllowGarrisoning>{allow_garrison}</AllowGarrisoning>',
                    '    <List>false</List>',
                    '  </GarrisonHolder>'
                ])
            
            # Add loot
            xml_lines.extend([
                '  <Loot>',
                f'    <xp>{xp_loot}</xp>',
                f'    <food>0</food>',
                f'    <wood>0</wood>',
                f'    <stone>0</stone>',
                f'    <metal>0</metal>',
                '  </Loot>',
                '  <VisualActor>',
                f'    <Actor>props/units/hellenes/infantry_spearman.xml</Actor>',
                '  </VisualActor>',
                '</Entity>'
            ])
            
            return '\n'.join(xml_lines)
        
        except Exception as e:
            return f"<!-- Error generating XML: {e} -->"
    
    def _preview_xml(self):
        """Show preview of generated XML."""
        xml_content = self._generate_xml()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("XML Preview")
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(xml_content)
        text_edit.setStyleSheet(get_text_edit_style())
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        button_layout = QHBoxLayout()
        copy_btn = QPushButton("📋 Copy to Clipboard")
        copy_btn.setStyleSheet(get_button_style())
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(xml_content))
        button_layout.addWidget(copy_btn)
        
        close_btn = QPushButton("❌ Close")
        close_btn.setStyleSheet(get_button_style())
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.exec()
    
    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "Copied", "XML copied to clipboard")
    
    def _create_unit(self):
        """Create the new unit with current form values."""
        if not self.main_window.project:
            QMessageBox.warning(self, "Warning", "No project loaded")
            return
        
        unit_name = self.unit_name_input.text().strip()
        if not unit_name:
            QMessageBox.warning(self, "Warning", "Please enter a unit name")
            return
        
        # Validate unit name
        if not unit_name.replace('_', '').replace('-', '').isalnum():
            QMessageBox.warning(self, "Warning", "Unit name must contain only letters, numbers, underscores, and hyphens")
            return
        
        try:
            xml_content = self._generate_xml()
            path = f"simulation/templates/units/{unit_name}.xml"
            
            self.main_window.project.add_file(xml_content, path)
            
            QMessageBox.information(self, "Success", f"Unit '{unit_name}' created successfully!")
            
            # Refresh units tab
            self.main_window.units_tab.refresh()
            
            # Ask if user wants to edit the new unit
            reply = QMessageBox.question(
                self, "Edit Unit?",
                f"Would you like to edit '{unit_name}' now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Navigate to units tab and select the new unit
                self.main_window._navigate_to("units")
                # The units tab will need to be refreshed to show the new unit
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create unit: {e}")
    
    def refresh(self):
        """Refresh the tab."""
        pass
    
    def get_help_text(self) -> str:
        """Provide help for the Unit Creator tab."""
        return (
            "Unit Creator Help:\n\n"
            "🎨 Templates:\n"
            "• Choose a template to start with preset values\n"
            "• Templates include: Basic Unit, Archer, Melee Fighter, Cavalry, Structure, Worker, Support, Hero\n"
            "• Templates set basic and advanced stats automatically\n\n"
            "📋 Basic Information:\n"
            "• Unit Internal Name: Technical name (no spaces, use underscores)\n"
            "• Display Name: Name shown to players\n"
            "• Generic Type: Category (e.g., Infantry, Cavalry)\n"
            "• Civilization: Civ code (e.g., athen, spart)\n\n"
            "📊 Quick Stats:\n"
            "• Health: Maximum hit points\n"
            "• Attack: Base attack damage\n"
            "• Defense: Base resistance value\n"
            "• Speed: Movement speed (0 for structures)\n\n"
            "⚙️ Advanced Options:\n"
            "• Click 'Show Advanced Options' for more detailed settings\n"
            "• Cost: Build time, population, resource costs\n"
            "• Combat: Melee/ranged damage, ranges, capture\n"
            "• Movement: Acceleration, terrain passability\n"
            "• Vision: Sight range, fog of war settings\n"
            "• Gather: Resource gathering rates and capacity\n"
            "• Garrison: Garrison capacity and permissions\n\n"
            "✨ Create Unit:\n"
            "• Click 'Create Unit' to generate the XML and add to project\n"
            "• Unit will be saved to simulation/templates/units/\n"
            "• You can then edit it in the Units tab\n\n"
            "👁️ Preview XML:\n"
            "• Click 'Preview XML' to see the generated XML\n"
            "• Copy to clipboard for manual editing\n\n"
            "🔄 Reset Form:\n"
            "• Clear all fields and reset to defaults\n"
            "• Useful when starting over"
        )


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
