from scr.models.dataset_manager import DatasetManager
from scr.models.page import ChunkSlice, PageRecord, StaffSlice


def run_demo() -> None:
    manager = DatasetManager()
    page = PageRecord(image_path="data/page_1.png", staff_count=2, bar_line_count=8)
    manager.add_page(page)

    staff = StaffSlice(
        staff_index=0,
        parent_page_path=page.image_path,
        x_start=10,
        x_end=400,
        y_start=100,
        y_end=180,
        image_path="data/processed/page_1/staff_0.png",
    )
    manager.add_staff_slice(page.image_path, staff)

    chunk = ChunkSlice(
        chunk_index=0,
        parent_page_path=page.image_path,
        parent_staff_index=0,
        x_start=10,
        x_end=120,
        y_start=100,
        y_end=180,
        image_path="data/processed/page_1/staff_0/chunk_0.png",
    )
    manager.add_chunk_slice(page.image_path, 0, chunk)

    payload = manager.dataset.to_dict()
    restored = manager.dataset.from_dict(payload)

    assert restored.pages[0].image_path == page.image_path
    assert restored.pages[0].staff_slices[0].chunks[0].image_path == chunk.image_path


if __name__ == "__main__":
    run_demo()

