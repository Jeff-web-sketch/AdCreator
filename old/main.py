#!/usr/bin/env python3
"""
0 A.D. Mod Maker - Modern Version
===================================
A clean, modern application for creating and managing 0 A.D. mods.

Requirements:
    Python 3.9+
    PyQt6 (pip install PyQt6)

Usage:
    python main.py
"""

import sys
from pathlib import Path

# Ensure local imports work
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt6.QtCore import Qt

from dialogs import StartupDialog
from main_window import MainWindow


def run():
    """Entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Show startup dialog
    startup = StartupDialog()
    dialog_result = startup.exec()
    
    # Create main window
    window = MainWindow()
    window.show()
    
    if dialog_result == QDialog.DialogCode.Accepted:
        selected_path = startup.selected_path
        if selected_path:
            # Load selected project
            try:
                from mod import ModProject
                window.project = ModProject(Path(selected_path))
                window.project.load()
                window.settings.last_mod_dir = str(window.project.project_path)
                window.settings.add_recent(str(window.project.project_path), window.project.info.label)
                window.settings.save()
                window._update_status_bar(f"Loaded project: {window.project.project_name}")
                window._refresh_all_tabs()
            except Exception as e:
                QMessageBox.critical(window, "Error", f"Failed to load project: {e}")
        else:
            # Create new mod
            window.action_new_mod()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
