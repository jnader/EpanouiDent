"""
Main page of EpanouiDent.
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QWidget,
    QTextEdit,
    QStackedWidget,
    QToolBar,
    QMenuBar,
    QTabWidget,
    QStackedLayout,
    QMessageBox,
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from PySide6.QtCore import QSize, Qt

from ui.pages.image_processing import ImageProcessor
from ui.pages.user_data_menu import UserData
from ui.widgets.before_after_widget import BeforeAfter


class MainPage(QMainWindow):
    def __init__(self, title: str, size: QSize, base_path: str):
        super().__init__()
        self.base_path = base_path
        self.setWindowTitle(title)
        self.setFixedSize(size)

        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.South)
        self.tab_widget.setDocumentMode(True)
        # Add as many pages (classes) as the software needs here
        # Images should be added in .css format (instead of tab1, tab2 strings...)
        # self.tab_widget.addTab(QPushButton("tab1"), "tab1")
        # self.tab_widget.addTab(QPushButton("tab2"), "tab2")
        self.tab_widget.addTab(ImageProcessor(self.base_path), "Image Proc.")
        self.tab_widget.addTab(UserData(), "User data")
        self.tab_widget.addTab(
            BeforeAfter(
                image_path_after="/home/joudy/Pictures/images/frame_0_right.pgm",
                image_path_before="/home/joudy/Pictures/images/frame_1_left.pgm",
            ),
            "Before/After",
        )
        h_layout.addWidget(self.tab_widget)

        toolbar = QToolBar(parent=self)
        toolbar.setFloatable(True)

        button_action = QAction("Your button", self)
        button_action.setStatusTip("Button Action")
        button_action.triggered.connect(self.hi)
        toolbar.addAction(button_action)

        # menu_bar = QMenuBar(self)
        # menu_bar.addAction("action1")
        # menu_bar.addAction("action2")

        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_widget = QWidget()
        main_widget.setLayout(h_layout)
        self.setCentralWidget(main_widget)
        self.addToolBar(toolbar)

    def hi(self):
        """Testing actions"""
        msgbox = QMessageBox(text="Action triggered")
        msgbox.exec()
