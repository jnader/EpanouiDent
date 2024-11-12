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
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtCore import QSize, Qt

from ui.pages.image_view_and_edit import ImageViewEdit
from ui.pages.gallery import GalleryPage
from ui.widgets.collage import CollagePreview

from backend.background_downloader import ImageDownloaderThread
from backend.airmpt_log_analyzer import AirMTPLogAnalyzer


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

        # Image Downloader Thread
        self.downloader_thread = ImageDownloaderThread()
        self.downloader_thread.start()

        self.airmtp_log_analyzer_thread = AirMTPLogAnalyzer()
        self.airmtp_log_analyzer_thread.camera_detected.connect(self.camera_detected)
        self.airmtp_log_analyzer_thread.download_signal.connect(self.picture_downloaded)
        self.airmtp_log_analyzer_thread.start()

    def camera_detected(self, camera_model: str, serial_number: str):
        """Handler of camera detection signal.
        
        Args:
            camera_model (str): Model of the camera
            serial_number (str): Serial number of detected camera
        """
        print(camera_model, serial_number)

    def picture_downloaded(self, downloaded_picture_path: str):
        """Handler of downloaded picture signal.
        
        Args:
            downloaded_picture_path (str): Path to the downloaded picture.
        """
        print(downloaded_picture_path)

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

        tab = CollagePreview(list_of_files)
        self.tab_widget.addTab(tab, f"Collage {self.opened_tab}")
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
        self.opened_tab += 1

    def receive_photo(self, request):
        """Receive photo via HTTP"""
        print("photo received")
