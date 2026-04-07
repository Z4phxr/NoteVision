import json
from dataclasses import asdict
from pathlib import Path

import cv2

from scr.DataInput.config import DATA_DIR, DATASET_PATH
from scr.DataInput.models import PageDataset
from scr.DataInput.storage import DatasetJsonStore
from scr.ParametersSearch.horizonstal_param_search import find_horizontal_line_params


def save_horizontal_params_to_settings(best_parameters, settings_path: Path | None = None) -> None:
    """Save final horizontal params into settings.json under BestHorizontalParameters."""
    settings_path = settings_path or (Path(__file__).resolve().parent / "settings.json")

    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            settings = {}
    else:
        settings = {}

    if best_parameters is None:
        serialized = []
    else:
        serialized = [asdict(param) for param in best_parameters]

    settings["BestHorizontalParameters"] = serialized
    settings.setdefault("BestVerticalParameters", [])

    settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    print(f"Saved BestHorizontalParameters to: {settings_path}")


def horizontal_param_pipeline(save_to_settings: bool = False):
    """Iteratively narrow parameter sets across pages and return final best parameters."""
    dataset: PageDataset = DatasetJsonStore.load(DATASET_PATH)
    best_parameters = None

    for page in dataset.pages:
        image_path = Path(page.image_path)
        if not image_path.is_absolute():
            image_path = DATA_DIR / image_path

        # skip 3 for now since they are very noisy and cause all params to be filtered out
        if page.image_path == "3.png" or page.image_path == "4.png":
            print(f"Skipping page 3.png due to noise")
            continue

        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Skipping page, cannot read image: {image_path}")
            continue

        best_parameters = find_horizontal_line_params(
            image=image,
            target=page.staff_line_count,
            params=best_parameters,
        )

        print(f"{page.image_path}: {len(best_parameters)} matching param sets")
        if not best_parameters:
            print("No matching parameters left. Stopping early.")
            break

    print(f"Final best_parameters count: {0 if best_parameters is None else len(best_parameters)}")

    if save_to_settings:
        save_horizontal_params_to_settings(best_parameters)

    return best_parameters


if __name__ == "__main__":
    best_parameters = horizontal_param_pipeline(save_to_settings=True)
