import math

import cv2

import merge_close_lines_horizontally as merge_utils
from scr.ParametersSearch.models import ParamSet
from scr.ParametersSearch.utils import colors


def draw_lines(image, params_set: ParamSet):
    """Detect and draw merged horizontal lines using values from ParamSet.

    Returns:
        tuple: (image_with_lines, merged_lines)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, params_set.canny_low, params_set.canny_high, apertureSize=3)

    raw_lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=math.pi / 180,
        threshold=params_set.threshold,
        minLineLength=params_set.min_len_ratio * image.shape[0],
        maxLineGap=params_set.max_gap,
    )

    merged = merge_utils.normalize_horizontal_lines(raw_lines)

    image_with_lines = image.copy()
    for i, line in enumerate(merged):
        x1, y1, x2, y2 = line[0]
        color = colors[i % len(colors)]
        cv2.line(image_with_lines, (x1, y1), (x2, y2), color, 1)

    return image_with_lines, merged
