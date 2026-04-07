import numpy as np
import cv2
from merge_close_lines_horizontally import normalize_horizontal_lines
from scr.ParametersSearch.models import ParamSet
from scr.ParametersSearch.utils import create_param_set

def find_horizontal_line_params(image, target=None, params=None):
    """
    Search for best parameters based on detected line count.

    Args:
        image (np.ndarray): Input image (BGR format).
        target (int | None): Expected detected line count. If None, return all tested params.
        is_first (bool): Pipeline flag kept in signature.
        params (list[ParamSet] | None): Parameter sets to evaluate. If None,
            function uses `create_param_set()`.

    Returns:
        list[ParamSet]: Matching parameter sets.

    """
    param_combos = create_param_set() if params is None else params

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return_params = []

    for param_set in param_combos:
        edges = cv2.Canny(gray, param_set.canny_low, param_set.canny_high, apertureSize=3)
        raw_lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=param_set.threshold,
            minLineLength=param_set.min_len_ratio * image.shape[0],
            maxLineGap=param_set.max_gap
        )

        merged = normalize_horizontal_lines(raw_lines)
        count = len(merged)

        if target is None or count == target:
            return_params.append(param_set)

    return return_params


