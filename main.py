
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication
from ui.pages.main_page import MainPage

import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainPage(title="Hello world", size=QSize(1280, 800))
    window.show()
    app.exec_()