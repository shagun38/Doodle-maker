# cleaning.py

import cv2
import numpy as np


def remove_small_components(mask, min_area=20):
    # check that a mask was provided
    if mask is None:
        raise ValueError("mask cannot be none")

    # make sure the mask is binary
    if len(mask.shape) != 2:
        raise ValueError(
            "mask must be a single-channel image"
        )

    # find connected components
    number_of_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask,
        connectivity=8
    )

    # create an empty mask for the cleaned result
    cleaned_mask = np.zeros_like(mask)

    # examine every connected component
    for label in range(1, number_of_labels):

        # get the area of this component
        area = stats[label, cv2.CC_STAT_AREA]

        # keep only components larger than the minimum area
        if area >= min_area:
            cleaned_mask[labels == label] = 255

    return cleaned_mask

def detect_background_lines(mask):
    # check that a mask was provided
    if mask is None:
        raise ValueError("mask cannot be none")

    # detect straight line segments
    lines = cv2.HoughLinesP(
        mask,
        rho=1,
        theta=np.pi / 180,
        threshold=50,
        minLineLength=100,
        maxLineGap=30
    )

    # create an empty image for visualization
    detected_lines = np.zeros_like(mask)

    # if no lines were found, return the empty image
    if lines is None:
        return detected_lines

    # examine every detected line
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)

        # calculate line length
        length = np.sqrt(
            (x2 - x1) ** 2 +
            (y2 - y1) ** 2
        )

        # calculate angle in degrees
        angle = np.degrees(
            np.arctan2(
                y2 - y1,
                x2 - x1
            )
        )

        # normalize the angle
        if angle < 0:
            angle += 180

        # keep long, approximately horizontal lines
        if length >= 100 and (
            angle <= 15 or angle >= 165
        ):
            cv2.line(
                detected_lines,
                (x1, y1),
                (x2, y2),
                255,
                2
            )

    return detected_lines

def remove_background_lines(mask):
    if mask is None:
        raise ValueError("mask cannot be none")

    result = mask.copy()

    # Work with a binary image
    binary = cv2.threshold(
        mask, 127, 255, cv2.THRESH_BINARY
    )[1]

    # Detect straight line segments
    edges = cv2.Canny(binary, 50, 150)

    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=50,
        minLineLength=int(mask.shape[1] * 0.30),
        maxLineGap=15
    )

    if lines is None:
        return result

    candidates = []

    for line in lines:
        line = np.asarray(line).reshape(-1)

        if len(line) != 4:
            continue

        x1, y1, x2, y2 = line

        dx = x2 - x1
        dy = y2 - y1

        length = np.sqrt(dx * dx + dy * dy)

        angle = np.degrees(np.arctan2(dy, dx))

        # Notebook lines are usually close to horizontal.
        # Allow some camera perspective.
        if abs(angle) > 15 and abs(angle - 180) > 15:
            continue

        candidates.append(
            (x1, y1, x2, y2, length, angle)
        )

    if len(candidates) < 3:
        return result

    # -------------------------------------------------
    # Find the dominant notebook-line angle
    # -------------------------------------------------

    angles = np.array([line[5] for line in candidates])

    dominant_angle = np.median(angles)

    # Keep only lines close to the dominant angle
    similar_lines = [
        line
        for line in candidates
        if abs(line[5] - dominant_angle) <= 3
    ]

    if len(similar_lines) < 3:
        return result

    # -------------------------------------------------
    # Sort lines by vertical position
    # -------------------------------------------------

    similar_lines.sort(
        key=lambda line: (line[1] + line[3]) / 2
    )

    # -------------------------------------------------
    # Find regularly spaced lines
    # -------------------------------------------------

    selected = []

    positions = [
        (line[1] + line[3]) / 2
        for line in similar_lines
    ]

    for i, line in enumerate(similar_lines):

        if len(selected) >= 2:

            previous_positions = [
                (l[1] + l[3]) / 2
                for l in selected[-3:]
            ]

            spacings = [
                abs(positions[i] - p)
                for p in previous_positions
            ]

            # If this line has a reasonable distance
            # from previous background lines, keep it.
            if any(15 <= spacing <= 150 for spacing in spacings):
                selected.append(line)

        else:
            selected.append(line)

    # We need several repeated lines.
    if len(selected) < 3:
        return result

    # -------------------------------------------------
    # Create background-line mask
    # -------------------------------------------------

    background_mask = np.zeros_like(mask)

    for x1, y1, x2, y2, length, angle in selected:

        cv2.line(
            background_mask,
            (x1, y1),
            (x2, y2),
            255,
            thickness=3
        )

    # -------------------------------------------------
    # Remove only detected background pixels
    # -------------------------------------------------

    result[background_mask > 0] = 0

    return result