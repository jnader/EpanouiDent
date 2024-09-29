"""
Custom image container widget
"""

from PySide6.QtCore import Qt, QPoint
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

        self.image_path = image_path
        self.original_image = None
        self.latest_updated_image = None
        self.image_without_background = None
        self.out_image = QImage()
        self.last_point = None
        self.enable_drawing = False
        self.pen_color = None
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

    def update_image(self):
        """Update the image display based on the widget's size.
        TODO: There's an issue, it redraws for all iterations."""
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
        self.image_container.setPixmap(
            self.current_pixmap  # .scaled(
            # self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            # )
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

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        if not self.enable_drawing:
            return
        if not self.current_pixmap:
            return
        painter = QPainter(self.current_pixmap)
        painter.setPen(self.pen_color)
        if self.last_point:
            painter.drawLine(
                self.last_point, QPoint(ev.position().x(), ev.position().y())
            )

        self.last_point = QPoint(ev.position().x(), ev.position().y())
        self.update_image()

    # def mousePressEvent(self, ev: QMouseEvent) -> None:
    #     if not self.enable_drawing:
    #         return
    #     if not self.current_pixmap or not self.enable_drawing:
    #         return
    #     painter = QPainter(self.current_pixmap)
    #     painter.setPen(QColor.fromRgb(255, 0, 0, 255))
    #     painter.drawPoint(ev.position().x(), ev.position().y())
    #     self.update()

    # def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
    #     self.last_point = None

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
        self.image_container.setPixmap(self.current_pixmap)  # .scaled(self.size(), Qt.KeepAspectRatio)

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
        self.image_container.setPixmap(self.current_pixmap)  # .scaled(self.size(), Qt.KeepAspectRatio)

