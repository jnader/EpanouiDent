"""
Main page of EpanouiDent.
"""

from typing import List
import os
import shutil

from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QWidget,
    QTextEdit,
    QCompleter,
    QLabel,
    QFileDialog,
    QStackedWidget,
    QToolBar,
    QMenuBar,
    QRadioButton,
    QTabWidget,
    QStackedLayout,
    QMessageBox,

)
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from PySide6.QtCore import QSize, Qt, QStringListModel

from ui.pages.image_view_and_edit import ImageViewEdit
from ui.pages.gallery import GalleryPage
from ui.widgets.gallery import Gallery
from ui.widgets.collage import CollagePreview

from backend.background_downloader import ImageDownloaderThread
from backend.airmtp_log_analyzer import AirMTPLogAnalyzer

from backend.utils import match_pattern_in_list


class MainPage(QMainWindow):
    """Main page of the software.
    This page will load the Gallery Page first and will handle signals sent from
    Gallery Page to create new ImageEdit tabs/pages.
    """

    gallery_page: GalleryPage
    opened_tab: int
    camera_model: str
    camera_serial: str

    def __init__(self, title: str, size: QSize, base_path: str):
        """Constructor"""
        super().__init__()

        if not "EPANOUIDENT_DEFAULT_PATH" in os.environ:
            self.default_path = input("Please select the default path: ")
            os.environ["EPANOUIDENT_DEFAULT_PATH"] = self.default_path
        else:
            self.default_path = os.environ["EPANOUIDENT_DEFAULT_PATH"]

        self.folders_list = os.listdir(self.default_path)

        self.opened_tab = 0
        self.base_path = base_path
        self.setWindowTitle(title)
        # self.setFixedSize(size)
        self.setMinimumSize(size)

        v_layout = QVBoxLayout()

        self.gallery_page = None

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setTabPosition(QTabWidget.West)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.setStyleSheet(
            "background-image: url(logo.png); background-repeat: no-repeat; background-position: center;"
        )
        v_layout.addWidget(self.tab_widget, stretch=29)

        h_layout = QHBoxLayout()
        label = QLabel("Folder: ")
        self.path_search = QTextEdit("")
        font_size = self.path_search.fontInfo().pixelSize()
        self.path_search.setFixedHeight(2.5 * font_size)
        self.path_search.textChanged.connect(self.path_search_text_change)
        self.path_cleared = False
        self.completer = QCompleter(self.path_search)
        self.completer.setWidget(self.path_search)  # Attach completer to QTextEdit
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.model = QStringListModel()
        self.completer.setModel(self.model)
        self.completer.activated.connect(self.on_match_selected)

        self.button_open = QPushButton("Open Folder")
        self.button_open.setFixedHeight(self.path_search.height() - 10)
        self.button_open.pressed.connect(self.open_folder_pressed)

        self.button_create = QPushButton("Create Folder")
        self.button_create.setFixedHeight(self.path_search.height() - 10)
        self.button_create.pressed.connect(self.create_folder_pressed)

        self.label_camera_model = QLabel("Camera Model: ")
        self.label_camera_serial = QLabel("Camera Serial: ")
        self.camera_detected_indicator = QRadioButton()
        self.camera_detected_indicator.setStyleSheet(
            "QRadioButton::indicator:checked{"
            "width:12px;height:12px;"
            "border-radius:7px;"
            "background-color:green;"
            "border:2px solid yellow;"
            "}"
            "QRadioButton::indicator:unchecked{"
            "width:8px;height:8px;"
            "border-radius:5px;"
            "background-color: transparent;"
            "border:2px solid gray;"
            "}"
        )
        self.camera_detected_indicator.setChecked(False)
        h_layout.addWidget(label)
        h_layout.addWidget(self.path_search)
        h_layout.addWidget(self.button_create)
        h_layout.addWidget(self.button_open)

        # Camera status widget
        camera_v_layout = QVBoxLayout()
        camera_v_layout.addWidget(self.camera_detected_indicator)
        camera_v_layout.addWidget(self.label_camera_model)
        camera_v_layout.addWidget(self.label_camera_serial)
        camera_status_widget = QWidget()
        camera_status_widget.setLayout(camera_v_layout)

        h_layout.addWidget(camera_status_widget)

        bottom_widget = QWidget()
        bottom_widget.setLayout(h_layout)
        v_layout.addWidget(
            bottom_widget, stretch=1, alignment=Qt.AlignmentFlag.AlignBottom
        )

        v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_widget = QWidget()
        main_widget.setLayout(v_layout)
        self.setCentralWidget(main_widget)

        # Image Downloader Thread
        self.downloader_thread = ImageDownloaderThread()
        self.downloader_thread.start()

        self.airmtp_log_analyzer_thread = AirMTPLogAnalyzer()
        self.airmtp_log_analyzer_thread.camera_detected.connect(self.camera_detected)
        self.airmtp_log_analyzer_thread.camera_disconnected.connect(
            self.camera_disconnected
        )
        self.airmtp_log_analyzer_thread.download_signal.connect(self.picture_downloaded)
        self.airmtp_log_analyzer_thread.start()

    def camera_detected(self, camera_model: str, serial_number: str):
        """Handler of camera detection signal.

        Args:
            camera_model (str): Model of the camera
            serial_number (str): Serial number of detected camera
        """
        self.camera_model = camera_model
        self.camera_serial = serial_number
        self.camera_detected_indicator.setChecked(True)
        self.label_camera_model.setText(f"Model: {self.camera_model}")
        self.label_camera_serial.setText(f"Serial: {self.camera_serial}")

    def camera_disconnected(self, flag: bool):
        """Handler for camera disconnection

        Args:
            flag (bool): True when camera is disconnected
        """
        self.camera_model = ""
        self.camera_serial = ""
        self.camera_detected_indicator.setChecked(False)
        self.label_camera_model.setText(f"Model: {self.camera_model}")
        self.label_camera_serial.setText(f"Serial: {self.camera_serial}")

    def picture_downloaded(self, downloaded_picture_path: str):
        """Handler of downloaded picture signal.

        Args:
            downloaded_picture_path (str): Path to the downloaded picture.
        """
        if self.gallery_page and self.gallery_page.directory_name:
            # Copy file to current directory
            if os.path.exists(downloaded_picture_path):
                shutil.move(
                    downloaded_picture_path,
                    os.path.join(
                        self.gallery_page.directory_name,
                        os.path.basename(downloaded_picture_path),
                    ),
                )
                self.gallery_page.sync_diff()

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
        if index == 0 and self.opened_tab == 0:
            self.tab_widget.setStyleSheet(
                "background-image: url(logo.png); background-repeat: no-repeat; background-position: center;"
            )
            self.tab_widget.removeTab(index)
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

    def path_search_text_change(self):
        """Search path text edit change

        Args:
            text (str): Current text in QTextEdit
        """
        if (
            not self.path_cleared
            and "Search for a folder here..." in self.path_search.toPlainText()
        ):
            self.path_cleared = True
            self.path_search.setText("")
            self.path_search.clear()

        text = self.path_search.toPlainText().strip()
        if os.path.exists(self.default_path) and text != "":
            matches = [
                os.path.join(self.default_path, f) for f in os.listdir(self.default_path)
                if text.lower() in f.lower()
            ]

            if len(matches) >= 1:
                self.show_completions(matches)
            else:
                self.completer.popup().hide()

    def on_match_selected(self, selected_match):
        """Event when the user selects a directory to load
        """
        self.path_search.setPlainText(os.path.basename(selected_match))
        self.completer.popup().hide()
        self.directory_name = selected_match

        # Add Gallery widget in TabWidget
        self.tab_widget.setStyleSheet("")

        if not self.gallery_page:
            self.gallery_page = GalleryPage()
            self.gallery_page.double_click_signal.connect(self.load_image)
            self.gallery_page.collage_click_signal.connect(self.load_collage)

        self.tab_widget.insertTab(
            0,
            self.gallery_page,
            "Gallery",
        )
        self.gallery_page.directory_name = self.directory_name
        self.gallery_page.gallery_preview.update_directory(self.directory_name)

    def open_folder_pressed(self):
        """Button pressed event
        Load directory
        """
        dialog = QFileDialog(self)
        self.directory_name = dialog.getExistingDirectory(
            self, "Open Folder", os.path.expanduser("~")
        )

        dialog.hide()

        if not self.gallery_page:
            self.tab_widget.setStyleSheet("")
            self.gallery_page = GalleryPage()
            self.gallery_page.double_click_signal.connect(self.load_image)
            self.gallery_page.collage_click_signal.connect(self.load_collage)

        self.tab_widget.insertTab(
            0,
            self.gallery_page,
            "Gallery",
        )
        self.gallery_page.directory_name = self.directory_name
        self.gallery_page.gallery_preview.update_directory(self.directory_name)

    def show_completions(self, matches):
        self.model.setStringList(matches)  # Set matched items to the QCompleter
        self.completer.complete()  # Show the completion popup

    def create_folder_pressed(self):
        """Create folder if user asks to"""
        text = self.path_search.toPlainText()

        new_directory = os.path.join(self.default_path, text)

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Create new folder.")
        msg_box.setText("Do you want to proceed? Make sure the folder doesn't already exist.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        # Show the message box and get the user's response
        response = msg_box.exec_()

        # Handle the response
        if response == QMessageBox.Yes:
            os.makedirs(new_directory)#, exist_ok=True)

            self.update_folders_list()

            if not self.gallery_page:
                self.tab_widget.setStyleSheet("")
                self.gallery_page = GalleryPage()
                self.gallery_page.double_click_signal.connect(self.load_image)
                self.gallery_page.collage_click_signal.connect(self.load_collage)

            self.tab_widget.insertTab(
                0,
                self.gallery_page,
                "Gallery",
            )
            self.directory_name = new_directory
            self.gallery_page.directory_name = new_directory
            self.gallery_page.gallery_preview.update_directory(new_directory)

        elif response == QMessageBox.No:
            return

    def update_folders_list(self):
        """Updates folder list in case new folders are created"""
        self.folders_list = os.listdir(self.default_path)
