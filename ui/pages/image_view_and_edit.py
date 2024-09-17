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
    QGridLayout,
    QScrollArea,
    QRadioButton,
    QColorDialog,
    QFrame,
    QSizePolicy,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from ui.widgets.image_container import ImageContainer
from ui.widgets.image_edit_menu import ImageEditMenu

import os
import sys


class ImageViewEdit(QWidget):
    """ Image View and Edit page containing the original image
    with edit menu (buttons, sliders, etc...) for image manipulation.
    """

    scroll_area: QScrollArea

    def __init__(self, base_path: str = None):
        """Constructor

        Args:
            base_path (str, optional): Path to main.py
        """
        super().__init__()
        self.base_path = base_path

        layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.image_container = ImageContainer(base_path)
        self.scroll_area.setWidget(self.image_container)

        self.image_edit_menu = ImageEditMenu()
        self.image_edit_menu.channel_gain_signal.connect(self.channel_gain_changed)

        widget = QWidget()
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.scroll_area, stretch=10)
        h_layout.addWidget(self.image_edit_menu, stretch=1)
        widget.setLayout(h_layout)

        self.save_button = QPushButton("Save image")
        self.save_button.setIcon(QIcon.fromTheme("media-floppy"))

        layout.addWidget(widget)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

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

    def channel_gain_changed(self, value: int):
        """Channel gain changed event handler.

        Args:
            sender (str): Slider name in menu.
            value (int): New value of the slider
        """
        self.image_container.apply_channel_gains(value[:3])
