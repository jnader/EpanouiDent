"""
Class containing the widgets used for image manipulation:
- Image rotation
- Image crop
- Sliders for channel gains
- Background removal buttons
- Draw lines
- Add text captions
"""

import os
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QSlider,
    QCheckBox,
    QTextEdit,
    QSizePolicy,
    QColorDialog,
    QLabel,
)
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Signal, Qt


class ImageEditMenu(QWidget):
    """Custom widget for the buttons used in the image edit view."""

    enable_drawing_signal = Signal(bool, QColor)
    enable_text_edit_signal = Signal(bool)
    remove_background_signal = Signal(bool)
    channel_gain_signal = Signal(list) # R, G, B, Angle
    image_rotation_signal = Signal(int)

    def __init__(self):
        """Construct and setup edit menu."""
        super().__init__()
        self.grid_layout = QGridLayout()
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Can be put inside a Widget with Horizontal layout to mark border.
        self.draw_button = QPushButton("Draw")
        self.draw_button.setCheckable(True)
        self.draw_button.setIcon(QIcon.fromTheme("edit-pencil"))
        self.draw_button.clicked.connect(self.enable_drawing)
        self.grid_layout.addWidget(self.draw_button, 1, 1)

        self.text_edit_button = QPushButton("Enter text")
        self.text_edit_button.setCheckable(True)
        self.text_edit_button.setIcon(QIcon.fromTheme("text-edit"))
        self.text_edit_button.clicked.connect(self.enable_text_edit)
        self.grid_layout.addWidget(self.text_edit_button, 1, 2)

        self.remove_background_button = QPushButton("Remove background")
        self.remove_background_button.setCheckable(True)
        self.remove_background_button.setIcon(QIcon.fromTheme("background"))
        self.remove_background_button.clicked.connect(self.remove_background)
        self.grid_layout.addWidget(self.remove_background_button, 1, 3)

        # Channel gain widget.
        widget = QWidget()
        v_layout = QVBoxLayout()

        label_channel_gains = QLabel("Edit Channel Gains")
        self.grid_layout.addWidget(
            label_channel_gains, 2, 1, -1, -1, alignment=Qt.AlignmentFlag.AlignTop
        )

        widget_r = self.create_slider_widget("Red", 0, 100)
        # widget_r.setStyleSheet("border: 1px solid gray;")
        v_layout.addWidget(widget_r, alignment=Qt.AlignmentFlag.AlignTop)

        widget_g = self.create_slider_widget("Green", 0, 100)
        v_layout.addWidget(widget_g, alignment=Qt.AlignmentFlag.AlignTop)

        widget_b = self.create_slider_widget("Blue", 0, 100)
        v_layout.addWidget(widget_b, alignment=Qt.AlignmentFlag.AlignTop)
        widget.setLayout(v_layout)
        # widget.setStyleSheet("border: 1px solid gray;")
        self.grid_layout.addWidget(
            widget, 3, 1, 1, -1, alignment=Qt.AlignmentFlag.AlignTop
        )

        # Image rotation widget
        label_rotate = QLabel("Rotate image")
        self.grid_layout.addWidget(
            label_rotate, 4, 1, 1, -1, alignment=Qt.AlignmentFlag.AlignTop
        )

        widget_angle = self.create_slider_widget("Angle", -90, 90)
        self.grid_layout.addWidget(
            widget_angle, 5, 1, 1, -1, alignment=Qt.AlignmentFlag.AlignTop
        )

        self.setLayout(self.grid_layout)

    def create_slider_widget(
        self, channel_str: str, min_value: int, max_value: int
    ) -> QWidget:
        """Create a widget in which there's a label with the
        channel_str (R,G,B) and a slider with values ranging from
        (min_val, max_val) and connects the callbacks accordingly.

        Args:
            channel_str (str): Red, Green or Blue.
            min_value (int): Minimum slider value
            max_value (int): Maximum slider value

        Returns:
            QWidget: The widget in the description.
        """
        widget = QWidget()
        h_layout = QHBoxLayout()

        setattr(self, f"{channel_str.lower()}_checkbox", QCheckBox())
        getattr(self, f"{channel_str.lower()}_checkbox").setObjectName(
            f"{channel_str.lower()}_checkbox"
        )
        getattr(self, f"{channel_str.lower()}_checkbox").stateChanged.connect(
            self.checkbox_clicked
        )

        label_channel = QLabel(channel_str)

        setattr(
            self,
            f"{channel_str.lower()}_slider",
            QSlider(orientation=Qt.Orientation.Horizontal),
        )
        getattr(self, f"{channel_str.lower()}_slider").setMinimum(min_value)
        getattr(self, f"{channel_str.lower()}_slider").setMaximum(max_value)
        getattr(self, f"{channel_str.lower()}_slider").setValue(max_value)
        getattr(self, f"{channel_str.lower()}_slider").setStatusTip(channel_str)
        getattr(self, f"{channel_str.lower()}_slider").setDisabled(True)
        getattr(self, f"{channel_str.lower()}_slider").setObjectName(
            f"{channel_str.lower()}_slider"
        )
        getattr(self, f"{channel_str.lower()}_slider").valueChanged.connect(
            self.slider_value_changed
        )

        h_layout.addWidget(getattr(self, f"{channel_str.lower()}_checkbox"), stretch=1)
        h_layout.addWidget(label_channel, stretch=1)
        h_layout.addWidget(getattr(self, f"{channel_str.lower()}_slider"), stretch=8)
        widget.setLayout(h_layout)
        return widget

    def enable_drawing(self):
        """Enable drawing signal."""
        if self.draw_button.isChecked():
            color_dialog = QColorDialog(parent=self)
            color_dialog.colorSelected.connect(self.get_pen_selected)
            color_dialog.open()

        else:
            self.enable_drawing_signal.emit(self.draw_button.isChecked(), None)

    def get_pen_selected(self, color_selected: QColor):
        """Get the selected color from dialog box"""
        self.enable_drawing_signal.emit(self.draw_button.isChecked(), color_selected)

    def enable_text_edit(self):
        """Enable text edit signal."""
        self.enable_text_edit_signal.emit(self.text_edit_button.isChecked())

    def remove_background(self):
        """Remove background signal."""
        self.remove_background_signal.emit(self.remove_background_button.isChecked())

    def slider_value_changed(self):
        """Channel gain changed event."""
        names = ["red", "green", "blue", "angle"]
        values = [getattr(self, f"{x}_slider").value() for x in names]
        self.channel_gain_signal.emit(values)

    def checkbox_clicked(self):
        """Channel gain checkbox clicked event.
        TODO: Modify checkbox to be added on the level of the section and not the slider."""
        sender: QCheckBox
        sender = self.sender()
        sender_identifier = sender.objectName().replace("_checkbox", "")

        if sender.isChecked():
            getattr(self, f"{sender_identifier}_slider").setDisabled(False)
        else:
            getattr(self, f"{sender_identifier}_slider").setDisabled(True)
