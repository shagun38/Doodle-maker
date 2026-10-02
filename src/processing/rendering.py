import cv2
import numpy as np


def render_vectors(vectors, width, height):
    if vectors is None:
        raise ValueError("vectors cannot be None")

    if width <= 0 or height <= 0:
        raise ValueError(
            "width and height must be greater than zero"
        )

    canvas = np.zeros(
        (height, width, 3),
        dtype=np.uint8
    )

    for vector in vectors:
        if vector is None:
            continue

        points = vector.get("points")
        line_width = vector.get("width")

        if points is None or len(points) < 2:
            continue

        if line_width is None or line_width <= 0:
            continue

        points_array = np.array(
            points,
            dtype=np.int32
        )

        cv2.polylines(
            canvas,
            [points_array],
            False,
            (255, 255, 255),
            thickness=line_width,
            lineType=cv2.LINE_AA
        )

    return canvas