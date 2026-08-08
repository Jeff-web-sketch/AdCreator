"""Dialog windows for the application."""

import time
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.settings import AppSettings
from ui.styles import get_tree_style, get_button_style


class StartupDialog(QDialog):
    """Startup dialog for selecting recent projects."""
    
    def __init__(self):
        super().__init__()
        self.selected_path: Optional[str] = None
        self._setup_ui()
        self._load_recent_projects()
    
    def _setup_ui(self):
        self.setWindowTitle("0 A.D. Mod Maker - Welcome")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        title = QLabel("🎮 0 A.D. Mod Maker")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #7b5eff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Select a recent project or create a new mod")
        subtitle.setStyleSheet("color: #c0c0d0; font-size: 16px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(15)
        
        # Help text
        help_text = QLabel("💡 Tip: Double-click a project to open it quickly")
        help_text.setStyleSheet("color: #9090a0; font-size: 13px; font-style: italic;")
        help_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(help_text)
        
        layout.addSpacing(15)
        
        # Recent projects
        recent_label = QLabel("🕒 Recent Projects")
        recent_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b5eff;")
        layout.addWidget(recent_label)
        
        self.recent_tree = QTreeWidget()
        self.recent_tree.setHeaderLabels(["📁 Mod Name", "📍 Location", "📅 Last Opened"])
        self.recent_tree.setStyleSheet(get_tree_style())
        self.recent_tree.itemDoubleClicked.connect(self._on_recent_double_click)
        self.recent_tree.setAlternatingRowColors(True)
        self.recent_tree.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.recent_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.recent_tree.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.recent_tree)
        
        # Empty state message
        self.empty_label = QLabel("No recent projects found. Create your first mod to get started!")
        self.empty_label.setStyleSheet("color: #9090a0; font-size: 14px; padding: 20px;")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        new_mod_btn = QPushButton("✨ Create New Mod")
        new_mod_btn.setStyleSheet(get_button_style(accent=True))
        new_mod_btn.clicked.connect(self.accept)
        new_mod_btn.setToolTip("Create a brand new mod project from scratch")
        button_layout.addWidget(new_mod_btn)
        
        open_btn = QPushButton("📂 Open Other Mod")
        open_btn.setStyleSheet(get_button_style())
        open_btn.clicked.connect(self._open_other_mod)
        open_btn.setToolTip("Open an existing .adcreator project file")
        button_layout.addWidget(open_btn)
        
        skip_btn = QPushButton("⏭️ Skip to Main Window")
        skip_btn.setStyleSheet(get_button_style())
        skip_btn.clicked.connect(self.reject)
        skip_btn.setToolTip("Open the main window without loading a project")
        button_layout.addWidget(skip_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def _load_recent_projects(self):
        settings = AppSettings()
        for entry in settings.recent_projects:
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
    
    def _on_recent_double_click(self, item: QTreeWidgetItem, column: int):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path and Path(path).exists():
            self.selected_path = path
            self.accept()
    
    def _open_other_mod(self):
        from PyQt6.QtWidgets import QFileDialog
        
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
