from pathlib import Path
from typing import List, Set

from scr.DataInput.models import PageDataset


def list_image_paths(data_dir: Path, extensions: Set[str]) -> List[Path]:
    """Collect image files from data directory recursively."""
    if not data_dir.exists():
        return []

    image_paths: List[Path] = []
    for path in data_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in extensions:
            image_paths.append(path)

    image_paths.sort()
    return image_paths


def find_new_page_paths(
    dataset: PageDataset,
    data_dir: Path,
    extensions: Set[str],
) -> List[str]:
    """Return relative image paths not yet present in dataset."""
    known = dataset.known_paths()
    candidates = list_image_paths(data_dir, extensions)

    new_paths: List[str] = []
    for image_path in candidates:
        relative = image_path.relative_to(data_dir).as_posix()
        if relative not in known:
            new_paths.append(relative)

    return new_paths


