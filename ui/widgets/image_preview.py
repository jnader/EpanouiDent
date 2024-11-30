"""
Image Preview widget to be used in image gallery.
An image preview widget can be selected (checkbox),
mouseHover events will be defined for this widget.
"""

import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QTextEdit
from PySide6.QtGui import QPixmap, QImage


class ImagePreview(QWidget):
    """ImagePreview class.
    It contains an image which can be selected to
    perform image processing.
    """

    checkbox_toggled = Signal(bool, int)
    double_click_signal = Signal(int)

    def __init__(self, id: int, q_image: QImage, name: str, image_preview_flag: bool = True):
        """Constructor of ImagePreview.

        Args:
            id (int): ID of the widget.
            q_image (QImage): QImage object.
            name (str): Name of the image, usually being its absolute path.
            image_preview_flag (bool, optional): Set some parameters for image previewing.
                                                 Defaults to True. Otherwise, to be used with collage.
        """
        super().__init__()
        self.q_image = q_image
        self.id = id
        self.name = name
        self.caption = None
        self.old_timestamp = 0

        self.layout = QVBoxLayout()
        self.image_container = QLabel()
        self.image_container.setToolTip(self.name)
        self.image_container.setAlignment(Qt.AlignCenter)
        if image_preview_flag:
            self.checkbox = QCheckBox()
            self.image_container.setStyleSheet("border: 1px solid gray;")
            self.layout.setContentsMargins(20, 20, 20, 20)
            # self.text_edit = QTextEdit("")
            self.layout.addWidget(self.checkbox)
        else:
            self.enterEvent = self.mouseMoveEvent
            self.leaveEvent = self.mouseMoveEvent

        self.layout.addWidget(self.image_container)
        # self.layout.addWidget(self.text)

        self.setLayout(self.layout)

        # Display the image initially
        self.update_image()

    def update_image(self):
        """Update the image display based on the widget's size."""
        pixmap = QPixmap(self.q_image)
        self.image_container.setPixmap(
            pixmap.scaled(
                320,
                240,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def enterEvent(self, event):
        """Mouse Enter event"""
        self.image_container.setStyleSheet(
            "background-color: rgba(40, 127, 200, 100); border: 1px solid gray;"
        )

    def leaveEvent(self, event):
        """Mouse Leave event"""
        self.image_container.setStyleSheet(
            "background-color: transparent(); border: 1px solid gray;"
        )

    def mouseMoveEvent(self, event):
        """Mouse Move event
        TODO: Implement draging inside the grid? (very optional)"""
        pass

    def mousePressEvent(self, event):
        """Mouse Press event.
        Handles also double-clicks now.
        Should check/uncheck the checkbox and update parent's selected files
        TODO: Improve implementation.
        """
        current_timestamp = event.timestamp()

        if self.old_timestamp == 0:
            self.old_timestamp = current_timestamp

        if (
            current_timestamp - self.old_timestamp < 400
            and current_timestamp - self.old_timestamp != 0
        ):
            # Double click detected
            self.double_click_signal.emit(self.id)

        else:
            if self.checkbox.isChecked():
                self.checkbox.setChecked(False)
            else:
                self.checkbox.setChecked(True)

            self.checkbox_toggled.emit(self.checkbox.isChecked(), self.id)

        self.old_timestamp = current_timestamp
