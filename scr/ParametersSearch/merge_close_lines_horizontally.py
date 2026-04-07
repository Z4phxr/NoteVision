import numpy as np


def normalize_horizontal_lines(lines, threshold=5):
    """
    Merge nearby horizontal lines by grouping lines with similar vertical position.

    For each close group, keep the first line's y-position (no multi-line y averaging).
    Output lines are normalized to the same x-range, using global min x-start and
    global max x-end computed from all detected lines.

    Args:
        lines (np.ndarray): OpenCV HoughLinesP output format: shape (N, 1, 4) where each
                           element is [[x1, y1, x2, y2]]. Can be None or empty.
        threshold (int): Maximum vertical distance (pixels) between lines to be merged.
                        Default: 5 pixels.

    Returns:
        list: Merged lines in format [np.array([[x1, y1, x2, y2]]), ...].
              Returns empty list if no lines detected.

    """
    if lines is None or lines.size == 0:
        return []

    # Normalize: ensure x1 <= x2 for each line
    normalized = []
    for line_coords_array in lines:
        x1, y1, x2, y2 = line_coords_array[0]
        if x1 > x2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        normalized.append((x1, y1, x2, y2))

    # Sort by vertical position (average y-coordinate)
    normalized.sort(key=lambda line: (line[1] + line[3]) / 2)

    # Global x normalization: all merged lines will share these x endpoints.
    global_x1 = min(line[0] for line in normalized)
    global_x2 = max(line[2] for line in normalized)

    merged = []
    used = [False] * len(normalized)

    for i, current_line in enumerate(normalized):
        if used[i]:
            continue

        x1_curr, y1_curr, x2_curr, y2_curr = current_line
        avg_y_curr = (y1_curr + y2_curr) / 2

        # Find nearby lines to merge
        for j, compare_line in enumerate(normalized):
            if i == j or used[j]:
                continue

            x1_cmp, y1_cmp, x2_cmp, y2_cmp = compare_line
            avg_y_cmp = (y1_cmp + y2_cmp) / 2

            # Check if within threshold distance
            if abs(avg_y_curr - avg_y_cmp) < threshold:
                used[j] = True

        # Keep first line y for group; use shared global x-range for normalization.
        merged_y = int(round((y1_curr + y2_curr) / 2))
        merged.append((global_x1, merged_y, global_x2, merged_y))
        used[i] = True

    # Convert back to OpenCV format: list of [[x1, y1, x2, y2]] arrays
    return [np.array([line]) for line in merged]
