from pathlib import Path

from scr.config.paths import CLEAN_DIR, DATASET_PATH, IMAGE_EXTENSIONS
from scr.io.input_manager import InputManager


def run() -> None:
    InputManager().run_sync(
        data_dir=Path(CLEAN_DIR),
        dataset_path=Path(DATASET_PATH),
        extensions=IMAGE_EXTENSIONS,
    )


if __name__ == "__main__":
    run()

