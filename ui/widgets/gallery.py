""" Gallery class to preview multiple photos.
The idea is to be used on a directory of images.
"""

import cv2
from multiprocessing.pool import ThreadPool
import numpy as np
import os
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout
from PySide6.QtGui import QImage
from typing import List
from ui.widgets.image_preview import ImagePreview


class Gallery(QWidget):
    """Main class of the image gallery."""

    directory: str
    layout: QGridLayout
    images: List[np.ndarray]
    image_names: List[str]
    image_containers: List[ImagePreview]
    selected_images: List[str]
    standalone: bool  # Used to check if widget is inside another page or not.

    image_selected_signal = Signal(list)
    double_click_signal = Signal(str)
    show_collage_button_signal = Signal(bool)

    def __init__(self, directory: str):
        """Constructor of the class.

        Args:
            directory (str): Path to image directory.
        """
        super().__init__()

        self.images = []
        self.image_names = []
        self.image_containers = []
        self.selected_images = []
        self.layout = QGridLayout()

        # Since it's showing a full directory
        self.standalone = False

        self.directory = directory
        if not os.path.exists(self.directory):
            print("Directory does not exist.")

        if os.path.exists(self.directory):
            self.potential_entries = os.listdir(self.directory)
            with ThreadPool(len(self.potential_entries)) as p:
                results = p.map(func=self.load_files, iterable=self.potential_entries)

            self.update_gallery()

    def load_files(self, entry_name: str):
        """Function to read entry (could be image or not) and update
        objects internal variables.

        Args:
            entry_id (str): String containing the path of the potential entry
        """
        try:
            img = cv2.imread(os.path.join(self.directory, entry_name), cv2.IMREAD_COLOR)
            if img is not None:
                self.images.append(img)
                self.image_names.append(os.path.join(self.directory, entry_name))
        except Exception as e:
            print(e)
            pass

    def update_gallery(self):
        """Updatess image gallery preview."""
        cols = 4

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
            )

            image_container.checkbox_toggled.connect(self.image_selected)
            image_container.double_click_signal.connect(self.image_double_clicked)
            self.image_containers.append(image_container)

            # self.layout.setContentsMargins(20, 20, 20, 20)
            self.layout.addWidget(self.image_containers[-1], i, j)

        self.setLayout(self.layout)

    def update_directory(self, directory: str):
        """Updates gallery preview. Used when an object is created
        with unknown or empty directory.
        Handles clearing previous images, image containers and selected images.

        Args:
            directory (str): Directory to be previewed.
        """
        self.image_names = []
        self.images = []
        for widget in self.image_containers:
            self.layout.removeWidget(widget)
            widget.deleteLater()
        self.image_containers = []
        self.update()
        self.selected_images = []

        self.directory = directory
        if not os.path.exists(self.directory):
            print("Directory does not exist.")

        if os.path.exists(self.directory):
            self.potential_entries = os.listdir(self.directory)
            if len(self.potential_entries) > 0:
                with ThreadPool(len(self.potential_entries)) as p:
                    results = p.map(
                        func=self.load_files,
                        iterable=self.potential_entries,
                    )

            self.update_gallery()

    def image_selected(self, selected, id):
        """Image selected event"""
        if selected:
            # Add selected ID to list
            self.selected_images.append(self.image_names[id])
        else:
            # Remove selected ID from list
            self.selected_images.remove(self.image_names[id])

        # Show collage button in Gallery Page.
        if not self.standalone:
            self.show_collage_button_signal.emit(len(self.selected_images) >= 2)

        self.image_selected_signal.emit(self.selected_images)

    def image_double_clicked(self, id):
        """Event raised when double click detected on image."""
        self.double_click_signal.emit(self.image_names[id])

    def sync_diff(self):
        """Sync directory for new files and update."""
        for file in os.listdir(self.directory):
            if os.path.join(self.directory, file) not in self.image_names:
                try:
                    img = cv2.imread(
                        os.path.join(self.directory, file), cv2.IMREAD_COLOR
                    )
                    if img is not None:
                        self.images.append(img)
                        self.image_names.append(os.path.join(self.directory, file))
                except Exception as e:
                    print(e)
                    pass

        self.update_gallery()
