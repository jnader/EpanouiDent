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

from ui.widgets.gallery import Gallery


class GalleryPage(QWidget):
    """Gallery image page containing a scrolling area in which
    we have an image gallery and a directory selector.

    Args:
        QWidget (_type_): _description_
    """

    gallery_preview: Gallery
    button_explore: QPushButton

    def __init__(self):
        """Constructor"""
        super().__init__()

        layout = QVBoxLayout()
        self.gallery_preview = Gallery("")

        self.button_explore = QPushButton("Open Folder")
        self.button_explore.setIcon(QIcon.fromTheme("folder"))
        self.button_explore.pressed.connect(self.button_pressed)

        layout.addWidget(self.gallery_preview)
        layout.addWidget(self.button_explore)

        self.setLayout(layout)

    def button_pressed(self):
        """Button pressed event
        Load directory
        """
        directory_name = QFileDialog.getExistingDirectory(self,
            "Open Folder", os.path.expanduser("~"))

        self.gallery_preview.update_directory(directory_name)
