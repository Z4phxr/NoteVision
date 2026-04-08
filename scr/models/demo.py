from scr.models.page import ChunkSlice, PageDataset, PageRecord, StaffSlice


def run_demo() -> None:
    dataset = PageDataset()
    page = PageRecord(image_path="data/page_1.png", staff_count=2, bar_line_count=8)
    dataset.add_page(page)

    staff = StaffSlice(
        staff_index=0,
        parent_page_path=page.image_path,
        x_start=10,
        x_end=400,
        y_start=100,
        y_end=180,
        image_path="data/processed/page_1/staff_0.png",
    )
    page.add_staff_slice(staff)

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
    staff.add_chunk(chunk)

    payload = dataset.to_dict()
    restored = dataset.from_dict(payload)

    assert restored.pages[0].image_path == page.image_path
    assert restored.pages[0].staff_slices[0].chunks[0].image_path == chunk.image_path


if __name__ == "__main__":
    run_demo()

