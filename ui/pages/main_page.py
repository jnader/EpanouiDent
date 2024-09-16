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
from ui.pages.gallery import GalleryPage
from ui.widgets.before_after_widget import BeforeAfter
from ui.widgets.gallery import Gallery


class MainPage(QMainWindow):
    def __init__(self, title: str, size: QSize, base_path: str):
        super().__init__()
        self.base_path = base_path
        self.setWindowTitle(title)
        self.setFixedSize(size)

        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.West)
        # Embed in QScrollArea
        self.tab_widget.addTab(
            # Gallery("/home/joudy/Pictures/Manuel & Tanias wedding/"),
            GalleryPage(),
            "Gallery",
        )
        self.tab_widget.addTab(ImageProcessor(self.base_path), "Image Proc.")
        # self.tab_widget.addTab(
        #     BeforeAfter(
        #         image_path_after="<path-to-old-image>",
        #         image_path_before="<path-to-new-image>",
        #     ),
        #     "Before/After",
        # )
        h_layout.addWidget(self.tab_widget)

        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_widget = QWidget()
        main_widget.setLayout(h_layout)
        self.setCentralWidget(main_widget)

