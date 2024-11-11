"""
Page containing image gallery widget and directory selector, etc...
"""

import os
from PySide6.QtCore import QFileSystemWatcher, Signal
from PySide6.QtWidgets import (
    QWidget,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QTextEdit,
    QPushButton,
    QSizePolicy,
)
from PySide6.QtGui import QIcon
from typing import List

from ui.widgets.gallery import Gallery
from backend.utils import match_pattern_in_list

class GalleryPage(QWidget):
    """Gallery image page containing a scrolling area in which
    we have an image gallery and a directory selector.

    Args:
        QWidget (_type_): _description_
    """

    double_click_signal = Signal(str)
    collage_click_signal = Signal(list)

    scroll_area: QScrollArea
    gallery_preview: Gallery
    button_explore: QPushButton

    def __init__(self):
        """Constructor"""
        super().__init__()

        self.directory_name = None
        self.directory_watcher = None

        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        self.collage_button = QPushButton("Collage")
        self.collage_button.setVisible(False)
        self.collage_button.clicked.connect(self.create_collage_page)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Make the scroll area resizable
        self.gallery_preview = Gallery("")
        self.scroll_area.setWidget(self.gallery_preview)

        self.button_explore = QPushButton("Open Folder")
        self.button_explore.setIcon(QIcon.fromTheme("folder"))
        self.button_explore.pressed.connect(self.button_pressed)

        self.path_search = QTextEdit("")
        font_size = self.path_search.fontInfo().pixelSize()
        self.path_search.setFixedHeight(2.5 * font_size)
        self.path_search.textChanged.connect(self.path_search_text_change)
        self.path_cleared = False
        h_layout.addWidget(self.path_search)
        h_layout.addWidget(self.button_explore)
        widget = QWidget()
        widget.setFixedHeight(2.5 * font_size)
        widget.setLayout(h_layout)

        layout.addWidget(self.collage_button)
        layout.addWidget(self.scroll_area)
        layout.addWidget(widget)

        self.setLayout(layout)

        # Connect signals
        self.gallery_preview.image_selected_signal.connect(self.image_selected)
        self.gallery_preview.double_click_signal.connect(self.image_double_clicked)
        self.gallery_preview.show_collage_button_signal.connect(
            self.show_collage_button
        )

        if not "EPANOUIDENT_DEFAULT_PATH" in os.environ:
            self.default_path = "Pictures" # should be in an environment variable?
        else:
            print("Using path from environment variable)")
            self.default_path = os.environ["EPANOUIDENT_DEFAULT_PATH"]

        self.folders_list = os.listdir(self.default_path)

    def button_pressed(self):
        """Button pressed event
        Load directory
        """
        dialog = QFileDialog(self)
        self.directory_name = dialog.getExistingDirectory(
            self, "Open Folder", os.path.expanduser("~")
        )

        dialog.hide()

        print(self.directory_name)
        self.directory_watcher = QFileSystemWatcher(self.directory_name)
        self.directory_watcher.directoryChanged.connect(self.directory_changed_event)
        self.gallery_preview.update_directory(self.directory_name)

    def image_selected(self, list_of_names: List[str]):
        """Image selection event."""
        self.images_selected = list_of_names

    def image_double_clicked(self, filename):
        """Image double clicked event."""
        self.double_click_signal.emit(filename)

    def sync_diff(self):
        """Sync gallery widget for new files in the directory."""
        self.gallery_preview.sync_diff()

    def directory_changed_event(self, files):
        """Directory changed event"""
        print(f"Directory changed {files}")
        self.gallery_preview.update_directory(self.directory_name)

    def show_collage_button(self, state: bool):
        """Show collage button signal callback.

        Args:
            state (bool): State sent from GalleryPreview object.
        """
        if state:
            self.collage_button.setVisible(True)

        else:
            self.collage_button.setVisible(False)

    def create_collage_page(self):
        """Collage button clicked"""
        self.collage_click_signal.emit(self.images_selected)

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

        text = self.path_search.toPlainText()
        potential_matches = match_pattern_in_list(self.folders_list, text)

        if potential_matches and len(potential_matches) == 1:
            self.directory_name = os.path.join(self.default_path, potential_matches[0])
            self.gallery_preview.update_directory(self.directory_name)
