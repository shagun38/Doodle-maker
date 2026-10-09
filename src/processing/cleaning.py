import cv2
import numpy as np

def remove_small_components(mask, min_area=100):
    if mask is None:
        raise ValueError("mask cannot be none")

    if len(mask.shape) != 2:
        raise ValueError(
            "mask must be a single-channel image"
        )
    
    number_of_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask,connectivity=8)
    cleaned_mask = np.zeros_like(mask)
    
    for label in range(1, number_of_labels):
        area = stats[label, cv2.CC_STAT_AREA]

        if area >= min_area:
            cleaned_mask[labels == label] = 255

    return cleaned_mask

