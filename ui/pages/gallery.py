"""
Page containing image gallery widget and directory selector, etc...
"""

import os
from PySide6.QtWidgets import (
    QWidget,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QTextEdit,
    QPushButton,
)
from PySide6.QtGui import QIcon
from typing import List

from ui.widgets.gallery import Gallery


class GalleryPage(QWidget):
    """Gallery image page containing a scrolling area in which
    we have an image gallery and a directory selector.

    Args:
        QWidget (_type_): _description_
    """

    scroll_area: QScrollArea
    gallery_preview: Gallery
    button_explore: QPushButton

    def __init__(self):
        """Constructor"""
        super().__init__()

        layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Make the scroll area resizable
        self.gallery_preview = Gallery("")
        self.scroll_area.setWidget(self.gallery_preview)

        self.button_explore = QPushButton("Open Folder")
        self.button_explore.setIcon(QIcon.fromTheme("folder"))
        self.button_explore.pressed.connect(self.button_pressed)

        layout.addWidget(self.scroll_area)
        layout.addWidget(self.button_explore)

        self.setLayout(layout)

        # Connect signals
        self.gallery_preview.image_selected_signal.connect(self.image_selected)

    def button_pressed(self):
        """Button pressed event
        Load directory
        """
        dialog = QFileDialog(self)
        directory_name = dialog.getExistingDirectory(self,
            "Open Folder", os.path.expanduser("~"))

        dialog.hide()

        self.gallery_preview.update_directory(directory_name)

    def image_selected(self, list_of_names: List[str]):
        """Image selection event."""
        print(list_of_names)