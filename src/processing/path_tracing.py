import cv2
import numpy as np

def trace_skeleton_paths(skeleton):
    if skeleton is None:
        raise ValueError("skeleton cannot be None")

    if len(skeleton.shape) != 2:
        raise ValueError("skeleton must be a single-channel image")

    # RETR_LIST extracts ALL contours (inner eyes, smiles, outer contours)
    contours, _ = cv2.findContours(
        skeleton, 
        cv2.RETR_LIST, 
        cv2.CHAIN_APPROX_NONE
    )

    paths = []
    height, width = skeleton.shape

    for contour in contours:
        pts = contour.reshape(-1, 2)

        # Ignore tiny specks/noise (fewer than 5 pixels)
        if len(pts) < 5:
            continue

        # Drop duplicate consecutive points (which crash splprep)
        filtered_pts = [pts[0]]
        for pt in pts[1:]:
            if not np.array_equal(pt, filtered_pts[-1]):
                filtered_pts.append(pt)

        path = np.array(filtered_pts)

        touches_border = any(
            x == 0 or y == 0 or x == width - 1 or y == height - 1
            for x, y in path
        )

        if len(path) >= 5 and not touches_border:
            paths.append(path.tolist())

    return paths