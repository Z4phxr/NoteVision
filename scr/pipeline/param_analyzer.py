import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np


@dataclass(frozen=True)
class ParamSet:
    """Single Hough/Canny parameter combination."""

    threshold: int
    min_len_ratio: float
    max_gap: int
    canny_low: int
    canny_high: int


class ParamAnalyzer:
    """Horizontal line detection and parameter search using Hough/Canny.

    Instantiate with a `ParamSet` to use the image-processing instance methods.
    Use class/static methods for parameter space generation, search, and settings I/O.
    """

    COLORS: List[Tuple[int, int, int]] = [
        (255, 0, 0),
        (255, 165, 0),
        (255, 255, 0),
        (0, 255, 0),
        (0, 0, 255),
    ]

    _THRESHOLDS = [30, 40, 50, 60, 80, 100]
    _MIN_LEN_RATIOS = [0.3, 0.4, 0.5, 0.6]
    _MAX_GAPS = [10, 20, 30, 40]
    _CANNY_LOWS = [20, 30, 50]
    _CANNY_HIGHS = [100, 150, 200]

    def __init__(self, param_set: ParamSet) -> None:
        self.param_set = param_set


    def detect_merged_lines(self, image) -> List:
        """Detect merged horizontal lines using this analyzer's ParamSet.

        Returns:
            list of np.array([[x1, y1, x2, y2]]).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, self.param_set.canny_low, self.param_set.canny_high, apertureSize=3)
        raw_lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=math.pi / 180,
            threshold=self.param_set.threshold,
            minLineLength=self.param_set.min_len_ratio * image.shape[0],
            maxLineGap=self.param_set.max_gap,
        )
        return self.normalize_horizontal_lines(raw_lines)

    def draw_lines(self, image) -> Tuple:
        """Detect and draw merged horizontal lines on a copy of the image.

        Returns:
            tuple: (image_with_lines, merged_lines)
        """
        merged = self.detect_merged_lines(image)
        image_with_lines = image.copy()
        for i, line in enumerate(merged):
            x1, y1, x2, y2 = line[0]
            color = self.COLORS[i % len(self.COLORS)]
            cv2.line(image_with_lines, (x1, y1), (x2, y2), color, 1)
        return image_with_lines, merged

    def split_image_by_lines(self, image, threshold: int = 0) -> List[Tuple[int, int, object]]:
        """Split image into fragments based on detected horizontal lines.

        Groups every 5 consecutive lines into one staff section.

        Args:
            image: Input image (np.ndarray, BGR).
            threshold: Extra margin in pixels to add around each section.

        Returns:
            list[tuple[int, int, np.ndarray]]: (y_start, y_end, image_fragment) per section.
        """
        merged_lines = self.detect_merged_lines(image)
        if not merged_lines:
            return []

        height, width = image.shape[:2]

        normalized = []
        for line in merged_lines:
            x1, y1, x2, y2 = line[0]
            x_start, x_end = sorted((x1, x2))
            y = int(round((y1 + y2) / 2))
            normalized.append((x_start, x_end, y))
        normalized.sort(key=lambda item: item[2])

        sections = []
        for i in range(0, len(normalized) - 4, 5):
            x_start, x_end, y_start = normalized[i]
            if i + 4 >= len(normalized):
                break
            _, _, y_end = normalized[i + 4]
            sections.append((y_start, y_end, x_start, x_end))

        result: List[Tuple[int, int, object]] = []
        for y1, y2, x1, x2 in sections:
            top = max(0, y1 - threshold)
            bottom = min(height, y2 + threshold)
            left = max(0, x1 - threshold)
            right = min(width, x2 + threshold)
            result.append((y1, y2, image[top:bottom, left:right]))

        return result

    def preview(self, image_path: Path, output_path: Optional[Path] = None) -> None:
        """Draw detected lines on an image and save the result.

        Args:
            image_path: Path to the input image.
            output_path: Save location. Defaults to preview_lines.png next to the input.
        """
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Cannot read image: {image_path}")
            return

        image_with_lines, merged = self.draw_lines(image)
        out = output_path or image_path.parent / "preview_lines.png"
        cv2.imwrite(str(out), image_with_lines)
        print(f"ParamSet: {self.param_set}")
        print(f"Detected merged lines: {len(merged)}")
        print(f"Saved preview to: {out}")



    @staticmethod
    def normalize_horizontal_lines(lines, threshold: int = 5) -> List:
        """Merge nearby horizontal lines and normalize all to a global x-range.

        Args:
            lines: OpenCV HoughLinesP output shape (N, 1, 4), or None.
            threshold: Max vertical distance (px) between lines to merge.

        Returns:
            list of np.array([[x1, y1, x2, y2]]). Empty list if no lines detected.
        """
        if lines is None or lines.size == 0:
            return []

        normalized = []
        for line_coords in lines:
            x1, y1, x2, y2 = line_coords[0]
            if x1 > x2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            normalized.append((x1, y1, x2, y2))
        normalized.sort(key=lambda ln: (ln[1] + ln[3]) / 2)

        global_x1 = min(ln[0] for ln in normalized)
        global_x2 = max(ln[2] for ln in normalized)

        merged = []
        used = [False] * len(normalized)
        for i, curr in enumerate(normalized):
            if used[i]:
                continue
            avg_y_curr = (curr[1] + curr[3]) / 2
            for j, cmp in enumerate(normalized):
                if i == j or used[j]:
                    continue
                if abs(avg_y_curr - (cmp[1] + cmp[3]) / 2) < threshold:
                    used[j] = True
            merged_y = int(round((curr[1] + curr[3]) / 2))
            merged.append((global_x1, merged_y, global_x2, merged_y))
            used[i] = True

        return [np.array([line]) for line in merged]


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
    def find_params(
        cls,
        image,
        target: Optional[int] = None,
        params: Optional[List[ParamSet]] = None,
    ) -> List[ParamSet]:
        """Return ParamSets whose detected line count matches target.

        Args:
            image: Input image (BGR np.ndarray).
            target: Expected number of lines. If None, returns all tested params.
            params: Candidate param sets. Defaults to the full search space.

        Returns:
            list[ParamSet]: Matching parameter sets.
        """
        param_combos = cls.create_param_set() if params is None else params
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        matching = []
        for param_set in param_combos:
            edges = cv2.Canny(gray, param_set.canny_low, param_set.canny_high, apertureSize=3)
            raw_lines = cv2.HoughLinesP(
                edges,
                rho=1,
                theta=np.pi / 180,
                threshold=param_set.threshold,
                minLineLength=param_set.min_len_ratio * image.shape[0],
                maxLineGap=param_set.max_gap,
            )
            count = len(cls.normalize_horizontal_lines(raw_lines))
            if target is None or count == target:
                matching.append(param_set)
        return matching



     # Settings I/O

    @staticmethod
    def load_settings(settings_path: Path) -> List[ParamSet]:
        """Load BestHorizontalParameters from settings.json as ParamSet objects."""
        payload = json.loads(settings_path.read_text(encoding="utf-8"))
        return [ParamSet(**item) for item in payload.get("BestHorizontalParameters", [])]

    @classmethod
    def from_settings(cls, settings_path: Path) -> Optional["ParamAnalyzer"]:
        """Load first ParamSet from settings and return a configured ParamAnalyzer, or None."""
        params = cls.load_settings(settings_path)
        return cls(params[0]) if params else None

    @staticmethod
    def save_settings(best_parameters: Optional[List[ParamSet]], settings_path: Path) -> None:
        """Save parameters to settings.json under BestHorizontalParameters."""
        if settings_path.exists():
            try:
                settings = json.loads(settings_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                settings = {}
        else:
            settings = {}

        settings["BestHorizontalParameters"] = (
            [] if best_parameters is None else [asdict(p) for p in best_parameters]
        )
        settings.setdefault("BestVerticalParameters", [])
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        print(f"Saved BestHorizontalParameters to: {settings_path}")


    # Pipeline
    @classmethod
    def run_pipeline(
        cls,
        dataset_path: Path,
        data_dir: Path,
        save_to_settings: bool = False,
        settings_path: Optional[Path] = None,
    ) -> Optional[List[ParamSet]]:
        """Iteratively narrow parameter sets across pages and return best params.

        Args:
            dataset_path: Path to dataset.json.
            data_dir: Base directory for resolving relative image paths.
            save_to_settings: If True, persist results to settings.json.
            settings_path: Where to write settings. Defaults to settings.json
                           in the same directory as dataset_path.
        """
        from scr.io.dataset_store import DatasetJsonStore

        dataset = DatasetJsonStore.load(dataset_path)
        best_parameters: Optional[List[ParamSet]] = None

        for page in dataset.pages:
            image_path = Path(page.image_path)
            if not image_path.is_absolute():
                image_path = data_dir / image_path

            # Skip pages known to be too noisy for reliable detection.
            if page.image_path in ("3.png", "4.png"):
                print(f"Skipping {page.image_path} (too noisy)")
                continue

            image = cv2.imread(str(image_path))
            if image is None:
                print(f"Skipping page, cannot read image: {image_path}")
                continue

            best_parameters = cls.find_params(
                image=image,
                target=page.staff_line_count,
                params=best_parameters,
            )
            print(f"{page.image_path}: {len(best_parameters)} matching param sets")
            if not best_parameters:
                print("No matching parameters left. Stopping early.")
                break

        total = 0 if best_parameters is None else len(best_parameters)
        print(f"Final best_parameters count: {total}")

        if save_to_settings:
            resolved = settings_path or dataset_path.parent / "settings.json"
            cls.save_settings(best_parameters, resolved)

        return best_parameters
