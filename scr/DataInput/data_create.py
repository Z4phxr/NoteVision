from pathlib import Path
from typing import Optional

from scr.DataInput.config import DATA_DIR, DATASET_PATH, IMAGE_EXTENSIONS
from scr.DataInput.discovery import find_new_page_paths
from scr.DataInput.models import PageDataset
from scr.DataInput.prompt import prompt_page_record
from scr.DataInput.storage import DatasetJsonStore


def sync_dataset(data_dir: Optional[Path] = None, dataset_path: Optional[Path] = None) -> PageDataset:
    """Sync dataset with images in data folder and prompt for metadata of new pages."""
    data_dir = data_dir or DATA_DIR
    dataset_path = dataset_path or DATASET_PATH

    dataset = DatasetJsonStore.load(dataset_path)
    new_paths = find_new_page_paths(dataset, data_dir, IMAGE_EXTENSIONS)

    if not new_paths:
        print("No new pages found. Dataset is up to date.")
        return dataset

    print(f"Found {len(new_paths)} new page(s).")
    for relative_path in new_paths:
        page = prompt_page_record(relative_path)
        dataset.add_page(page)

    DatasetJsonStore.save(dataset, dataset_path)
    print(f"Saved dataset to: {dataset_path}")
    print(f"Total pages in dataset: {len(dataset.pages)}")
    return dataset


if __name__ == "__main__":
    sync_dataset()


