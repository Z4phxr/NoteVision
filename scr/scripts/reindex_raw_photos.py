from pathlib import Path
from shutil import move

from scr.config.paths import CLEAN_DIR, IMAGE_EXTENSIONS, RAW_DIR


def _used_photo_numbers(directory: Path) -> set[int]:
    used: set[int] = set()
    for path in directory.iterdir():
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        try:
            used.add(int(path.stem))
        except ValueError:
            continue
    return used


def run(start_number: int = 10) -> None:
    """
    Move all images from data/raw into data/clean and rename them sequentially.

    Example output names: 10.png, 11.jpg, 12.png...
    """
    raw_dir = RAW_DIR
    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw directory does not exist: {raw_dir}")
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    photo_files = sorted(
        p for p in raw_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )

    if not photo_files:
        print(f"No photos found in {raw_dir}")
        return

    minimum_start = 10
    used_numbers = _used_photo_numbers(CLEAN_DIR)
    if used_numbers:
        next_number = max(start_number, minimum_start, max(used_numbers) + 1)
    else:
        next_number = max(start_number, minimum_start)

    moved_count = 0

    for src_path in photo_files:
        while next_number in used_numbers:
            next_number += 1

        target_name = f"{next_number}{src_path.suffix.lower()}"
        dst_path = CLEAN_DIR / target_name

        move(str(src_path), str(dst_path))
        used_numbers.add(next_number)
        next_number += 1
        moved_count += 1

    print(f"Moved {moved_count} photos from {raw_dir} to {CLEAN_DIR}")


if __name__ == "__main__":
    run()
