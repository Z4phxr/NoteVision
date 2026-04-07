from scr.ParametersSearch.models import ParamSet

colors = [
    (255, 0, 0),
    (255, 165, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 0, 255),
]

thresholds = [30, 40, 50, 60, 80, 100]
min_len_ratios = [0.3, 0.4, 0.5, 0.6]
max_gaps = [10, 20, 30, 40]
canny_lows = [20, 30, 50]
canny_highs = [100, 150, 200]


def create_param_set():
    """Create list of all parameter combinations."""
    param_sets = []
    for threshold in thresholds:
        for min_len_ratio in min_len_ratios:
            for max_gap in max_gaps:
                for canny_low in canny_lows:
                    for canny_high in canny_highs:
                        param_sets.append(ParamSet(
                            threshold=threshold,
                            min_len_ratio=min_len_ratio,
                            max_gap=max_gap,
                            canny_low=canny_low,
                            canny_high=canny_high
                        ))
    return param_sets