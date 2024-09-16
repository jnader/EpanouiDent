"""
Image Preview widget to be used in image gallery.
An image preview widget can be selected (checkbox),
mouseHover events will be defined for this widget.
"""

import cv2
import numpy as np
from PySide6.QtCore import *
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox
from PySide6.QtGui import QPixmap, QImage


class ImagePreview(QWidget):
    """ImagePreview class.
    It contains an image which can be selected to
    perform image processing.
    """

    def __init__(self, q_image: QImage):
        """Constructor of ImagePreview.

        Args:
            q_image (QImage): QImage object.
        """
        super().__init__()
        self.q_image = q_image

        # Step 1: Set up the layout and image container
        self.layout = QVBoxLayout()
        self.image_container = QLabel()
        self.image_container.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.layout.addWidget(self.image_container)

        self.setLayout(self.layout)

        # Display the image initially
        self.update_image()

    def resizeEvent(self, event):
        """Resize event.
        Update the image to fit the new size of the widget.
        """
        self.update_image()
        super().resizeEvent(event)

    def update_image(self):
        """Update the image display based on the widget's size."""
        pixmap = QPixmap(self.q_image)
        self.image_container.setPixmap(
            pixmap.scaled(
                self.width() - 40,
                self.height() - 40,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def enterEvent(self, event):
        """Mouse Enter event"""
        self.setStyleSheet("background-color: rgb(40, 127, 200)")

    def leaveEvent(self, event):
        """Mouse Leave event"""
        self.setStyleSheet("background-color: transparent()")

    def mouseMoveEvent(self, event):
        """Mouse Move event
        TODO: Implement draging inside the grid? (very optional)"""
        pass

    def mousePressEvent(self, event):
        """Mouse Press event
        Should check/uncheck the checkbox and update parent's selected files
        """
        pass
        # emit signals
