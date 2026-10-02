import cv2
import numpy as np


def simplify_paths(paths, epsilon_ratio=0.01):
    if paths is None:
        raise ValueError("paths cannot be None")

    simplified_paths = []

    for path in paths:
        if path is None or len(path) < 2:
            continue

        points = np.array(
            path,
            dtype=np.int32
        ).reshape(-1, 1, 2)

        perimeter = cv2.arcLength(
            points,
            False
        )

        epsilon = epsilon_ratio * perimeter

        simplified = cv2.approxPolyDP(
            points,
            epsilon,
            False
        )

        simplified_path = (
            simplified.reshape(-1, 2).tolist()
        )

        if len(simplified_path) >= 2:
            simplified_paths.append(
                simplified_path
            )

    return simplified_paths