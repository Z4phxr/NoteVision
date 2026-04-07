from pathlib import Path

import cv2

from scr.DataInput.config import DATA_DIR
from scr.ParametersSearch.draw_lines import draw_lines
from scr.ParametersSearch.settings_io import get_first_param_set


def run_preview(image_name: str = "4.png") -> None:
    """Run quick preview: load first ParamSet from settings and draw lines on one image."""
    settings_path = Path(__file__).resolve().parent / "settings.json"
    first_param = get_first_param_set(settings_path)

    if first_param is None:
        print("No parameters found in settings.json")
        return

    image_path = DATA_DIR / image_name
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Cannot read image: {image_path}")
        return

    image_with_lines, merged = draw_lines(image, first_param)
    output_path = Path(__file__).resolve().parent / "preview_lines.png"
    cv2.imwrite(str(output_path), image_with_lines)

    print(f"Loaded first ParamSet: {first_param}")
    print(f"Detected merged lines: {len(merged)}")
    print(f"Saved preview image to: {output_path}")


if __name__ == "__main__":
    run_preview()
