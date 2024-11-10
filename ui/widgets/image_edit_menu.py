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

    # TODO: replace QColor by QPen maybe? (Brush size, etc...)
    draw_horizontal_line_signal = Signal(bool, QColor)
    draw_vertical_line_signal = Signal(bool, QColor)
    draw_line_signal = Signal(bool, QColor)
    draw_rectangle_signal = Signal(bool, QColor)
    draw_circle_signal = Signal(bool, QColor)
    enable_text_edit_signal = Signal(bool, QColor)

    remove_background_signal = Signal(bool)
    flip_horizontal_signal = Signal(bool)
    flip_vertical_signal = Signal(bool)
    rotate_clockwise_signal = Signal(bool)
    rotate_counter_clockwise_signal = Signal(bool)
    channel_gain_signal = Signal(list)  # R, G, B
    paint_brush_size_signal = Signal(int)
    image_rotation_signal = Signal(int)

    def __init__(self):
        """Construct and setup edit menu."""
        super().__init__()
        self.grid_layout = QGridLayout()
        self.grid_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        row_increment = 1
        self.drawing_widgets_list = []
        self.widget_to_signal_mapping = {}

        # Can be put inside a Widget with Horizontal layout to mark border.
        self.draw_circle_button = QPushButton("O")
        self.draw_circle_button.setCheckable(True)
        self.draw_circle_button.setIcon(QIcon.fromTheme(""))
        self.draw_circle_button.clicked.connect(self.draw_circle)
        self.widget_to_signal_mapping[self.draw_circle_button] = self.draw_circle_signal
        self.drawing_widgets_list.append(self.draw_circle_button)
        self.grid_layout.addWidget(self.draw_circle_button, row_increment, 1)

        self.draw_rectangle_button = QPushButton("Rectangle")
        self.draw_rectangle_button.setCheckable(True)
        self.draw_rectangle_button.setIcon(QIcon.fromTheme(""))
        self.draw_rectangle_button.clicked.connect(self.draw_rectangle)
        self.widget_to_signal_mapping[
            self.draw_rectangle_button
        ] = self.draw_rectangle_signal
        self.drawing_widgets_list.append(self.draw_rectangle_button)
        self.grid_layout.addWidget(self.draw_rectangle_button, row_increment, 2)
        row_increment += 1

        self.draw_horizontal_line_button = QPushButton("--")
        self.draw_horizontal_line_button.setCheckable(True)
        self.draw_horizontal_line_button.setIcon(QIcon.fromTheme(""))
        self.draw_horizontal_line_button.clicked.connect(self.draw_horizontal_line)
        self.widget_to_signal_mapping[
            self.draw_horizontal_line_button
        ] = self.draw_horizontal_line_signal
        self.drawing_widgets_list.append(self.draw_horizontal_line_button)
        self.grid_layout.addWidget(self.draw_horizontal_line_button, row_increment, 1)

        self.draw_vertical_line_button = QPushButton("|")
        self.draw_vertical_line_button.setCheckable(True)
        self.draw_vertical_line_button.setIcon(QIcon.fromTheme(""))
        self.draw_vertical_line_button.clicked.connect(self.draw_vertical_line)
        self.widget_to_signal_mapping[
            self.draw_vertical_line_button
        ] = self.draw_vertical_line_signal
        self.drawing_widgets_list.append(self.draw_vertical_line_button)
        self.grid_layout.addWidget(self.draw_vertical_line_button, row_increment, 2)

        self.draw_line_button = QPushButton("\\")
        self.draw_line_button.setCheckable(True)
        self.draw_line_button.setIcon(QIcon.fromTheme(""))
        self.draw_line_button.clicked.connect(self.draw_line)
        self.widget_to_signal_mapping[self.draw_line_button] = self.draw_line_signal
        self.drawing_widgets_list.append(self.draw_line_button)
        self.grid_layout.addWidget(self.draw_line_button, row_increment, 3)
        row_increment += 1

        brush_icon = QLabel("Brush size")
        self.grid_layout.addWidget(brush_icon, row_increment, 1)

        self.brush_size = QSlider(orientation=Qt.Orientation.Horizontal)
        self.brush_size.setMinimum(1)
        self.brush_size.setMaximum(100)
        self.brush_size.setValue(1)
        self.brush_size.setStatusTip("Brush size")
        self.brush_size.valueChanged.connect(self.brush_size_value_changed)
        self.grid_layout.addWidget(self.brush_size, row_increment, 2, 1, -1)
        row_increment += 1

        self.text_edit_button = QPushButton("Enter text")
        self.text_edit_button.setCheckable(True)
        self.text_edit_button.setIcon(QIcon.fromTheme("text-edit"))
        self.text_edit_button.clicked.connect(self.enable_text_edit)
        self.drawing_widgets_list.append(self.text_edit_button)
        self.widget_to_signal_mapping[self.text_edit_button] = self.enable_text_edit_signal
        self.grid_layout.addWidget(self.text_edit_button, row_increment, 1)

        self.remove_background_button = QPushButton("Remove background")
        self.remove_background_button.setCheckable(True)
        self.remove_background_button.setIcon(QIcon.fromTheme("background"))
        self.remove_background_button.clicked.connect(self.remove_background)
        self.grid_layout.addWidget(self.remove_background_button, row_increment, 2)
        row_increment += 1

        self.flip_horizontal_button = QPushButton("")
        self.flip_horizontal_button.setIcon(QIcon.fromTheme("object-flip-horizontal"))
        self.flip_horizontal_button.clicked.connect(self.flip_horizontal)
        self.grid_layout.addWidget(self.flip_horizontal_button, row_increment, 1)

        self.flip_vertical_button = QPushButton("")
        self.flip_vertical_button.setIcon(QIcon.fromTheme("object-flip-vertical"))
        self.flip_vertical_button.clicked.connect(self.flip_vertical)
        self.grid_layout.addWidget(self.flip_vertical_button, row_increment, 2)

        self.rotate_clockwise_button = QPushButton("")
        self.rotate_clockwise_button.setIcon(QIcon.fromTheme("object-rotate-left"))
        self.rotate_clockwise_button.clicked.connect(self.rotate_clockwise)
        self.grid_layout.addWidget(self.rotate_clockwise_button, row_increment, 3)

        self.rotate_counter_clockwise_button = QPushButton("")
        self.rotate_counter_clockwise_button.setIcon(
            QIcon.fromTheme("object-rotate-right")
        )
        self.rotate_counter_clockwise_button.clicked.connect(
            self.rotate_counter_clockwise
        )
        self.grid_layout.addWidget(
            self.rotate_counter_clockwise_button, row_increment, 4
        )
        row_increment += 1

        # Channel gain widget.
        widget = QWidget()
        v_layout = QVBoxLayout()

        label_channel_gains = QLabel("Edit Channel Gains")
        self.grid_layout.addWidget(
            label_channel_gains,
            row_increment,
            1,
            -1,
            -1,
            alignment=Qt.AlignmentFlag.AlignTop,
        )
        row_increment += 1

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
            widget, row_increment, 1, 1, -1, alignment=Qt.AlignmentFlag.AlignTop
        )
        row_increment += 1

        # Image rotation widget
        label_rotate = QLabel("Rotate image")
        self.grid_layout.addWidget(
            label_rotate, row_increment, 1, 1, -1, alignment=Qt.AlignmentFlag.AlignTop
        )
        row_increment += 1

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

    def control_draw_buttons(self, sender: QPushButton):
        """Inverse other widgets' state when a widget is checked."""
        widget: QPushButton
        for i, widget in enumerate(self.drawing_widgets_list):
            if widget == sender:
                continue
            widget.setChecked(False)

    def draw_horizontal_line(self):
        """Enable drawing horizontal line."""
        self.control_draw_buttons(self.sender())
        if self.draw_horizontal_line_button.isChecked():
            color_dialog = QColorDialog(parent=self)
            color_dialog.colorSelected.connect(self.get_pen_selected)
            color_dialog.open()

        else:
            self.draw_horizontal_line_signal.emit(
                self.draw_horizontal_line_button.isChecked(), None
            )

    def draw_vertical_line(self):
        """Enable drawing vertucal line."""
        self.control_draw_buttons(self.sender())
        if self.draw_vertical_line_button.isChecked():
            color_dialog = QColorDialog(parent=self)
            color_dialog.colorSelected.connect(self.get_pen_selected)
            color_dialog.open()

        else:
            self.draw_vertical_line_signal.emit(
                self.draw_vertical_line_button.isChecked(), None
            )

    def draw_line(self):
        """Enable drawing random orientation line."""
        self.control_draw_buttons(self.sender())
        if self.draw_line_button.isChecked():
            color_dialog = QColorDialog(parent=self)
            color_dialog.colorSelected.connect(self.get_pen_selected)
            color_dialog.open()

        else:
            self.draw_line_signal.emit(self.draw_line_button.isChecked(), None)

    def draw_rectangle(self):
        """Enable drawing rectangle."""
        self.control_draw_buttons(self.sender())
        if self.draw_rectangle_button.isChecked():
            color_dialog = QColorDialog(parent=self)
            color_dialog.colorSelected.connect(self.get_pen_selected)
            color_dialog.open()

        else:
            self.draw_rectangle_signal.emit(
                self.draw_rectangle_button.isChecked(), None
            )

    def draw_circle(self):
        """Enable drawing circle."""
        self.control_draw_buttons(self.sender())
        if self.draw_circle_button.isChecked():
            color_dialog = QColorDialog(parent=self)
            color_dialog.colorSelected.connect(self.get_pen_selected)
            color_dialog.open()

        else:
            self.draw_circle_signal.emit(self.draw_circle_button.isChecked(), None)

    def get_pen_selected(self, color_selected: QColor):
        """Get the selected color from dialog box"""
        widget: QPushButton
        for widget in self.drawing_widgets_list:
            self.widget_to_signal_mapping[widget].emit(
                widget.isChecked(), color_selected
            )

    def enable_text_edit(self):
        """Enable text edit signal."""
        self.control_draw_buttons(self.sender())
        if self.text_edit_button.isChecked():
            color_dialog = QColorDialog(parent=self)
            color_dialog.colorSelected.connect(self.get_pen_selected)
            color_dialog.open()

        else:
            self.enable_text_edit_signal.emit(self.text_edit_button.isChecked(), None)

    def remove_background(self):
        """Remove background signal."""
        self.remove_background_signal.emit(self.remove_background_button.isChecked())

    def slider_value_changed(self):
        """Channel gain changed event."""
        names = ["red", "green", "blue"]
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

    def flip_horizontal(self):
        """Flip horizontal button clicked event"""
        self.flip_horizontal_signal.emit(True)

    def flip_vertical(self):
        """Flip vertical button clicked event"""
        self.flip_vertical_signal.emit(True)

    def rotate_clockwise(self):
        """Rotate clockwise button clicked event"""
        self.rotate_clockwise_signal.emit(True)

    def rotate_counter_clockwise(self):
        """Rotate counter clockwise button clicked event"""
        self.rotate_counter_clockwise_signal.emit(True)

    def brush_size_value_changed(
        self,
    ):
        """Paint brush size value changed event"""
        self.paint_brush_size_signal.emit(self.brush_size.value())
