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
    QLabel,
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

        layout.addWidget(self.collage_button)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

        # Connect signals
        self.gallery_preview.image_selected_signal.connect(self.image_selected)
        self.gallery_preview.double_click_signal.connect(self.image_double_clicked)
        self.gallery_preview.show_collage_button_signal.connect(
            self.show_collage_button
        )

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
