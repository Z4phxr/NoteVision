from pathlib import Path
from typing import Optional, Set

from scr.io.dataset_store import DatasetJsonStore
from scr.models.page import PageDataset, PageRecord

_DEFAULT_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


class InputManager:
    """Manager responsible for collecting dataset input."""

    def __init__(self, dataset: Optional[PageDataset] = None) -> None:
        self.dataset = dataset or PageDataset()

    @staticmethod
    def _prompt_int(message: str) -> int:
        """Prompt until the user enters a non-negative integer."""
        while True:
            raw = input(message)
            if raw is None:
                print("Please enter a valid integer.")
                continue
            raw = raw.strip()
            try:
                value = int(raw)
            except ValueError:
                print("Please enter a valid integer.")
                continue
            if value < 0:
                print("Please enter a non-negative integer.")
                continue
            return value

    def prompt_page_record(self, relative_image_path: str) -> PageRecord:
        """Collect metadata for a new page and return a PageRecord."""
        print(f"\nNew page found: {relative_image_path}")
        staff_count = self._prompt_int("  Staff count: ")
        bar_line_count = self._prompt_int("  Bar line count: ")
        return PageRecord(
            image_path=relative_image_path,
            staff_count=staff_count,
            bar_line_count=bar_line_count,
        )

    def run_sync(
        self,
        data_dir: Path,
        dataset_path: Path,
        extensions: Optional[Set[str]] = None,
    ) -> PageDataset:
        """Scan data_dir, prompt for new pages, and persist the dataset."""
        exts = extensions or _DEFAULT_EXTENSIONS
        self.dataset = DatasetJsonStore.load(dataset_path)
        self.dataset.data_dir = data_dir
        new_paths = self.dataset.find_new_paths(exts)

        if not new_paths:
            print("No new pages found. Dataset is up to date.")
            return self.dataset

        print(f"Found {len(new_paths)} new page(s).")
        for relative_path in new_paths:
            page = self.prompt_page_record(relative_path)
            self.dataset.add_page(page)

        DatasetJsonStore.save(self.dataset, dataset_path)
        print(f"Saved dataset to: {dataset_path}")
        print(f"Total pages in dataset: {len(self.dataset.pages)}")
        return self.dataset

