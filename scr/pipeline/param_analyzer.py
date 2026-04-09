import json
from dataclasses import asdict
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


    @classmethod
    def find_best_param_sets(
        cls,
        data_dir: Path,
        max_photos: int = 2,
        save: bool = False,
        dataset_path: Optional[Path] = None,
    ) -> List[ParamSet]:
        """Find ParamSets that match staff line count on up to `max_photos` pages.

        The search is progressive:
        - photo 1 tests all combinations
        - photo 2 tests only winners from photo 1
        - etc.
        """
        from scr.io.dataset_store import DatasetJsonStore

        resolved_data_dir = Path(data_dir)
        resolved_dataset_path = Path(dataset_path) if dataset_path is not None else (resolved_data_dir / "dataset.json")

        dataset = DatasetJsonStore.load(resolved_dataset_path)
        dataset.data_dir = resolved_data_dir

        if max_photos <= 0:
            print("max_photos must be greater than 0. Returning no parameter sets.")
            return []

        if not resolved_dataset_path.exists():
            print(
                f"Dataset file not found: {resolved_dataset_path}. "
                "No photos to evaluate; returning full parameter search space."
            )

        candidates: List[ParamSet] = cls.create_param_set()
        pages_to_check = dataset.pages[:max_photos]
        if not pages_to_check:
            print("Dataset has no pages to evaluate. Returning full parameter search space.")
            return candidates

        for photo_index, page in enumerate(pages_to_check, start=1):
            image_path = Path(page.image_path)
            if not image_path.is_absolute():
                image_path = resolved_data_dir / image_path

            image = cv2.imread(str(image_path))
            if image is None:
                print(
                    f"Photo {photo_index}/{len(pages_to_check)} {page.image_path}: missing image, "
                    f"skipping (current combos: {len(candidates)})"
                )
                continue

            next_candidates: List[ParamSet] = []
            for param_set in candidates:
                merged = page.detect_merged_lines(image, param_set)
                if len(merged) == page.staff_line_count:
                    next_candidates.append(param_set)

            candidates = next_candidates
            print(
                f"After photo {photo_index}/{len(pages_to_check)} ({page.image_path}) -> "
                f"{len(candidates)} param combos"
            )

            if not candidates:
                print("No parameter combinations left. Stopping early.")
                break

        if save:
            from scr.config.paths import SETTINGS_PATH

            settings_path = SETTINGS_PATH
            payload = [asdict(param_set) for param_set in candidates]
            settings_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print(f"Saved {len(candidates)} param combos to: {settings_path}")

        return candidates

    @staticmethod
    def _format_folder_name(rank: int, set_result: ParamSetResult) -> str:
        """Build a filesystem-safe folder name for one ranked ParamSet result."""
        param = set_result.param_set
        ratio = f"{param.min_len_ratio:.2f}".replace(".", "p")
        score = f"{set_result.score:.2f}".replace(".", "p")
        return (
            f"rank_{rank:02d}_score_{score}_"
            f"thr_{param.threshold}_min_{ratio}_gap_{param.max_gap}_"
            f"canny_{param.canny_low}_{param.canny_high}"
        )

    @staticmethod
    def _overlay_text(image, lines: List[str]) -> None:
        """Draw white text with black outline for readability on an image."""
        import cv2

        x = 10
        y = 20
        for line in lines:
            cv2.putText(image, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3)
            cv2.putText(image, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
            y += 20

    @staticmethod
    def load_results(input_path: Path) -> List[ParamSetResult]:
        """Load analysis results JSON produced by `run_full_analysis`."""
        payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
        return [ParamSetResult.from_dict(item) for item in payload.get("results", [])]

    @staticmethod
    def load_settings(settings_path: Path) -> List[ParamSet]:
        """Load plain ParamSet list from `settings.json`."""
        payload = json.loads(Path(settings_path).read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("settings.json must contain a JSON list of ParamSet objects.")
        return [ParamSet(**item) for item in payload]

    @staticmethod
    def visualize(
        input_path: Path,
        output_path: Path,
        dataset_path: Optional[Path] = None,
        data_dir: Optional[Path] = None,
    ) -> None:
        """Render top ParamSet detections for all dataset pages."""
        from scr.config.paths import CLEAN_DIR, DATASET_PATH
        from scr.io.dataset_store import DatasetJsonStore

        resolved_dataset_path = dataset_path or DATASET_PATH
        resolved_data_dir = data_dir or CLEAN_DIR
        dataset = DatasetJsonStore.load(resolved_dataset_path)
        dataset.data_dir = resolved_data_dir

        results: List[ParamSetResult] = ParamAnalyzer.load_results(input_path)
        top_results = sorted(results, key=lambda item: item.score, reverse=True)[:3]
        if not top_results:
            print("No results found.")
            return

        output_path.mkdir(parents=True, exist_ok=True)
        for rank, set_result in enumerate(top_results, start=1):
            param = set_result.param_set
            target_dir = output_path / ParamAnalyzer._format_folder_name(rank, set_result)
            target_dir.mkdir(parents=True, exist_ok=True)

            label_lines = [
                f"rank={rank} score={set_result.score:.2f}",
                f"thr={param.threshold} min_len={param.min_len_ratio:.2f} gap={param.max_gap}",
                f"canny={param.canny_low}/{param.canny_high}",
            ]

            for page in dataset.pages:
                image_path = Path(page.image_path)
                if not image_path.is_absolute():
                    image_path = resolved_data_dir / image_path

                image = cv2.imread(str(image_path))
                if image is None:
                    print(f"Missing image: {page.image_path}")
                    continue

                image_with_lines, _ = page.draw_lines(image, param)
                ParamAnalyzer._overlay_text(image_with_lines, label_lines)

                output_name = f"{Path(page.image_path).stem}_lines.png"
                cv2.imwrite(str(target_dir / output_name), image_with_lines)

    @staticmethod
    def visualize_settings(
        settings_path: Path,
        output_path: Path,
        dataset_path: Optional[Path] = None,
        data_dir: Optional[Path] = None,
        top_k: int = 3,
    ) -> None:
        """Render first `top_k` ParamSets from settings.json on all dataset pages."""
        from scr.config.paths import CLEAN_DIR, DATASET_PATH
        from scr.io.dataset_store import DatasetJsonStore

        resolved_dataset_path = dataset_path or DATASET_PATH
        resolved_data_dir = data_dir or CLEAN_DIR
        dataset = DatasetJsonStore.load(resolved_dataset_path)
        dataset.data_dir = resolved_data_dir

        if top_k <= 0:
            print("top_k must be greater than 0.")
            return

        param_sets = ParamAnalyzer.load_settings(settings_path)
        selected = param_sets[:top_k]
        if not selected:
            print("No parameter sets in settings.json.")
            return

        output_path.mkdir(parents=True, exist_ok=True)
        for rank, param in enumerate(selected, start=1):
            ratio = f"{param.min_len_ratio:.2f}".replace(".", "p")
            target_dir = (
                output_path
                / f"rank_{rank:02d}_thr_{param.threshold}_min_{ratio}_"
                  f"gap_{param.max_gap}_canny_{param.canny_low}_{param.canny_high}"
            )
            target_dir.mkdir(parents=True, exist_ok=True)

            label_lines = [
                f"rank={rank}",
                f"thr={param.threshold} min_len={param.min_len_ratio:.2f} gap={param.max_gap}",
                f"canny={param.canny_low}/{param.canny_high}",
            ]

            for page in dataset.pages:
                image_path = Path(page.image_path)
                if not image_path.is_absolute():
                    image_path = resolved_data_dir / image_path

                image = cv2.imread(str(image_path))
                if image is None:
                    print(f"Missing image: {page.image_path}")
                    continue

                image_with_lines, _ = page.draw_lines(image, param)
                ParamAnalyzer._overlay_text(image_with_lines, label_lines)
                output_name = f"{Path(page.image_path).stem}_lines.png"
                cv2.imwrite(str(target_dir / output_name), image_with_lines)

        print(f"Saved settings-based visualization to: {output_path}")

    @staticmethod
    def visualize_photo_params(
        input_path: Path,
        photo_path: Path | str,
        output_path: Path,
        dataset_path: Optional[Path] = None,
        data_dir: Optional[Path] = None,
    ) -> Path:
        """Render all ranked ParamSets on one photo and save the outputs."""
        from scr.config.paths import CLEAN_DIR, DATASET_PATH
        from scr.io.dataset_store import DatasetJsonStore
        from scr.models.page import PageRecord

        resolved_dataset_path = dataset_path or DATASET_PATH
        resolved_data_dir = data_dir or CLEAN_DIR
        dataset = DatasetJsonStore.load(resolved_dataset_path)
        dataset.data_dir = resolved_data_dir

        resolved_photo = Path(photo_path)
        page = next(
            (
                item
                for item in dataset.pages
                if Path(item.image_path).name == resolved_photo.name
                or item.image_path == str(photo_path)
            ),
            None,
        )
        if page is None:
            page = PageRecord(
                image_path=str(photo_path),
                staff_count=0,
                bar_line_count=0,
            )

        image_path = resolved_photo
        if not image_path.is_absolute():
            if image_path.exists():
                image_path = image_path.resolve()
            else:
                image_path = resolved_data_dir / image_path

        image = cv2.imread(str(image_path))
        if image is None:
            raise FileNotFoundError(f"Missing image: {image_path}")

        results: List[ParamSetResult] = ParamAnalyzer.load_results(input_path)
        sorted_results = sorted(results, key=lambda item: item.score, reverse=True)

        target_dir = output_path / Path(page.image_path).stem
        target_dir.mkdir(parents=True, exist_ok=True)

        for rank, set_result in enumerate(sorted_results, start=1):
            param = set_result.param_set
            image_with_lines, _ = page.draw_lines(image, param)
            output_name = (
                f"{rank:03d}_score_{set_result.score:.2f}_"
                f"thr_{param.threshold}_min_{param.min_len_ratio:.2f}_"
                f"gap_{param.max_gap}_canny_{param.canny_low}_{param.canny_high}.png"
            )
            cv2.imwrite(str(target_dir / output_name), image_with_lines)

        return target_dir

