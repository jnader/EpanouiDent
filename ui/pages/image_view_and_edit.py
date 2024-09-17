"""
Image processing widget

TODO:
1) Check if face image is added or not. (Detect face in image)
2) Add to the right, a gimp-like window for removing background, writing with pen, etc...
"""

from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QColorDialog,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from ui.widgets.image_container import ImageContainer
from ui.widgets.image_edit_menu import ImageEditMenu

import os
import sys


class ImageViewEdit(QWidget):
    def __init__(self, base_path: str):
        """Constructor

        Args:
            base_path (str): Path to main.py
        """
        super().__init__()
        self.base_path = base_path

        self.global_layout = QVBoxLayout()

        widget = QWidget()
        h_layout = QHBoxLayout()
        self.image_container = ImageContainer()
        self.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image_edit_menu = ImageEditMenu()

        h_layout.addWidget(self.image_container, stretch=6)
        h_layout.addWidget(self.image_edit_menu, stretch=1)
        widget.setLayout(h_layout)

        # # Control buttons
        # # TODO: To be placed in ImageProcessingSettings
        # self.remove_background = QRadioButton("Remove Background")
        # self.remove_background.toggled.connect(self.toggle_remove_background)
        # h_layout.addWidget(self.remove_background)

        # self.image_processing_settings = ImageProcessingSettings(self.base_path)

        # # TODO: Not a clean way of doing it
        # self.image_processing_settings.draw_button.clicked.connect(self.enable_drawing)
        # self.image_processing_settings.text_button.clicked.connect(self.enable_text)
        # h_layout.addWidget(self.image_processing_settings)
        # h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # v_layout.addLayout(h_layout)
        # self.global_layout.addLayout(v_layout)

        self.save_button = QPushButton("Save image")
        self.save_button.setIcon(QIcon.fromTheme("media-floppy"))

        self.global_layout.addWidget(widget)
        self.global_layout.addWidget(self.save_button)

        self.setLayout(self.global_layout)

    def toggle_remove_background(self):
        """
        Triggered when remove background is clicked
        """
        if self.remove_background.isChecked():
            if self.image_container.image_path:
                self.image_container.remove_background()
        else:
            if self.image_container.image_path:
                self.image_container.reset_original_image()

    def enable_drawing(self):
        """Enable drawing on image"""
        # self.image_processing_settings.draw_button.setCheckable(self.image_processing_settings.draw_button.isChecked())
        self.image_container.enable_drawing = True

    def enable_text(self):
        """Enable text on image"""
        # self.image_processing_settings.text_button.setCheckable(self.image_processing_settings.text_button.isChecked())
        self.image_container.enable_text = True
