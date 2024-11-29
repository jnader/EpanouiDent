"""
Custom image container widget
"""

from PySide6.QtCore import Qt, QPoint, QPointF, QRect, QKeyCombination, Signal
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
import cv2
import numpy as np
import os
from threading import Thread
from PySide6.QtGui import (
    QMouseEvent,
    QPixmap,
    QKeyEvent,
    QDropEvent,
    QDragEnterEvent,
    QImageReader,
    QImage,
    QPainter,
    QColor,
    QIcon,
    QFont,
    QPen,
)
from typing import List
from collections import deque
from backend.background_removal import remove_background


class ImageContainer(QWidget):
    """ImageContainer class in which all image processing
    will be supported:
    - Image rotation
    - Image crop
    - Channel gain manipulation
    - Drawing and Text edit
    - Background removal
    """

    background_image_generated = Signal(bool)

    def __init__(self, image_path: str = None):
        """Constructor

        Args:
            image_path (str, optional): image_path. Defaults to None.
        """
        super().__init__()
        layout = QVBoxLayout()
        self.image_container = QLabel()
        self.image_container.setStyleSheet("border: 1px solid gray")
        self.image_container.mousePressEvent = self.mouseReleaseEvent
        self.image_container.mousePressEvent = self.mousePressEvent
        self.image_container.mouseMoveEvent = self.mouseMoveEvent
        self.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_container.setFocusPolicy(Qt.StrongFocus)
        layout.addWidget(self.image_container)

        self.image_container_current_size = self.image_container.size()
        self.image_path = image_path
        self.original_image = None
        self.latest_updated_image = None
        self.image_without_background = None
        self.out_image = QImage()
        self.last_point = None

        # Undo/Redo stack handling
        self.pixmap_undo_stack = deque([])
        self.pixmap_redo_stack = deque([])

        # Drawing flags and variables
        self.enable_drawing_line = False
        self.enable_drawing_horizontal_line = False
        self.enable_drawing_vertical_line = False
        self.enable_drawing_circle = False
        self.enable_drawing_rectangle = False
        self.pen_color = QColor("black")
        self.brush_size = 6
        self.first_point = None
        self.last_point = None
        self.rect = None
        self.current_text = ""
        self.enable_text = False

        if os.path.exists(image_path):
            t = Thread(target=self.remove_background_target, args=[image_path])
            t.start()

            self.original_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
            self.latest_updated_image = self.original_image
            self.out_image = QImage(
                self.latest_updated_image,
                self.latest_updated_image.shape[1],
                self.latest_updated_image.shape[0],
                self.latest_updated_image.shape[1] * 3,
                QImage.Format_BGR888,
            )
            self.current_pixmap = QPixmap(self.out_image)
            self.update_undo_stack()
        else:
            self.current_pixmap = QPixmap()

        self.update_image()
        self.setAcceptDrops(True)
        self.setLayout(layout)

    def remove_background_target(self, img_path: str):
        """Function to be called in a background thread.

        Args:
            img_path (str): Image file name
        """
        self.image_without_background, self.original_image = remove_background(
            image_path=img_path
        )

        self.background_image_generated.emit(True)

    def update_image(self, pixmap: QPixmap = None):
        """Update the image display based on the widget's size.
        TODO: There's an issue, it redraws for all iterations.
        This function should only update the view with a given pixmap not just
        self.current_pixmap.

        Args:
            pixmap (QPixmap, optional): Pixmap to assign to the image container.
                                        If None, assign self.current_pixmap
        """
        # if (
        #     self.out_image.size().width() > self.width()
        #     or self.out_image.size().height() > self.height()
        # ):
        #     self.image_container.setPixmap(
        #         self.current_pixmap.scaled(
        #             self.width(),
        #             self.height(),
        #             Qt.KeepAspectRatio,
        #             Qt.SmoothTransformation,
        #         )
        #     )

        # else:
        #     self.image_container.setPixmap(self.current_pixmap)
        if not pixmap:
            pixmap = self.current_pixmap

        self.image_container.setPixmap(
            pixmap.scaled(
                self.image_container_current_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    # def resizeEvent(self, event):
    #     """Resize event.
    #     Update the image to fit the new size of the widget.
    #     """
    #     self.update_image()
    #     super().resizeEvent(event)

    def wheelEvent(self, event):
        """Mouse wheel event"""
        self.image_container.setPixmap(
            self.current_pixmap.scaled(
                self.width() + event.angleDelta().y(),
                self.height() + event.angleDelta().y(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )
        self.image_container_current_size = self.image_container.size()

    # def dragEnterEvent(self, event: QDragEnterEvent) -> None:
    #     """DragEnter event

    #     Args:
    #         event (QDragEnterEvent): QDragEnterEvent
    #     """
    #     # Define the accepted drop action
    #     if event.mimeData().hasUrls() and len(event.mimeData().urls()) == 1:
    #         event.acceptProposedAction()

    # def dropEvent(self, event: QDropEvent) -> None:
    #     """dropEvent

    #     Args:
    #         event (QDropEvent): QDropEvent
    #     """
    #     # Get the file path of the dropped image
    #     self.image_path = event.mimeData().urls()[0].toLocalFile()

    #     # Check if it's an image file
    #     image_reader = QImageReader(self.image_path)
    #     if image_reader.format().isEmpty():
    #         return

    #     # Update and display pixmap
    #     self.image_without_background, self.original_image = remove_background(
    #         image_path=self.image_path
    #     )
    #     self.reset_original_image()
    #     self.save_no_background_image()

    def apply_channel_gains(self, gains: List[int]):
        """Apply a list of gains provided in %.

        Args:
            gains (List[int]): List of gains to apply (R, G, B) order.
        """
        gains = np.array([x / 100.0 for x in gains])
        new_image = cv2.xphoto.applyChannelGains(
            self.latest_updated_image, gains[2], gains[1], gains[0]
        )
        # TODO: needs normalization...
        # new_image = self.latest_updated_image * gains
        self.out_image = QImage(
            new_image,
            new_image.shape[1],
            new_image.shape[0],
            new_image.shape[1] * 3,
            QImage.Format_BGR888,
        )
        self.update_undo_stack()
        self.current_pixmap = QPixmap(self.out_image)
        self.update_image()

    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.drawPixmap(self.current_pixmap.rect(), self.current_pixmap)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Called whenever a key is pressed"""
        data = event.keyCombination()
        if data.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
            if data.key() == Qt.Key.Key_Z:
                self.undo_image_manipulation()
            # elif data.key() == Qt.Key.Key_Y:
            # self.redo_image_manipulation()
            return

        tmp_pixmap = self.current_pixmap.copy()
        with QPainter(tmp_pixmap) as painter:
            painter.setPen(QPen(self.pen_color, self.brush_size))
            if self.first_point:
                if self.enable_text:
                    if event.key() == Qt.Key.Key_Backspace:
                        self.current_text = self.current_text[:-1]
                    elif event.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return]:
                        self.current_text += "\n"
                    elif event.text():
                        self.current_text += chr(event.key())

                    serifFont = QFont("Times", self.brush_size * 3, QFont.Bold)
                    painter.setFont(serifFont)
                    painter.drawText(self.rect, self.current_text)
                    painter.drawRect(self.rect)
                    self.update_image(tmp_pixmap)

    def undo_image_manipulation(self):
        """Undo latest modification."""
        if len(self.pixmap_undo_stack) > 0:
            self.current_pixmap = self.pixmap_undo_stack.pop()
            self.pixmap_redo_stack.append(self.current_pixmap.copy())
            self.update_image()

    # def redo_image_manipulation(self):
    #     """Redo latest modification."""
    #     if len(self.pixmap_redo_stack) > 0:
    #         self.current_pixmap = self.pixmap_redo_stack.pop()
    #         print(f"Undo: {len(self.pixmap_undo_stack)}, Redo: {len(self.pixmap_redo_stack)}")
    #         self.update_undo_stack()
    #         self.update_image()

    def is_mouse_inside_pixmap(self, ev: QMouseEvent):
        """Checks if mouse is inside the actual pixmap or not.

        Args:
            ev (QMouseEvent): Event data related to the mouse's position.
        """
        point = ev.position()
        left = (
            self.image_container.width() - self.image_container.pixmap().width()
        ) // 2
        top = (
            self.image_container.height() - self.image_container.pixmap().height()
        ) // 2
        if point.x() > left and point.x() < self.image_container.width() - left:
            if point.y() > top and point.y() < self.image_container.height() - top:
                return True
            return False
        return False

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        """Called when the user moves the mouse while it's pressed.
        TODO: Convert from image_container's coordinates to pixmap's.

        Args:
            ev (QMouseEvent): Event data related to the mouse's position.
        """
        if self.is_mouse_inside_pixmap(ev):
            pixmap_offset_x = (
                self.image_container.width() - self.image_container.pixmap().width()
            ) // 2
            pixmap_offset_y = (
                self.image_container.height() - self.image_container.pixmap().height()
            ) // 2
            self.last_point = QPointF(
                ev.position().x() - pixmap_offset_x, ev.position().y() - pixmap_offset_y
            )

        tmp_pixmap = self.current_pixmap.copy()
        scale_x = tmp_pixmap.width() / self.image_container.pixmap().width()
        scale_y = tmp_pixmap.height() / self.image_container.pixmap().height()

        self.last_point.setX(self.last_point.x() * scale_x)
        self.last_point.setY(self.last_point.y() * scale_y)

        with QPainter(tmp_pixmap) as painter:
            painter.setPen(QPen(self.pen_color, self.brush_size))
            if self.first_point:
                if self.enable_drawing_rectangle or self.enable_text:
                    self.rect = QRect(
                        min(self.first_point.x(), self.last_point.x()),
                        min(self.first_point.y(), self.last_point.y()),
                        abs(self.first_point.x() - self.last_point.x()),
                        abs(self.first_point.y() - self.last_point.y()),
                    )
                    painter.drawRect(self.rect)
                    self.update_image(tmp_pixmap)

                elif self.enable_drawing_circle:
                    radius = (self.last_point - self.first_point).manhattanLength() // 2
                    center = self.first_point + (self.last_point - self.first_point) / 2
                    painter.drawEllipse(center, radius, radius)
                    self.update_image(tmp_pixmap)

                elif self.enable_drawing_horizontal_line:
                    painter.drawLine(
                        self.first_point.x(),
                        self.first_point.y(),
                        self.last_point.x(),
                        self.first_point.y(),
                    )
                    self.update_image(tmp_pixmap)

                elif self.enable_drawing_vertical_line:
                    painter.drawLine(
                        self.first_point.x(),
                        self.first_point.y(),
                        self.first_point.x(),
                        self.last_point.y(),
                    )
                    self.update_image(tmp_pixmap)

                elif self.enable_drawing_line:
                    painter.drawLine(
                        self.first_point.x(),
                        self.first_point.y(),
                        self.last_point.x(),
                        self.last_point.y(),
                    )
                    self.update_image(tmp_pixmap)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        """Called when the user initiates a mouse press/move event.
        TODO: Convert from image_container's coordinates to pixmap's.

        Args:
            ev (QMouseEvent): Event data related to the mouse's position.
        """
        if self.is_mouse_inside_pixmap(ev):
            pixmap_offset_x = (
                self.image_container.width() - self.image_container.pixmap().width()
            ) // 2
            pixmap_offset_y = (
                self.image_container.height() - self.image_container.pixmap().height()
            ) // 2
            self.first_point = QPointF(
                ev.position().x() - pixmap_offset_x, ev.position().y() - pixmap_offset_y
            )
            scale_x = (
                self.current_pixmap.width() / self.image_container.pixmap().width()
            )
            scale_y = (
                self.current_pixmap.height() / self.image_container.pixmap().height()
            )
            self.first_point.setX(self.first_point.x() * scale_x)
            self.first_point.setY(self.first_point.y() * scale_y)
        else:
            self.first_point = None

        # If text edit enabled, write the final version of the text.
        if self.enable_text:
            with QPainter(self.current_pixmap) as painter:
                serifFont = QFont("Times", self.brush_size * 3, QFont.Bold)
                painter.setFont(serifFont)
                painter.setPen(QPen(self.pen_color, self.brush_size))
                if (
                    self.first_point
                    and self.current_text is not None
                    and len(self.current_text) > 0
                ):
                    painter.drawText(self.rect, self.current_text)
                    painter.drawRect(self.rect)
                    self.update_image()

        self.current_text = ""

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        """Called when the user releases the mouse and thus applies
        the last draw shape.
        TODO: Convert from image_container's coordinates to pixmap's.

        Args:
            ev (QMouseEvent): Event data related to the mouse's position.
        """
        with QPainter(self.current_pixmap) as painter:
            painter.setPen(QPen(self.pen_color, self.brush_size))
            if self.first_point:
                if self.enable_drawing_rectangle or (
                    self.enable_text and self.current_text != ""
                ):
                    self.rect = QRect(
                        min(self.first_point.x(), self.last_point.x()),
                        min(self.first_point.y(), self.last_point.y()),
                        abs(self.first_point.x() - self.last_point.x()),
                        abs(self.first_point.y() - self.last_point.y()),
                    )
                    self.update_undo_stack()
                    painter.drawRect(self.rect)
                    self.update_image()

                elif self.enable_drawing_circle:
                    radius = (self.last_point - self.first_point).manhattanLength() // 2
                    center = self.first_point + (self.last_point - self.first_point) / 2
                    self.update_undo_stack()
                    painter.drawEllipse(center, radius, radius)
                    self.update_image()

                elif self.enable_drawing_horizontal_line:
                    self.update_undo_stack()
                    painter.drawLine(
                        self.first_point.x(),
                        self.first_point.y(),
                        self.last_point.x(),
                        self.first_point.y(),
                    )
                    self.update_image()

                elif self.enable_drawing_vertical_line:
                    self.update_undo_stack()
                    painter.drawLine(
                        self.first_point.x(),
                        self.first_point.y(),
                        self.first_point.x(),
                        self.last_point.y(),
                    )
                    self.update_image()

                elif self.enable_drawing_line:
                    if self.first_point and self.last_point:
                        self.update_undo_stack()
                        painter.drawLine(
                            self.first_point.x(),
                            self.first_point.y(),
                            self.last_point.x(),
                            self.last_point.y(),
                        )
                        self.update_image()

        out_image = self.current_pixmap.toImage()
        out_image = out_image.convertToFormat(QImage.Format_BGR888)
        ptr = out_image.bits()

        self.latest_updated_image = np.array(ptr).reshape(
            out_image.height(), out_image.width(), 3
        )

    def update_undo_stack(self):
        if len(self.pixmap_redo_stack) > 0:
            self.pixmap_redo_stack.clear()
        self.pixmap_undo_stack.append(self.current_pixmap.copy())

    def remove_background(self):
        """
        Remove background of the image. In fact this will replace the original
        image with the one without background.
        TODO:
        - Handle it more intelligently, by taking the current pixmap and
        removing the background.
            - This can be done by creating another function remove_background_pixmap()
            that will take as input `current_pixmap`.
        """
        if self.image_without_background is None:
            # TODO: Handle asynchronously
            print("Not yet generated")
            return
        out_image = QImage(
            self.image_without_background,
            self.image_without_background.shape[1],
            self.image_without_background.shape[0],
            self.image_without_background.shape[1] * 4,
            QImage.Format_RGBA8888,
        )
        self.update_undo_stack()
        self.current_pixmap = QPixmap(out_image)
        self.update_image()

    def reset_original_image(self):
        """
        Resets original image with background.
        """
        out_image = QImage(
            self.original_image,
            self.original_image.shape[1],
            self.original_image.shape[0],
            self.original_image.shape[1] * 3,
            QImage.Format_BGR888,
        )
        self.update_undo_stack()
        self.current_pixmap = QPixmap(out_image)
        self.update_image()

    def horizontal_flip(self):
        """Flip image horizontally.
        # TODO: Modify latest_updated_image?
        """
        self.latest_updated_image = cv2.flip(self.latest_updated_image, 1)
        out_image = QImage(
            self.latest_updated_image,
            self.latest_updated_image.shape[1],
            self.latest_updated_image.shape[0],
            self.latest_updated_image.shape[1] * 3,
            QImage.Format_BGR888,
        )
        self.update_undo_stack()
        self.current_pixmap = QPixmap(out_image)
        self.update_image()

    def vertical_flip(self):
        """Flip image vertically.
        # TODO: Modify latest_updated_image?
        """
        self.latest_updated_image = cv2.flip(self.latest_updated_image, 0)
        out_image = QImage(
            self.latest_updated_image,
            self.latest_updated_image.shape[1],
            self.latest_updated_image.shape[0],
            self.latest_updated_image.shape[1] * 3,
            QImage.Format_BGR888,
        )
        self.update_undo_stack()
        self.current_pixmap = QPixmap(out_image)
        self.update_image()

    def rotate_clockwise(self):
        """Rotate image clockwise"""
        self.latest_updated_image = cv2.rotate(
            self.latest_updated_image, cv2.ROTATE_90_CLOCKWISE
        )
        out_image = QImage(
            self.latest_updated_image,
            self.latest_updated_image.shape[1],
            self.latest_updated_image.shape[0],
            self.latest_updated_image.shape[1] * 3,
            QImage.Format_BGR888,
        )
        self.update_undo_stack()
        self.current_pixmap = QPixmap(out_image)
        self.update_image()

    def rotate_counter_clockwise(self):
        """Rotate image counter clockwise"""
        self.latest_updated_image = cv2.rotate(
            self.latest_updated_image, cv2.ROTATE_90_COUNTERCLOCKWISE
        )
        out_image = QImage(
            self.latest_updated_image,
            self.latest_updated_image.shape[1],
            self.latest_updated_image.shape[0],
            self.latest_updated_image.shape[1] * 3,
            QImage.Format_BGR888,
        )
        self.update_undo_stack()
        self.current_pixmap = QPixmap(out_image)
        self.update_image()
