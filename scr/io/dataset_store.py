import json
from pathlib import Path
from typing import FrozenSet, Optional

from scr.models.page import PageDataset, PageRecord

_DEFAULT_EXTENSIONS: FrozenSet[str] = frozenset({".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"})


class DatasetJsonStore:
    """Read/write `PageDataset` objects from/to a JSON file."""

    @staticmethod
    def load(path: Path | str) -> PageDataset:
        """Load dataset from JSON. Returns empty dataset if file does not exist."""
        path = Path(path)
        if not path.exists():
            return PageDataset()

        payload = json.loads(path.read_text(encoding="utf-8"))
        return PageDataset.from_dict(payload)

    @staticmethod
    def save(dataset: PageDataset, path: Path | str) -> None:
        """Save dataset to JSON."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset.to_dict(), indent=2), encoding="utf-8")

    @staticmethod
    def sync(
        data_dir: Path,
        dataset_path: Path,
        extensions: Optional[FrozenSet[str]] = None,
    ) -> PageDataset:
        """Sync dataset with images in data_dir, prompting for new page metadata.

        Loads the existing dataset, finds images not yet registered, prompts the
        user for their metadata, then saves the updated dataset.

        Args:
            data_dir: Directory to scan for image files.
            dataset_path: Path to the dataset JSON file.
            extensions: Image file extensions to scan. Defaults to common formats.
        """
        exts = extensions or _DEFAULT_EXTENSIONS
        dataset = DatasetJsonStore.load(dataset_path)
        new_paths = dataset.find_new_paths(data_dir, exts)

        if not new_paths:
            print("No new pages found. Dataset is up to date.")
            return dataset

        print(f"Found {len(new_paths)} new page(s).")
        for relative_path in new_paths:
            page = PageRecord.from_prompt(relative_path)
            dataset.add_page(page)

        DatasetJsonStore.save(dataset, dataset_path)
        print(f"Saved dataset to: {dataset_path}")
        print(f"Total pages in dataset: {len(dataset.pages)}")
        return dataset
