"""
Main page of EpanouiDent.
"""

from typing import List

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
from PySide6.QtHttpServer import QHttpServer
from PySide6.QtNetwork import QHostAddress

from ui.pages.image_view_and_edit import ImageViewEdit
from ui.pages.gallery import GalleryPage
from ui.widgets.before_after_widget import BeforeAfter
from ui.widgets.collage import CollagePreview


class MainPage(QMainWindow):
    """Main page of the software.
    This page will load the Gallery Page first and will handle signals sent from
    Gallery Page to create new ImageEdit tabs/pages.
    """

    gallery_page: GalleryPage
    opened_tab: int

    def __init__(self, title: str, size: QSize, base_path: str):
        """Constructor"""
        super().__init__()

        # self.http_server = QHttpServer()
        # self.http_server.route("/photo", self.receive_photo)
        # ip_address = QHostAddress("192.168.209.143")
        # port = 2560
        # if self.http_server.listen(ip_address, port):
        #     print(f"Server is running on {ip_address.toString()}:{port}")
        # else:
        #     print("Failed to start the server")

        self.opened_tab = 0
        self.base_path = base_path
        self.setWindowTitle(title)
        # self.setFixedSize(size)
        self.setMinimumSize(size)

        h_layout = QHBoxLayout()

        self.gallery_page = GalleryPage()
        self.gallery_page.double_click_signal.connect(self.load_image)
        self.gallery_page.collage_click_signal.connect(self.load_collage)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setTabPosition(QTabWidget.West)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.addTab(
            self.gallery_page,
            "Gallery",
        )
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
        tab = ImageViewEdit(filename)
        tab.image_saved_signal.connect(self.send_update_gallery_signal)
        self.tab_widget.addTab(tab, f"Image {self.opened_tab}")
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
        self.opened_tab += 1

    def close_tab(self, index: int):
        """Close tab requested

        Args:
            index (int): Index of the tab being closed
        """
        if index == 0:
            return
        self.tab_widget.removeTab(index)
        self.opened_tab -= 1

    def send_update_gallery_signal(self, dir_name: str):
        """Send signal to Gallery to update with new save images."""

        if self.gallery_page.directory_name == dir_name:
            self.gallery_page.sync_diff()

    def load_collage(self, list_of_files: List[str]):
        """Load a new tab in self.tab_widget containing the collage selected."""
        if len(list_of_files) > 4:
            return

        # tab = BeforeAfter(
        #     image_path_after=list_of_files[0],
        #     image_path_before=list_of_files[1],
        # )
        tab = CollagePreview(list_of_files)
        self.tab_widget.addTab(tab, f"Collage {self.opened_tab}")
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
        self.opened_tab += 1

    def receive_photo(self, request):
        """Receive photo via HTTP"""
        print("photo received")
