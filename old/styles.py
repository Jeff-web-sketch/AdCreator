"""UI styling for the application."""

from PyQt6.QtGui import QPalette, QColor


def get_dark_theme_palette():
    """Get a dark theme palette for the application."""
    palette = QPalette()
    
    # Window
    palette.setColor(QPalette.ColorRole.Window, QColor("#1a1a2a"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
    
    # Base (text editors, etc.)
    palette.setColor(QPalette.ColorRole.Base, QColor("#2d2d3d"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#383848"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
    
    # Button
    palette.setColor(QPalette.ColorRole.Button, QColor("#2d2d3d"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
    
    # Highlight
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#7b5eff"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    
    return palette


def get_button_style(accent: bool = False) -> str:
    """Get CSS style for buttons."""
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
            QPushButton:disabled {
                background-color: #5a5a7a;
                color: #9090a0;
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
            QPushButton:disabled {
                background-color: #2d2d3d;
                border-color: #5a5a7a;
                color: #9090a0;
            }
        """


def get_tree_style() -> str:
    """Get CSS style for tree widgets."""
    return """
        QTreeWidget {
            background-color: #2d2d3d;
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
        QTreeWidget::item:selected:hover {
            background-color: #8b6fff;
        }
        QTreeWidget::branch {
            background-color: transparent;
        }
        QTreeWidget::branch:has-children {
            background-color: transparent;
        }
        QTreeWidget::branch:has-children:closed {
            background-color: transparent;
        }
        QTreeWidget::branch:has-children:open {
            background-color: transparent;
        }
        QTreeWidget::header {
            background-color: #383848;
            color: #7b5eff;
            font-weight: bold;
            padding: 8px;
            border: none;
            border-bottom: 2px solid #4a4a6a;
        }
        QTreeWidget::header::section {
            background-color: transparent;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
    """


def get_tab_widget_style() -> str:
    """Get CSS style for tab widgets."""
    return """
        QTabWidget::pane {
            background-color: #1a1a2a;
            border: 2px solid #4a4a6a;
            border-radius: 8px;
        }
        QTabBar::tab {
            background-color: #2d2d3d;
            color: #c0c0d0;
            padding: 12px 24px;
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
            background-color: #383848;
            border-color: #7b5eff;
        }
    """


def get_group_box_style() -> str:
    """Get CSS style for group boxes."""
    return """
        QGroupBox {
            background-color: #2d2d3d;
            color: #7b5eff;
            font-weight: bold;
            border: 2px solid #4a4a6a;
            border-radius: 8px;
            margin-top: 12px;
            padding: 12px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
        }
    """


def get_line_edit_style() -> str:
    """Get CSS style for line edits."""
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
        QLineEdit:disabled {
            background-color: #2d2d3d;
            color: #9090a0;
        }
    """


def get_spin_box_style() -> str:
    """Get CSS style for spin boxes."""
    return """
        QSpinBox, QDoubleSpinBox {
            background-color: #1a1a2a;
            color: #ffffff;
            border: 2px solid #4a4a6a;
            border-radius: 6px;
            padding: 6px;
            font-size: 13px;
        }
        QSpinBox:focus, QDoubleSpinBox:focus {
            border-color: #7b5eff;
        }
        QSpinBox::up-button, QDoubleSpinBox::up-button {
            background-color: #383848;
            border: none;
            border-radius: 4px;
            width: 20px;
        }
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            background-color: #383848;
            border: none;
            border-radius: 4px;
            width: 20px;
        }
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
            background-color: #484858;
        }
    """


def get_text_edit_style() -> str:
    """Get CSS style for text edits."""
    return """
        QTextEdit {
            background-color: #1a1a2a;
            color: #ffffff;
            border: 2px solid #4a4a6a;
            border-radius: 8px;
            padding: 12px;
            font-family: monospace;
            font-size: 12px;
        }
        QTextEdit:focus {
            border-color: #7b5eff;
        }
    """


def get_label_style() -> str:
    """Get CSS style for labels."""
    return """
        QLabel {
            color: #c0c0d0;
            font-size: 13px;
        }
    """


def get_check_box_style() -> str:
    """Get CSS style for check boxes."""
    return """
        QCheckBox {
            color: #c0c0d0;
            font-size: 13px;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border: 2px solid #4a4a6a;
            border-radius: 4px;
            background-color: #1a1a2a;
        }
        QCheckBox::indicator:checked {
            background-color: #7b5eff;
            border-color: #7b5eff;
        }
        QCheckBox::indicator:hover {
            border-color: #7b5eff;
        }
    """
