import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

import cv2


@dataclass(frozen=True)
class ParamSet:
    """Single Hough/Canny parameter combination."""

    threshold: int
    min_len_ratio: float
    max_gap: int
    canny_low: int
    canny_high: int


class ParamAnalyzer:
    """Parameter search utilities for horizontal line detection."""

    _THRESHOLDS = [30, 40, 50, 60, 80, 100]
    _MIN_LEN_RATIOS = [0.3, 0.4, 0.5, 0.6]
    _MAX_GAPS = [10, 20, 30, 40]
    _CANNY_LOWS = [20, 30, 50]
    _CANNY_HIGHS = [100, 150, 200]

    def __init__(self, param_set: ParamSet) -> None:
        self.param_set = param_set

    @classmethod
    def create_param_set(cls) -> List[ParamSet]:
        """Return all parameter combinations from the built-in search space."""
        param_sets = []
        for threshold in cls._THRESHOLDS:
            for min_len_ratio in cls._MIN_LEN_RATIOS:
                for max_gap in cls._MAX_GAPS:
                    for canny_low in cls._CANNY_LOWS:
                        for canny_high in cls._CANNY_HIGHS:
                            param_sets.append(ParamSet(
                                threshold=threshold,
                                min_len_ratio=min_len_ratio,
                                max_gap=max_gap,
                                canny_low=canny_low,
                                canny_high=canny_high,
                            ))
        return param_sets

    @classmethod
    def run_full_analysis(
        cls,
        dataset_path: Path,
        data_dir: Path,
        output_path: Path,
        params: Optional[List[ParamSet]] = None,
    ) -> Path:
        """Evaluate all ParamSets on all pages and save results as JSON.

        Output contains per-image results and per-ParamSet summary counts.
        """
        from scr.io.dataset_store import DatasetJsonStore

        dataset = DatasetJsonStore.load(dataset_path)
        dataset.data_dir = data_dir
        param_combos = cls.create_param_set() if params is None else params
        total_pages = len(dataset.pages)

        per_image = []
        summary = []

        output_path.parent.mkdir(parents=True, exist_ok=True)
        for param_set in param_combos:
            analyzer = cls(param_set)
            matched = 0
            evaluated = 0

            for page in dataset.pages:
                image_path = Path(page.image_path)
                if not image_path.is_absolute():
                    image_path = data_dir / image_path

                image = cv2.imread(str(image_path))
                if image is None:
                    per_image.append({
                        "param_set": asdict(param_set),
                        "image_path": page.image_path,
                        "expected_lines": page.staff_line_count,
                        "merged_count": None,
                        "matched": False,
                        "status": "missing_image",
                    })
                    continue

                merged = page.detect_merged_lines(image, analyzer.param_set)
                merged_count = len(merged)
                expected = page.staff_line_count
                is_match = merged_count == expected

                if is_match:
                    matched += 1
                evaluated += 1

                per_image.append({
                    "param_set": asdict(param_set),
                    "image_path": page.image_path,
                    "expected_lines": expected,
                    "merged_count": merged_count,
                    "matched": is_match,
                    "status": "ok",
                })

            summary.append({
                "param_set": asdict(param_set),
                "matched": matched,
                "evaluated": evaluated,
                "total_pages": total_pages,
            })

        payload = {
            "per_image": per_image,
            "summary": summary,
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path
