# image_input.py

import os
import cv2

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


MAX_WIDTH = 4096
MAX_HEIGHT = 4096


def load_image(image_path):
    # check whether the provided path exists
    if not os.path.isfile(image_path):
        raise FileNotFoundError(
            f"image file not found: {image_path}"
        )
    
    extension = os.path.splitext(image_path)[1].lower()

    # check whether the image format is supported
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"unsupported image format: {extension}"
        )

    # read the image using opencv
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    # check whether opencv successfully decoded the image
    if image is None:
        raise ValueError(
            "the image could not be decoded or may be corrupted"
        )

    height, width = image.shape[:2]

    if width <= 0 or height <= 0:
        raise ValueError(
            "image has invalid dimensions"
        )

    if width > MAX_WIDTH or height > MAX_HEIGHT:
        raise ValueError(
            f"image is too large: {width}x{height}. "
            f"maximum allowed size is "
            f"{MAX_WIDTH}x{MAX_HEIGHT}"
        )

    channels = image.shape[2] if len(image.shape) == 3 else 1

    return {
        "image": image,
        "width": width,
        "height": height,
        "channels": channels,
        "format": extension
    }