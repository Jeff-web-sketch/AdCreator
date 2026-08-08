#!/usr/bin/env python3
"""Simple test of the GUI."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QLabel, QWidget

def test():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Test")
    layout = QVBoxLayout(window)
    layout.addWidget(QLabel("Test GUI"))
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    test()
