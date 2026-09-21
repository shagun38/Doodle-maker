# cleaning.py

import cv2
import numpy as np


def remove_small_components(mask, min_area=50):
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

    # # create an empty mask for the cleaned result
    # cleaned_mask = np.zeros_like(mask)

    # # examine every connected component
    # for label in range(1, number_of_labels):

    #     # get the area of this component
    #     area = stats[label, cv2.CC_STAT_AREA]

    #     # keep only components larger than the minimum area
    #     if area >= min_area:
    #         cleaned_mask[labels == label] = 255

    areas = []

    for label in range(1, number_of_labels):
        area = stats[label, cv2.CC_STAT_AREA]
        areas.append(area)

    print("Number of components:", len(areas))
    print("Smallest component areas:", sorted(areas)[:30])

    cleaned_mask = np.zeros_like(mask)

    for label in range(1, number_of_labels):
        area = stats[label, cv2.CC_STAT_AREA]

        if area >= min_area:
            cleaned_mask[labels == label] = 255

    return cleaned_mask

