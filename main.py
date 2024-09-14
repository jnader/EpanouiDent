"""
Main entry of the program.
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication

from ui.pages.main_page import MainPage

import os
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    base_path = os.path.join(os.path.abspath(__file__), os.path.dirname(__file__))
    window = MainPage(title="EpanouiDent", size=QSize(1280, 800), base_path=base_path)
    window.show()
    app.exec()
