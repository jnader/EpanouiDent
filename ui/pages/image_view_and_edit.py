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
    QFileDialog,
)
from PySide6.QtGui import QIcon, QColor, QKeyEvent
from PySide6.QtCore import Signal, Qt
from ui.widgets.image_container import ImageContainer
from ui.widgets.image_edit_menu import ImageEditMenu

import os
import sys


class ImageViewEdit(QWidget):
    """Image View and Edit page containing the original image
    with edit menu (buttons, sliders, etc...) for image manipulation.
    """

    scroll_area: QScrollArea
    image_saved_signal = Signal(str)

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
        self.image_edit_menu.draw_rectangle_signal.connect(
            self.enable_drawing_rectangle
        )
        self.image_edit_menu.draw_circle_signal.connect(self.enable_drawing_circle)
        self.image_edit_menu.draw_horizontal_line_signal.connect(
            self.enable_drawing_horizontal_line
        )
        self.image_edit_menu.draw_vertical_line_signal.connect(
            self.enable_drawing_vertical_line
        )
        self.image_edit_menu.draw_line_signal.connect(self.enable_drawing_line)
        self.image_edit_menu.remove_background_signal.connect(self.remove_background)
        self.image_edit_menu.flip_horizontal_signal.connect(self.flip_horizontal)
        self.image_edit_menu.flip_vertical_signal.connect(self.flip_vertical)
        self.image_edit_menu.rotate_clockwise_signal.connect(self.rotate_clockwise)
        self.image_edit_menu.rotate_counter_clockwise_signal.connect(
            self.rotate_counter_clockwise
        )
        self.image_edit_menu.paint_brush_size_signal.connect(self.paint_brush_size_changed)
        self.image_edit_menu.enable_text_edit_signal.connect(self.enable_text)

        widget = QWidget()
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.scroll_area, stretch=10)
        h_layout.addWidget(self.image_edit_menu, stretch=1)
        widget.setLayout(h_layout)

        self.save_button = QPushButton("Save image")
        self.save_button.setIcon(QIcon.fromTheme("media-floppy"))
        self.save_button.clicked.connect(self.save_image)

        layout.addWidget(widget)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.setFocusPolicy(Qt.StrongFocus)

    def paint_brush_size_changed(self, new_brush_size: int):
        """Change paint brush size.

        Args:
            new_brush_size (int): Value of the new brush in pixels.
        """
        self.image_container.brush_size = new_brush_size

    def enable_drawing_line(self, state: bool, pen_color: QColor):
        """Enable drawing line on image."""
        self.image_container.enable_drawing_line = state
        self.image_container.pen_color = pen_color

    def enable_drawing_horizontal_line(self, state: bool, pen_color: QColor):
        """Enable drawing horizontal line on image."""
        self.image_container.enable_drawing_horizontal_line = state
        self.image_container.pen_color = pen_color

    def enable_drawing_vertical_line(self, state: bool, pen_color: QColor):
        """Enable drawing vertical line on image."""
        self.image_container.enable_drawing_vertical_line = state
        self.image_container.pen_color = pen_color

    def enable_drawing_rectangle(self, state: bool, pen_color: QColor):
        """Enable drawing rectangle on image."""
        self.image_container.enable_drawing_rectangle = state
        self.image_container.pen_color = pen_color

    def enable_drawing_circle(self, state: bool, pen_color: QColor):
        """Enable drawing circle on image."""
        self.image_container.enable_drawing_circle = state
        self.image_container.pen_color = pen_color

    def enable_text(self, state: bool, pen_color: QColor):
        """Enable text on image"""
        self.image_container.enable_text = state
        self.image_container.pen_color = pen_color

    def remove_background(self, state: bool):
        """Remove background signal handler.

        Args:
            state (bool): Button state. If true, remove background, restore if False
        """
        if state:
            self.image_container.remove_background()
        else:
            self.image_container.reset_original_image()

    def flip_horizontal(self, state: bool):
        """Flip image horizontally

        Args:
            state (bool): Button state. If true, flip horizontally.
        """
        self.image_container.horizontal_flip()

    def flip_vertical(self, state: bool):
        """Flip image vertically

        Args:
            state (bool): Button state. If true, flip vertically.
        """
        self.image_container.vertical_flip()

    def rotate_clockwise(self, state: bool):
        """Rotate image clockwise

        Args:
            state (bool): Button state. If true, rotate clockwise.
        """
        self.image_container.rotate_clockwise()

    def rotate_counter_clockwise(self, state: bool):
        """Rotate image counter clockwise

        Args:
            state (bool): Button state. If true, rotate counter clockwise.
        """
        self.image_container.rotate_counter_clockwise()

    def channel_gain_changed(self, value: int):
        """Channel gain changed event handler.

        Args:
            sender (str): Slider name in menu.
            value (int): New value of the slider
        """
        self.image_container.apply_channel_gains(value[:3])

    # def save_image(self):
    #     """Save processed image."""
    #     self.image_container.save_image()

    def save_image(self):
        """Callback to save processed image."""
        dialog = QFileDialog(self)
        file_name = dialog.getSaveFileName(
            self, "Save File", os.path.dirname(self.base_path)
        )

        ret = self.image_container.current_pixmap.toImage().save(
            os.path.join(os.path.dirname(self.base_path), file_name[0])
        )

        if ret:
            # Send signal to update gallery page.
            self.image_saved_signal.emit(os.path.dirname(self.base_path))

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Called whenever a key is pressed"""
        data = event.keyCombination()
        if data.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
            if data.key() == Qt.Key.Key_Z:
                self.image_container.undo_image_manipulation()
            elif data.key() == Qt.Key.Key_Y:
                self.image_container.redo_image_manipulation()
            return
