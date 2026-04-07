from scr.DataInput.models import PageRecord


def prompt_int(message: str) -> int:
    """Prompt until user enters a non-negative integer."""
    while True:
        raw = input(message).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a valid integer.")
            continue

        if value < 0:
            print("Please enter a non-negative integer.")
            continue

        return value

    raise RuntimeError("Unreachable")


def prompt_page_record(relative_image_path: str) -> PageRecord:
    """Collect metadata for one page and return a PageRecord."""
    print(f"\nNew page found: {relative_image_path}")
    staff_count = prompt_int("  Staff count: ")
    bar_line_count = prompt_int("  Bar line count: ")
    return PageRecord(
        image_path=relative_image_path,
        staff_count=staff_count,
        bar_line_count=bar_line_count,
    )


