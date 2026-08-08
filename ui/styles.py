"""UI styling constants and helpers."""

from PyQt6.QtGui import QPalette, QColor


class Colors:
    """Color constants for the UI."""
    BG_DARK = QColor("#2d2d3d")
    BG_PANEL = QColor("#383848")
    BG_INPUT = QColor("#1a1a2a")
    BG_INPUT_FOCUS = QColor("#252535")
    FG_PRIMARY = QColor("#ffffff")
    FG_SECONDARY = QColor("#c0c0d0")
    FG_MUTED = QColor("#9090a0")
    ACCENT = QColor("#7b5eff")
    ACCENT_HOVER = QColor("#9a7cff")
    ACCENT_PRESSED = QColor("#6a4ce0")
    BORDER = QColor("#6a6a8a")
    SUCCESS = QColor("#4ade80")
    WARNING = QColor("#fbbf24")
    ERROR = QColor("#ef4444")


def get_dark_theme_palette() -> QPalette:
    """Get a dark theme palette for PyQt6."""
    palette = QPalette()
    
    palette.setColor(QPalette.ColorRole.Window, Colors.BG_DARK)
    palette.setColor(QPalette.ColorRole.WindowText, Colors.FG_PRIMARY)
    palette.setColor(QPalette.ColorRole.Base, Colors.BG_INPUT)
    palette.setColor(QPalette.ColorRole.AlternateBase, Colors.BG_PANEL)
    palette.setColor(QPalette.ColorRole.ToolTipBase, Colors.FG_PRIMARY)
    palette.setColor(QPalette.ColorRole.ToolTipText, Colors.FG_PRIMARY)
    palette.setColor(QPalette.ColorRole.Text, Colors.FG_PRIMARY)
    palette.setColor(QPalette.ColorRole.Button, Colors.BG_PANEL)
    palette.setColor(QPalette.ColorRole.ButtonText, Colors.FG_PRIMARY)
    palette.setColor(QPalette.ColorRole.BrightText, Colors.FG_PRIMARY)
    palette.setColor(QPalette.ColorRole.Link, Colors.ACCENT)
    palette.setColor(QPalette.ColorRole.Highlight, Colors.ACCENT)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    
    return palette


def get_button_style(accent: bool = False) -> str:
    """Get button stylesheet."""
    if accent:
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
    else:
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


def get_input_style() -> str:
    """Get input field stylesheet."""
    return """
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
    """


def get_tree_style() -> str:
    """Get tree widget stylesheet."""
    return """
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
    """
