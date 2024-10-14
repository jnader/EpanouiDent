"""
Custom image container widget
"""

from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
import cv2
import numpy as np
import os
from PySide6.QtGui import (
    QMouseEvent,
    QPixmap,
    QDropEvent,
    QDragEnterEvent,
    QImageReader,
    QImage,
    QPainter,
    QColor,
    QIcon,
    QPen,
)
from typing import List
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

    def __init__(self, image_path: str = None):
        """Constructor

        Args:
            image_path (str, optional): image_path. Defaults to None.
        """
        super().__init__()
        layout = QVBoxLayout()
        self.image_container = QLabel()
        self.image_container.setStyleSheet("border: 1px solid gray")
        self.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_container)

        self.image_container_current_size = self.image_container.size()
        self.image_path = image_path
        self.original_image = None
        self.latest_updated_image = None
        self.image_without_background = None
        self.out_image = QImage()
        self.last_point = None

        # Drawing flags and variables
        self.enable_drawing_line = False
        self.enable_drawing_horizontal_line = False
        self.enable_drawing_vertical_line = False
        self.enable_drawing_circle = False
        self.enable_drawing_rectangle = False
        self.pen_color = QColor("black")
        self.brush_size = 1
        self.first_point = None
        self.last_point = None

        self.enable_text = False

        if os.path.exists(image_path):
            self.image_without_background, self.original_image = remove_background(
                image_path=image_path
            )
            self.latest_updated_image = self.original_image
            self.out_image = QImage(
                self.latest_updated_image,
                self.latest_updated_image.shape[1],
                self.latest_updated_image.shape[0],
                self.latest_updated_image.shape[1] * 3,
                QImage.Format_BGR888,
            )
            self.current_pixmap = QPixmap(self.out_image)
        else:
            self.current_pixmap = QPixmap()

        self.update_image()
        self.setAcceptDrops(True)
        self.setLayout(layout)

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
                self.width() + event.pixelDelta().y(),
                self.height() + event.pixelDelta().y(),
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
        self.current_pixmap = QPixmap(self.out_image)
        self.update_image()

    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.drawPixmap(self.current_pixmap.rect(), self.current_pixmap)

    def map_to_image_coords(self, mouse_pos):
        image_container_size = self.image_container.size()
        pixmap_size = self.image_container.pixmap().size()

        # Calculate scale ratios
        scale_x = pixmap_size.width() / image_container_size.width()
        scale_y = pixmap_size.height() / image_container_size.height()

        # Map image_container coordinates to pixmap coordinates
        image_x = mouse_pos.x() * scale_x
        image_y = mouse_pos.y() * scale_y

        return QPoint(image_x, image_y)

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        """Called when the user moves the mouse while it's pressed.
        TODO: Convert from image_container's coordinates to pixmap's.

        Args:
            ev (QMouseEvent): Event data related to the mouse's position.
        """
        # self.last_point = ev.position()
        self.last_point = self.map_to_image_coords(ev.position())
        tmp_pixmap = self.current_pixmap.copy()
        with QPainter(tmp_pixmap) as painter:
            painter.setPen(QPen(self.pen_color, self.brush_size))
            if self.first_point:
                if self.enable_drawing_rectangle:
                    rect = QRect(
                        min(self.first_point.x(), self.last_point.x()),
                        min(self.first_point.y(), self.last_point.y()),
                        abs(self.first_point.x() - self.last_point.x()),
                        abs(self.first_point.y() - self.last_point.y()),
                    )
                    painter.drawRect(rect)
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
        # self.first_point = ev.position()
        self.first_point = self.map_to_image_coords(ev.position())

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
                if self.enable_drawing_rectangle:
                    rect = QRect(
                        min(self.first_point.x(), self.last_point.x()),
                        min(self.first_point.y(), self.last_point.y()),
                        abs(self.first_point.x() - self.last_point.x()),
                        abs(self.first_point.y() - self.last_point.y()),
                    )
                    painter.drawRect(rect)
                    self.update_image()

                elif self.enable_drawing_circle:
                    radius = (self.last_point - self.first_point).manhattanLength() // 2
                    center = self.first_point + (self.last_point - self.first_point) / 2
                    painter.drawEllipse(center, radius, radius)
                    self.update_image()

                elif self.enable_drawing_horizontal_line:
                    painter.drawLine(
                        self.first_point.x(),
                        self.first_point.y(),
                        self.last_point.x(),
                        self.first_point.y(),
                    )
                    self.update_image()

                elif self.enable_drawing_vertical_line:
                    painter.drawLine(
                        self.first_point.x(),
                        self.first_point.y(),
                        self.first_point.x(),
                        self.last_point.y(),
                    )
                    self.update_image()

                elif self.enable_drawing_line:
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

    def remove_background(self):
        """
        Remove background of the image. In fact this will replace the original
        image with the one without background.
        """
        out_image = QImage(
            self.image_without_background,
            self.image_without_background.shape[1],
            self.image_without_background.shape[0],
            self.image_without_background.shape[1] * 4,
            QImage.Format_RGBA8888,
        )
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
        self.current_pixmap = QPixmap(out_image)
        self.update_image()
