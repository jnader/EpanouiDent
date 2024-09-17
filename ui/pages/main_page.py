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

from ui.pages.image_view_and_edit import ImageViewEdit
from ui.pages.gallery import GalleryPage
from ui.widgets.before_after_widget import BeforeAfter


class MainPage(QMainWindow):
    """Main page of the software.
    This page will load the Gallery Page first and will handle signals sent from
    Gallery Page to create new ImageEdit tabs/pages.
    """

    gallery_page: GalleryPage

    def __init__(self, title: str, size: QSize, base_path: str):
        """Constructor"""
        super().__init__()
        self.base_path = base_path
        self.setWindowTitle(title)
        self.setFixedSize(size)

        h_layout = QHBoxLayout()

        self.gallery_page = GalleryPage()
        self.gallery_page.double_click_signal.connect(self.load_image)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.West)
        self.tab_widget.addTab(
            self.gallery_page,
            "Gallery",
        )
        # self.tab_widget.addTab(ImageViewEdit(self.base_path), "Image Proc.")
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

    def load_image(self, filename: str):
        """Loads a new tab in self.tab_widget containing the image selected.

        Args:
            filename (str): File name to open in ImageViewerEdit.
        """
        self.tab_widget.addTab(ImageViewEdit(filename), "Image 1")
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
