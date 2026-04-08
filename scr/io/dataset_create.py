from pathlib import Path
from typing import Optional

from scr.config.paths import DATASET_PATH, DATA_DIR, IMAGE_EXTENSIONS
from scr.io.input_manager import InputManager


def sync_dataset(
    data_dir: Optional[Path] = None,
    dataset_path: Optional[Path] = None,
) -> None:
    resolved_data_dir = data_dir or DATA_DIR
    resolved_dataset_path = dataset_path or DATASET_PATH
    InputManager().run_sync(resolved_data_dir, resolved_dataset_path, IMAGE_EXTENSIONS)


if __name__ == "__main__":
    sync_dataset()

