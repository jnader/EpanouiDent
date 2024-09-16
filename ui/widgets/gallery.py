""" Gallery class to preview multiple photos.
The idea is to be used on a directory of images.
"""

import cv2
import numpy as np
import os
from PySide6.QtWidgets import QWidget, QGridLayout, QScrollArea
from PySide6.QtGui import QImage, QPixmap
from typing import List
from ui.widgets.image_preview import ImagePreview


class Gallery(QWidget):
    """Main class of the image gallery."""

    directory: str
    layout: QGridLayout
    images: List[np.ndarray]
    image_containers: List[ImagePreview]
    selected_images: List[ImagePreview]

    def __init__(self, directory: str):
        """Constructor of the class.

        Args:
            directory (str): Path to image directory.
        """
        super().__init__()
        self.directory = directory
        if not os.path.exists(self.directory):
            print("Directory does not exist.")

        self.images = []
        self.image_containers = []
        self.selected_images = []
        self.layout = QGridLayout()
        for file in os.listdir(self.directory):
            try:
                self.images.append(
                    cv2.imread(os.path.join(self.directory, file), cv2.IMREAD_COLOR)
                )
            except Exception as e:
                print(e)
                pass

        print(f"{len(self.images)} found")
        self.update()

    def update(self):
        """Updatess image gallery preview."""
        rows = len(self.images) // 4
        cols = 4 + len(self.images) % 4
        print(f"Grid: {rows} x {cols}")

        for id, img in enumerate(self.images):
            i = id // cols
            j = id % cols

            q_image = QImage(
                img,
                img.shape[1],
                img.shape[0],
                QImage.Format_BGR888,
            )

            image_container = ImagePreview(id=id, q_image=q_image)
            image_container.checkbox_toggled.connect(self.image_selected)
            self.image_containers.append(image_container)

            self.layout.addWidget(self.image_containers[-1], i, j)

        self.setLayout(self.layout)

    def image_selected(self, selected, id):
        """Image selected event
        """
        if selected:
            # Add selected ID to list
            self.selected_images.append(id)
        else:
            # Remove selected ID from list
            self.selected_images.remove(id)

        print(self.selected_images)