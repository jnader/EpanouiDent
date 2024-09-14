"""
Custom image container widget
"""

from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtWidgets import QLabel, QWidget, QGridLayout, QPushButton
import cv2
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
from backend.background_removal import remove_background


class ImageProcessingSettings(QWidget):
    """Custom widget for the buttons used in the image edit view

    Args:
        QWidget (_type_): Inherits from QWidget
    """

    def __init__(self, base_path: str):
        """Constructor

        Args:
            base_path (str): Base path to main.py
        """
        super().__init__()
        self.base_path = base_path
        self.setFixedSize(100, 100)
        grid_layout = QGridLayout()
        self.draw_button = QPushButton(
            icon=QIcon(os.path.join(self.base_path, "data", "icons", "draw.jpg"))
        )
        self.draw_button.setFixedSize(QSize(50, 50))
        self.draw_button.setIconSize(QSize(50, 50))
        # self.draw_button.clicked.connect(self.enable_drawing)
        grid_layout.addWidget(self.draw_button, 1, 1)

        self.text_button = QPushButton(
            icon=QIcon(os.path.join(self.base_path, "data", "icons", "text.png"))
        )
        self.text_button.setFixedSize(QSize(50, 50))
        self.text_button.setIconSize(QSize(50, 50))
        # self.text_button.clicked.connect(self.enable_text)
        grid_layout.addWidget(self.text_button, 2, 1)
        self.setLayout(grid_layout)


class ImageContainer(QLabel):
    def __init__(self, image_path: str = None):
        """Constructor

        Args:
            image_path (str, optional): image_path. Defaults to None.
        """
        super().__init__()
        self.image_path = image_path
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.last_point = None
        self.enable_drawing = False
        self.enable_text = False
        self.current_pixmap = QPixmap()
        self.setup(image_path)

    def setup(self, image_path: str = None):
        """Setup the image container

        Args:
            image_path (str, optional): Image path
        """
        self.original_image = None
        self.image_without_background = None
        self.setPixmap(self.current_pixmap)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """DragEnter event

        Args:
            event (QDragEnterEvent): QDragEnterEvent
        """
        # Define the accepted drop action
        if event.mimeData().hasUrls() and len(event.mimeData().urls()) == 1:
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """dropEvent

        Args:
            event (QDropEvent): QDropEvent
        """
        # Get the file path of the dropped image
        self.image_path = event.mimeData().urls()[0].toLocalFile()

        # Check if it's an image file
        image_reader = QImageReader(self.image_path)
        if image_reader.format().isEmpty():
            return

        # Update and display pixmap
        self.image_without_background, self.original_image = remove_background(
            image_path=self.image_path
        )
        self.reset_original_image()
        self.save_no_background_image()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.current_pixmap.rect(), self.current_pixmap)

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        if not self.enable_drawing:
            return
        if not self.current_pixmap:
            return
        painter = QPainter(self.current_pixmap)
        painter.setPen(QColor.fromRgb(255, 0, 0, 255))
        if self.last_point:
            painter.drawLine(
                self.last_point, QPoint(ev.position().x(), ev.position().y())
            )

        self.last_point = QPoint(ev.position().x(), ev.position().y())
        self.update()

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if not self.enable_drawing:
            return
        if not self.current_pixmap or not self.enable_drawing:
            return
        painter = QPainter(self.current_pixmap)
        painter.setPen(QColor.fromRgb(255, 0, 0, 255))
        painter.drawPoint(ev.position().x(), ev.position().y())
        self.update()

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        self.last_point = None

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
        self.setPixmap(self.current_pixmap)  # .scaled(self.size(), Qt.KeepAspectRatio)

    def reset_original_image(self):
        """
        Resets original image with background.
        """
        out_image = QImage(
            self.original_image,
            self.original_image.shape[1],
            self.original_image.shape[0],
            self.original_image.shape[1] * 4,
            QImage.Format_RGBA8888,
        )
        self.current_pixmap = QPixmap(out_image)
        self.setPixmap(self.current_pixmap)  # .scaled(self.size(), Qt.KeepAspectRatio)

    def save_no_background_image(self):
        """
        Saves image without the background.
        TODO: We should the latest image after every manipulation
        TODO: Think about the undo process.
        """
        new_path = self.image_path.replace(".", "_no_bg.")
        cv2.imwrite(
            f"{new_path}",
            cv2.cvtColor(self.image_without_background, cv2.COLOR_BGRA2RGBA),
        )
