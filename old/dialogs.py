"""Dialog windows for the application."""

import time
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QFileDialog, QMessageBox, QMenu, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from settings import AppSettings
from styles import get_tree_style, get_button_style
from version import __version__


class StartupDialog(QDialog):
    """Startup dialog for selecting recent projects."""
    
    def __init__(self):
        super().__init__()
        self.selected_path: Optional[str] = None
        self._setup_ui()
        self._load_recent_projects()
    
    def _setup_ui(self):
        self.setWindowTitle(f"0 A.D. Mod Maker v{__version__} - Welcome")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Welcome card
        welcome_card = QFrame()
        welcome_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d2d3d, stop:1 #383848);
                border-radius: 15px;
                padding: 30px;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_card)
        
        # Header
        title = QLabel("🎮 Welcome to 0 A.D. Mod Maker")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #7b5eff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(title)
        
        subtitle = QLabel("Create and manage your 0 A.D. mods with ease")
        subtitle.setStyleSheet("color: #c0c0d0; font-size: 18px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(subtitle)
        
        welcome_layout.addSpacing(15)
        
        # Feature highlights
        features_layout = QHBoxLayout()
        features_layout.setSpacing(20)
        
        features = [
            ("📁", "Asset Management", "Browse and manage game assets"),
            ("⚔️", "Unit Editor", "Create and customize units"),
            ("🏗️", "Structure Builder", "Design buildings and structures"),
            ("🔬", "Tech Research", "Manage technologies and upgrades")
        ]
        
        for icon, title, desc in features:
            feature_frame = QFrame()
            feature_frame.setStyleSheet("""
                QFrame {
                    background-color: #1a1a2a;
                    border-radius: 10px;
                    padding: 15px;
                }
            """)
            feature_layout = QVBoxLayout(feature_frame)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            feature_layout.addWidget(icon_label)
            
            feature_title = QLabel(title)
            feature_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #7b5eff;")
            feature_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            feature_layout.addWidget(feature_title)
            
            feature_desc = QLabel(desc)
            feature_desc.setStyleSheet("color: #9090a0; font-size: 11px;")
            feature_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            feature_desc.setWordWrap(True)
            feature_layout.addWidget(feature_desc)
            
            features_layout.addWidget(feature_frame)
        
        welcome_layout.addLayout(features_layout)
        layout.addWidget(welcome_card)
        
        layout.addSpacing(20)
        
        # Quick actions section
        actions_label = QLabel("⚡ Quick Actions")
        actions_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        new_mod_btn = QPushButton("✨ Create New Mod")
        new_mod_btn.setStyleSheet(get_button_style(accent=True))
        new_mod_btn.clicked.connect(self.accept)
        new_mod_btn.setToolTip("Create a brand new mod project from scratch")
        new_mod_btn.setMinimumHeight(50)
        actions_layout.addWidget(new_mod_btn)
        
        open_btn = QPushButton("📂 Open Existing Mod")
        open_btn.setStyleSheet(get_button_style())
        open_btn.clicked.connect(self._open_other_mod)
        open_btn.setToolTip("Open an existing .adcreator project file")
        open_btn.setMinimumHeight(50)
        actions_layout.addWidget(open_btn)
        
        skip_btn = QPushButton("⏭️ Explore App")
        skip_btn.setStyleSheet(get_button_style())
        skip_btn.clicked.connect(self.reject)
        skip_btn.setToolTip("Open the main window without loading a project")
        skip_btn.setMinimumHeight(50)
        actions_layout.addWidget(skip_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        layout.addSpacing(20)
        
        # Recent projects section
        recent_label = QLabel("🕒 Recent Projects")
        recent_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(recent_label)
        
        self.recent_tree = QTreeWidget()
        self.recent_tree.setHeaderLabels(["📁 Mod Name", "📍 Location", "📅 Last Opened"])
        self.recent_tree.setStyleSheet(get_tree_style())
        self.recent_tree.itemDoubleClicked.connect(self._on_recent_double_click)
        self.recent_tree.setAlternatingRowColors(True)
        self.recent_tree.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.recent_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.recent_tree.customContextMenuRequested.connect(self._show_context_menu)
        self.recent_tree.setToolTip("Double-click to open • Right-click for options")
        self.recent_tree.setMinimumHeight(200)
        layout.addWidget(self.recent_tree)
        
        # Empty state message
        self.empty_label = QLabel("🚀 No recent projects found.\n\nCreate your first mod to get started!")
        self.empty_label.setStyleSheet("color: #9090a0; font-size: 16px; padding: 30px;")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)
        
        # Help tip
        help_label = QLabel("💡 Tip: Use keyboard shortcuts for faster navigation (see Help menu)")
        help_label.setStyleSheet("color: #707080; font-size: 12px; font-style: italic;")
        help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(help_label)
    
    def _load_recent_projects(self):
        settings = AppSettings()
        recent_projects = settings.recent_projects
        
        if not recent_projects:
            self.recent_tree.setVisible(False)
            self.empty_label.setVisible(True)
            return
        
        self.recent_tree.setVisible(True)
        self.empty_label.setVisible(False)
        
        for entry in recent_projects:
            path = entry.get("path", "")
            if not path:
                continue
            exists = Path(path).exists() and path.endswith('.adcreator')
            
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
                item.setForeground(2, QColor("#707080"))
                item.setText(0, f"❌ {entry.get('label', 'Unknown')} (Not Found)")
    
    def _on_recent_double_click(self, item: QTreeWidgetItem, column: int):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path and Path(path).exists():
            self.selected_path = path
            self.accept()
    
    def _open_other_mod(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Project File",
            str(Path.home()),
            "AD Creator Projects (*.adcreator);;All Files (*)"
        )
        
        if file_path:
            if file_path.endswith('.adcreator'):
                self.selected_path = file_path
                self.accept()
            else:
                QMessageBox.warning(self, "Invalid Project", "Selected file is not a valid .adcreator project.")
    
    def _show_context_menu(self, position):
        """Show context menu for recent projects."""
        item = self.recent_tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        open_action = menu.addAction("📂 Open")
        open_action.triggered.connect(lambda: self._on_recent_double_click(item, 0))
        
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path and Path(path).exists():
            menu.addSeparator()
            remove_action = menu.addAction("🗑️ Remove from Recent")
            remove_action.triggered.connect(lambda: self._remove_recent(path))
        
        menu.exec(self.recent_tree.mapToGlobal(position))
    
    def _remove_recent(self, path: str):
        """Remove a project from recent list."""
        settings = AppSettings()
        settings.remove_recent(path)
        self.recent_tree.clear()
        self._load_recent_projects()
