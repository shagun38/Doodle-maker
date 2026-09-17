# preprocessing.py

import cv2
import numpy as np


def preprocess_image(image):
    if image is None:
        raise ValueError("image cannot be none")

    # apply a small blur to reduce camera noise
    denoised = cv2.GaussianBlur(
        image,
        (3, 3),
        0
    )

    # convert the image to hsv
    hsv = cv2.cvtColor(denoised,cv2.COLOR_BGR2HSV)

    # separate the brightness channel
    value = hsv[:, :, 2]

    # estimate large-scale illumination
    illumination = cv2.GaussianBlur(value,(0, 0),25)

    # prevent division by zero
    illumination = np.maximum(illumination,1)

    # normalize brightness using the estimated illumination
    corrected_value = (value.astype(np.float32) /illumination.astype(np.float32))

    # normalize the corrected brightness to 0-255
    corrected_value = cv2.normalize(corrected_value,None,0,255,cv2.NORM_MINMAX)

    # convert the corrected brightness to uint8
    corrected_value = corrected_value.astype(np.uint8)

    # replace the original value channel
    corrected_hsv = hsv.copy()

    corrected_hsv[:, :, 2] = corrected_value

    # convert corrected hsv image back to bgr
    corrected_color = cv2.cvtColor(corrected_hsv,cv2.COLOR_HSV2BGR)

    # create grayscale version from corrected color
    corrected_grayscale = cv2.cvtColor(corrected_color,cv2.COLOR_BGR2GRAY)

    return {
        "original": image,
        "color": corrected_color,
        "grayscale": corrected_grayscale
    }