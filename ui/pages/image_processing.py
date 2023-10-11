"""
Image processing widget

TODO:
1) Check if face image is added or not. (Detect face in image)
2) Add to the right, a gimp-like window for removing background, writing with pen, etc...
"""

from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPixmap
from ui.widgets.image_container import ImageContainer

import os
import sys

class ImageProcessor(QWidget):
    def __init__(self):
        super().__init__()

        global_layout = QHBoxLayout()

        v_layout = QVBoxLayout()
        self.image_container = ImageContainer()
        v_layout.addWidget(self.image_container)

        h_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.load_button = QPushButton("Load")
        h_layout.addWidget(self.save_button)
        h_layout.addWidget(self.load_button)

        v_layout.addLayout(h_layout)
        global_layout.addLayout(v_layout)

        # Control buttons

        self.setLayout(global_layout)
