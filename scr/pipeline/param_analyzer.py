import json
from pathlib import Path
from typing import List, Optional

import cv2

from scr.models.analysis import ParamSet, ParamSetResult, PhotoResult



class ParamAnalyzer:
    """Parameter search utilities for horizontal line detection."""

    _THRESHOLDS = [20, 30, 40, 50, 60, 80, 100, 120, 150]
    _MIN_LEN_RATIOS = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    _MAX_GAPS = [5, 10, 15, 20, 30, 40, 60]
    _CANNY_LOWS = [10, 20, 30, 50, 70]
    _CANNY_HIGHS = [80, 100, 120, 150, 200, 250]

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

        Output contains per-ParamSet results with per-image details and summary counts.
        """
        from scr.io.dataset_store import DatasetJsonStore

        dataset = DatasetJsonStore.load(dataset_path)
        dataset.data_dir = data_dir
        param_combos = cls.create_param_set() if params is None else params
        total_pages = len(dataset.pages)

        results: List[ParamSetResult] = []

        output_path.parent.mkdir(parents=True, exist_ok=True)
        for param_index, param_set in enumerate(param_combos, start=1):
            analyzer = cls(param_set)
            photo_results: List[PhotoResult] = []

            for page_index, page in enumerate(dataset.pages, start=1):
                image_path = Path(page.image_path)
                if not image_path.is_absolute():
                    image_path = data_dir / image_path

                image = cv2.imread(str(image_path))
                if image is None:
                    photo_results.append(PhotoResult(
                        path=page.image_path,
                        found_lines=None,
                        target_lines=page.staff_line_count,
                    ))
                    print(
                        f"[{param_index}/{len(param_combos)}] "
                        f"{page_index}/{total_pages} {page.image_path}: missing image"
                    )
                    continue

                merged = page.detect_merged_lines(image, analyzer.param_set)
                found_lines = len(merged)
                target_lines = page.staff_line_count

                photo_results.append(PhotoResult(
                    path=page.image_path,
                    found_lines=found_lines,
                    target_lines=target_lines,
                ))
                print(
                    f"[{param_index}/{len(param_combos)}] "
                    f"{page_index}/{total_pages} {page.image_path}: "
                    f"{found_lines}/{target_lines}"
                )

            score = ParamSetResult._compute_score(photo_results)
            results.append(ParamSetResult(
                param_set=param_set,
                photos=photo_results,
                score=score,
            ))

        payload = {
            "results": [result.to_dict() for result in results],
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path


    @staticmethod
    def load_results(path: Path | str) -> List[ParamSetResult]:
        """Load analysis results saved by run_full_analysis."""
        resolved_path = Path(path)
        if not resolved_path.exists():
            raise FileNotFoundError(
                f"Analysis results not found: {resolved_path}. "
                "Run param analysis first or update the input_path."
            )
        payload = json.loads(resolved_path.read_text(encoding="utf-8"))
        raw_results = payload.get("results")
        if raw_results is None:
            raise ValueError("Invalid analysis payload: missing 'results'.")
        return [ParamSetResult.from_dict(item) for item in raw_results]

    @staticmethod
    def visualize(input_path: Path, output_path: Path) -> None:
        results: List[ParamSetResult] = ParamAnalyzer.load_results(input_path)
        for set_result in results:
            if set_result.score < 1.0:
                continue
            print(f"[{set_result.score:.2f}] ")



