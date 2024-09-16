"""
Image Preview widget to be used in image gallery.
An image preview widget can be selected (checkbox),
mouseHover events will be defined for this widget.
"""

import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox
from PySide6.QtGui import QPixmap, QImage


class ImagePreview(QWidget):
    """ImagePreview class.
    It contains an image which can be selected to
    perform image processing.
    """

    checkbox_toggled = Signal(bool, int)

    def __init__(self, id: int, q_image: QImage, name: str):
        """Constructor of ImagePreview.

        Args:
            id (int): ID of the widget.
            q_image (QImage): QImage object.
        """
        super().__init__()
        self.q_image = q_image
        self.id = id
        self.name = name

        # Step 1: Set up the layout and image container
        self.layout = QVBoxLayout()
        self.checkbox = QCheckBox()
        self.image_container = QLabel()
        self.image_container.setToolTip(self.name)
        self.image_container.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.layout.addWidget(self.checkbox)
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
                self.width() - 50,
                self.height() - 50,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def enterEvent(self, event):
        """Mouse Enter event"""
        self.image_container.setStyleSheet("background-color: rgba(40, 127, 200, 100)")

    def leaveEvent(self, event):
        """Mouse Leave event"""
        self.image_container.setStyleSheet("background-color: transparent()")

    def mouseMoveEvent(self, event):
        """Mouse Move event
        TODO: Implement draging inside the grid? (very optional)"""
        pass

    def mousePressEvent(self, event):
        """Mouse Press event
        Should check/uncheck the checkbox and update parent's selected files
        """
        if self.checkbox.isChecked():
            self.checkbox.setChecked(False)
        else:
            self.checkbox.setChecked(True)

        # emit signals
        self.checkbox_toggled.emit(self.checkbox.isChecked(), self.id)
