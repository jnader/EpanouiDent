"""
Main page of EpanouiDent
"""

from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget, QTextEdit, QStackedWidget, QTabWidget, QStackedLayout
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from PySide6.QtCore import QSize

from ui.pages.image_processing import ImageProcessor
from ui.pages.user_data_menu import UserData

class MainPage(QMainWindow):
    def __init__(self, title : str, size : QSize):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(size)

        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.West)
        self.tab_widget.setDocumentMode(True)
        # Add as many pages (classes) as the software needs here
        # Images should be added in .css format (instead of tab1, tab2 strings...)
        self.tab_widget.addTab(QPushButton("tab1"), "tab1")
        self.tab_widget.addTab(QPushButton("tab2"), "tab2")
        self.tab_widget.addTab(ImageProcessor(), "Image Proc.")
        self.tab_widget.addTab(UserData(), "User data")
        h_layout.addWidget(self.tab_widget)

        main_widget = QWidget()
        main_widget.setLayout(h_layout)
        self.setCentralWidget(main_widget)

