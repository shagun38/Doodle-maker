import cv2
import numpy as np
from scipy.interpolate import splprep, splev

def simplify_paths(paths, max_deviation=1.5, points_per_unit=0.5):
    if paths is None:
        raise ValueError("paths cannot be None")

    simplified_paths = []

    for path in paths:
        if path is None or len(path) < 2:
            continue

        points = np.array(path, dtype=np.int32).reshape(-1, 1, 2)

        # 1. RDP simplification with absolute pixel tolerance
        # max_deviation of 1.5 keeps vertices close to the original drawn line
        simplified = cv2.approxPolyDP(points, max_deviation, False)
        control_points = simplified.reshape(-1, 2)

        # Deduplicate any adjacent vertices
        unique_mask = np.ones(len(control_points), dtype=bool)
        for i in range(1, len(control_points)):
            if np.all(control_points[i] == control_points[i - 1]):
                unique_mask[i] = False
        control_points = control_points[unique_mask]

        n_pts = len(control_points)

        # 2. Fit B-Spline if enough unique points exist
        if n_pts >= 4:
            x = control_points[:, 0].astype(float)
            y = control_points[:, 1].astype(float)

            # Check if all points are collinear or identical
            dx = np.diff(x)
            dy = np.diff(y)
            dist = np.hypot(dx, dy)
            total_len = np.sum(dist)

            if total_len < 5.0 or np.any(dist == 0):
                simplified_paths.append(control_points.tolist())
                continue

            try:
                # k=3 for cubic splines; s=len(control_points) provides moderate smoothing
                tck, u = splprep([x, y], s=len(control_points), k=3)
                
                # Dynamic number of output points based on arc length
                num_samples = max(int(total_len * points_per_unit), 15)
                u_fine = np.linspace(0, 1, num_samples)
                x_smooth, y_smooth = splev(u_fine, tck)

                smooth_path = np.column_stack((x_smooth, y_smooth)).astype(np.int32).tolist()
                simplified_paths.append(smooth_path)
            except Exception:
                # Fallback to straight RDP segments if splprep fails condition checks
                simplified_paths.append(control_points.tolist())
        else:
            simplified_paths.append(control_points.tolist())

    return simplified_paths