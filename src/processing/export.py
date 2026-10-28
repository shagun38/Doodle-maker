import os
import cv2
import numpy as np

import os
import cv2
import numpy as np

def save_as_svg(paths, width, height, output_filename):
    if not paths:
        raise ValueError("No paths to export")

    svg_content = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">'
    ]

    path_commands = []
    
    for path in paths:
        if len(path) < 3:
            continue
            
        # M = Move to the first point
        commands = [f"M {path[0][0]},{path[0][1]}"]
        
        # L = Draw a line to subsequent points
        for x, y in path[1:]:
            commands.append(f"L {x},{y}")
            
        # Z = Close the loop back to the start
        commands.append("Z")
        
        path_commands.append(" ".join(commands))

    # Join all sub-paths into one massive compound string
    full_path_data = " ".join(path_commands)

    # Use fill-rule="evenodd" to create negative space for the inner boundaries
    svg_content.append(
        f'  <path d="{full_path_data}" fill="black" fill-rule="evenodd" stroke="none" />'
    )

    svg_content.append('</svg>')

    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg_content))
    
    print(f"Successfully saved vector graphic to: {os.path.abspath(output_filename)}")

# (Keep your existing save_as_png function below this)

def save_as_png(paths, width, height, output_filename):
    if not paths:
        raise ValueError("No paths to export")

    # Create a blank 4-channel matrix (RGBA) initialized to fully transparent
    canvas = np.zeros((height, width, 4), dtype=np.uint8)

    all_contours = []
    for path in paths:
        if len(path) >= 3:
            all_contours.append(np.array(path, dtype=np.int32))

    # CRITICAL FIX: Pass all contours simultaneously so OpenCV mathematically cuts out the holes
    if all_contours:
        cv2.fillPoly(canvas, all_contours, (0, 0, 0, 255), lineType=cv2.LINE_AA)

    cv2.imwrite(output_filename, canvas)
    print(f"Successfully saved raster graphic to: {os.path.abspath(output_filename)}")