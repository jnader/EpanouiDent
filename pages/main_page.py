"""
Main page of EpanouiDent
"""

from PySide2.QtWidgets import QMainWindow, QPushButton, QWidget, QTextEdit, QStackedWidget, QTabWidget, QStackedLayout
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout
from PySide2.QtCore import QSize

from pages.image_processing import ImageProcessor

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
        h_layout.addWidget(self.tab_widget)

        main_widget = QWidget()
        main_widget.setLayout(h_layout)
        self.setCentralWidget(main_widget)

