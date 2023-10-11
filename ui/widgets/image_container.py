"""
Custom image container widget
"""

from PySide6.QtCore import *
from PySide6.QtWidgets import QLabel
import cv2
from PySide6.QtGui import QPixmap, QDropEvent, QDragEnterEvent, QImageReader, QImage
from backend.background_removal import remove_background

class ImageContainer(QLabel):
    def __init__(self, image_path : str = None):
        """ Constructor

        Args:
            image_path (str, optional): image_path. Defaults to None.
        """
        super().__init__()
        self.setup(image_path)

    def setup(self, image_path : str = None):
        """ Setup the image container

        Args:
            image_path (str, optional): Image path
        """
        pixmap = QPixmap()
        self.image_without_background = None
        self.setPixmap(pixmap)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """ DragEnter event

        Args:
            event (QDragEnterEvent): QDragEnterEvent
        """
        # Define the accepted drop action
        if event.mimeData().hasUrls() and len(event.mimeData().urls()) == 1:
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """ dropEvent

        Args:
            event (QDropEvent): QDropEvent
        """
        # Get the file path of the dropped image
        image_path = event.mimeData().urls()[0].toLocalFile()

        # Check if it's an image file
        image_reader = QImageReader(image_path)
        if image_reader.format().isEmpty():
            return

        # Update and display pixmap
        # TODO: Only create image without background and leave it internal. Display on other action.
        self.image_without_background = remove_background(image_path=image_path)
        new_path = image_path.replace(".","_no_bg.")
        cv2.imwrite(f"{new_path}", cv2.cvtColor(self.image_without_background, cv2.COLOR_BGRA2RGBA))
        out_image = QImage(self.image_without_background, self.image_without_background.shape[1],\
                        self.image_without_background.shape[0], self.image_without_background.shape[1] * 4,\
                        QImage.Format_RGBA8888)
        pixmap = QPixmap(out_image)
        self.setPixmap(pixmap)#.scaled(self.size(), Qt.KeepAspectRatio))
