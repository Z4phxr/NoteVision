from dataclasses import dataclass


@dataclass(frozen=True)
class ParamSet:
    """Single Hough/Canny parameter combination."""

    threshold: int
    min_len_ratio: float
    max_gap: int
    canny_low: int
    canny_high: int