"""
Custom widget for before/after effect
"""

import cv2
import numpy as np
import os
from typing import List

from PySide6.QtCore import *
from PySide6.QtWidgets import QWidget, QLabel, QSlider, QVBoxLayout, QGridLayout
from PySide6.QtGui import QPixmap, QDropEvent, QDragEnterEvent, QImageReader, QImage

from ui.widgets.image_preview import ImagePreview


class CollagePreview(QWidget):
    """This class will handle the collage of 2/3/4 pictures in
    a grid layout.

    It inherits from QWidget class.
    """

    image_path_list: List[str]
    original_width: int
    original_height: int
    selected_width: int
    pixmap: QPixmap
    pixmap_container: QLabel
    slider: QSlider

    def __init__(self, image_path_list: List[str]):
        """Constructor for CollagePreview widget.

        Args:
            image_path_before (str): Path to image before.
            image_path_after (str): Path to image after.
        """
        super().__init__()
        self.images = []
        self.image_names = []
        self.image_containers = []
        self.selected_images = []
        self.grid_layout = QGridLayout()

        self.image_path_list = image_path_list

        for file in self.image_path_list:
            try:
                self.images.append(cv2.imread(file, cv2.IMREAD_COLOR))
                self.image_names.append(file)
            except Exception as e:
                print(e)
                pass

            self.update_collage()

    def update_collage(self):
        """Updatess image collage preview.
        TODO: '2' can be added to an internal variable
        if the user changes it, the collage changes from
        nX2 to mX3 for example, etc...
        """
        cols = 2

        for id, img in enumerate(self.images):
            i = id // cols
            j = id % cols

            q_image = QImage(
                img,
                img.shape[1],
                img.shape[0],
                img.shape[1] * 3,
                QImage.Format_BGR888,
            )

            image_container = ImagePreview(
                id=id,
                q_image=q_image,
                name=self.image_names[id],
                image_preview_flag=False,
            )
            self.image_containers.append(image_container)

            self.grid_layout.addWidget(self.image_containers[-1], i, j)

        self.setLayout(self.grid_layout)

    def setup(self):
        """Setup the container having this effect"""
        self.pixmap_container = QLabel()
        self.pixmap = QPixmap()
        self.pixmap_container.setPixmap(self.pixmap)

        slider_widget = QWidget()
        layout_horizontal = QGridLayout()
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

        w, h = (
            self.pixmap_container.size().width(),
            self.pixmap_container.size().height(),
        )
        final_image = cv2.resize(final_image, (w, h))

        final_qimage = QImage(
            final_image,
            final_image.shape[1],
            final_image.shape[0],
            QImage.Format_BGR888,
        )

        self.pixmap = QPixmap(final_qimage)
        self.pixmap_container.setPixmap(self.pixmap)

        return final_image
