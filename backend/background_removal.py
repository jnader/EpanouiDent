"""
Abstraction for image background removal
"""

import numpy as np
import cv2
from external.rembg.rembg import remove


def remove_background(image_path: str):
    """Removes background from image and image without background

    Args:
        image_path (str): Path to input image

    Output:
        output_image: Image without the background
        input_image: Original image

    """
    input_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    output_image = remove(input_image)
    output_image = cv2.cvtColor(output_image, cv2.COLOR_RGBA2BGRA)

    return output_image, input_image
