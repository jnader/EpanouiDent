"""
Custom widget for before/after effect
"""

import cv2
import numpy as np
import os
from PySide6.QtCore import *
from PySide6.QtWidgets import QWidget, QLabel, QSlider, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPixmap, QDropEvent, QDragEnterEvent, QImageReader, QImage
from backend.background_removal import remove_background


class BeforeAfter(QWidget):
    """This class will handle the effect of having 2 images
    to be compared (before/after). It'll contain a slider to
    set the proportion of images before and after.

    It inherits from QWidget class.
    """

    image_before: np.ndarray
    image_after: np.ndarray
    original_width: int
    original_height: int
    selected_width: int
    pixmap: QPixmap
    pixmap_container: QLabel
    image_before_path: str
    image_after_path: str
    slider: QSlider

    def __init__(self, image_path_before: str, image_path_after: str):
        """Constructor for BeforeAfter widget.

        Args:
            image_path_before (str): Path to image before.
            image_path_after (str): Path to image after.
        """
        super().__init__()
        if os.path.exists(image_path_after) and os.path.exists(image_path_before):
            self.image_before = cv2.imread(image_path_before, cv2.IMREAD_COLOR)
            self.image_after = cv2.imread(image_path_after, cv2.IMREAD_COLOR)

            # Make sure to have (C, H, W) instead of (H, W)
            if len(self.image_before.shape) != 3:
                self.image_before = np.expand_dims(self.image_before, axis=0)
            if len(self.image_after.shape) != 3:
                self.image_after = np.expand_dims(self.image_after, axis=0)

            # Save the Width of the original image
            self.original_height, self.original_width = self.image_before.shape[0:2]
            self.selected_width = self.original_width // 2

            # Setup widget
            self.setup(image_path_before, image_path_after)

        else:
            print("One or both images do not exist!")
            exit(0)

    def setup(self, image_path_before: str, image_path_after: str):
        """Setup the container having this effect

        Args:
            image_path_before (str): image path before.
            image_path_after (str): image path after.
        """
        self.pixmap_container = QLabel()
        self.pixmap = QPixmap()
        self.pixmap_container.setPixmap(self.pixmap)

        slider_widget = QWidget()
        layout_horizontal = QHBoxLayout()
        label_left = QLabel(text="Before")
        label_right = QLabel(text="After")
        self.slider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.valueChanged)
        layout_horizontal.addWidget(label_left)
        layout_horizontal.addWidget(self.slider)
        layout_horizontal.addWidget(label_right)
        slider_widget.setLayout(layout_horizontal)

        layout = QVBoxLayout()
        layout.addWidget(self.pixmap_container)
        layout.addWidget(slider_widget)
        self.setLayout(layout)

        self.draw_final_image()

    def valueChanged(self):
        """Callback when slider value changes"""
        self.selected_width = int(
            self.slider.value() * self.original_width / float(self.slider.maximum())
        )
        self.draw_final_image()

    def draw_final_image(self):
        """Creates the final image with portions of old and new images."""

        final_image = np.concatenate(
            (
                self.image_before[:, : self.selected_width, :],
                self.image_after[:, self.selected_width :, :],
            ),
            axis=1,
        )

        final_image = cv2.line(
            final_image,
            (self.selected_width, 0),
            (self.selected_width, self.original_height),
            (255, 255, 255),
            3,
        )

        w, h = self.pixmap_container.size().width(), self.pixmap_container.size().height()
        final_image = cv2.resize(final_image, (w,h))

        final_qimage = QImage(
            final_image,
            final_image.shape[1],
            final_image.shape[0],
            QImage.Format_BGR888,
        )

        self.pixmap = QPixmap(final_qimage)
        self.pixmap_container.setPixmap(self.pixmap)

        return final_image
