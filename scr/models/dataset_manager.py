from typing import Optional

from scr.models.page import ChunkSlice, PageDataset, PageRecord, StaffSlice


class DatasetManager:
    """Simple manager for PageDataset with helpers to attach slices."""

    def __init__(self, dataset: Optional[PageDataset] = None) -> None:
        self.dataset = dataset or PageDataset()

    def add_page(self, page: PageRecord) -> None:
        self.dataset.add_page(page)

    def find_page(self, image_path: str) -> Optional[PageRecord]:
        for page in self.dataset.pages:
            if page.image_path == image_path:
                return page
        return None

    def add_staff_slice(self, page_path: str, staff_slice: StaffSlice) -> None:
        page = self.find_page(page_path)
        if page is None:
            raise ValueError(f"Page not found: {page_path}")
        page.add_staff_slice(staff_slice)

    def add_chunk_slice(self, page_path: str, staff_index: int, chunk_slice: ChunkSlice) -> None:
        page = self.find_page(page_path)
        if page is None:
            raise ValueError(f"Page not found: {page_path}")
        for staff in page.staff_slices:
            if staff.staff_index == staff_index:
                staff.add_chunk(chunk_slice)
                return
        raise ValueError(f"Staff slice not found: page={page_path}, staff_index={staff_index}")

