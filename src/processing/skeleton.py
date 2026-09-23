import cv2
import numpy as np


def skeletonize_mask(mask):
    if mask is None:
        raise ValueError("mask cannot be None")

    if len(mask.shape) != 2:
        raise ValueError(
            "mask must be a single-channel image"
        )

    binary = mask.copy()
    binary[binary > 0] = 255

    skeleton = cv2.ximgproc.thinning(
        binary,
        thinningType=cv2.ximgproc.THINNING_ZHANGSUEN
    )

    return skeleton


def clean_skeleton(skeleton, min_component_size=10):
    if skeleton is None:
        raise ValueError("skeleton cannot be None")

    if len(skeleton.shape) != 2:
        raise ValueError(
            "skeleton must be a single-channel image"
        )

    cleaned = np.zeros_like(skeleton)

    number_of_labels, labels, stats, _ = (
        cv2.connectedComponentsWithStats(
            skeleton,
            connectivity=8
        )
    )

    for label in range(1, number_of_labels):
        area = stats[label, cv2.CC_STAT_AREA]

        if area >= min_component_size:
            cleaned[labels == label] = 255

    return cleaned


def close_skeleton_gaps(mask, kernel_size=3):
    if mask is None:
        raise ValueError("mask cannot be None")

    if len(mask.shape) != 2:
        raise ValueError(
            "mask must be a single-channel image"
        )

    kernel = cv2.getStructuringElement(
        cv2.MORPH_CROSS,
        (kernel_size, kernel_size)
    )

    closed = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    return closed