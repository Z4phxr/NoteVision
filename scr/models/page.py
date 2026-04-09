from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, SupportsInt, cast

import numpy as np

from scr.config.paths import CLEAN_DIR


@dataclass
class ChunkSlice:
    """Vertical chunk cut from a staff slice."""

    chunk_index: int
    parent_page_path: str
    parent_staff_index: int
    x_start: int
    x_end: int
    y_start: int
    y_end: int
    image_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_index": self.chunk_index,
            "parent_page_path": self.parent_page_path,
            "parent_staff_index": self.parent_staff_index,
            "x_start": self.x_start,
            "x_end": self.x_end,
            "y_start": self.y_start,
            "y_end": self.y_end,
            "image_path": self.image_path,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChunkSlice":
        return cls(
            chunk_index=int(cast(SupportsInt, data["chunk_index"])),
            parent_page_path=str(data["parent_page_path"]),
            parent_staff_index=int(cast(SupportsInt, data["parent_staff_index"])),
            x_start=int(cast(SupportsInt, data["x_start"])),
            x_end=int(cast(SupportsInt, data["x_end"])),
            y_start=int(cast(SupportsInt, data["y_start"])),
            y_end=int(cast(SupportsInt, data["y_end"])),
            image_path=data.get("image_path"),
        )


@dataclass
class StaffSlice:
    """One staff (5-line) slice extracted from a page."""

    staff_index: int
    parent_page_path: str
    x_start: int
    x_end: int
    y_start: int
    y_end: int
    image_path: Optional[str] = None
    chunks: List[ChunkSlice] = field(default_factory=list)

    def add_chunk(self, chunk: ChunkSlice) -> None:
        self.chunks.append(chunk)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "staff_index": self.staff_index,
            "parent_page_path": self.parent_page_path,
            "x_start": self.x_start,
            "x_end": self.x_end,
            "y_start": self.y_start,
            "y_end": self.y_end,
            "image_path": self.image_path,
            "chunks": [chunk.to_dict() for chunk in self.chunks],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StaffSlice":
        chunks_data = data.get("chunks", [])
        return cls(
            staff_index=int(cast(SupportsInt, data["staff_index"])),
            parent_page_path=str(data["parent_page_path"]),
            x_start=int(cast(SupportsInt, data["x_start"])),
            x_end=int(cast(SupportsInt, data["x_end"])),
            y_start=int(cast(SupportsInt, data["y_start"])),
            y_end=int(cast(SupportsInt, data["y_end"])),
            image_path=data.get("image_path"),
            chunks=[ChunkSlice.from_dict(item) for item in chunks_data],
        )


@dataclass
class PageRecord:
    """Metadata for one music page used by detection pipelines.

    `staff_count` means the number of staff groups, not the number of staff lines.
    The actual number of staff lines is `staff_count * 5`.
    `bar_line_count` is the accurate number of detected bar lines.
    `possible_vertical_lines` is the relaxed detection target:
    `bar_line_count + (2 * staff_count)`.
    """

    image_path: str
    staff_count: int
    bar_line_count: int
    staff_slices: List[StaffSlice] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.image_path = str(self.image_path)
        self.staff_count = int(self.staff_count)
        self.bar_line_count = int(self.bar_line_count)
        if self.staff_count < 0 or self.bar_line_count < 0:
            raise ValueError("staff_count and bar_line_count must be non-negative.")

    @property
    def staff_line_count(self) -> int:
        return self.staff_count * 5

    @property
    def possible_vertical_lines(self) -> int:
        return self.bar_line_count + (self.staff_count * 2)

    def add_staff_slice(self, staff_slice: StaffSlice) -> None:
        self.staff_slices.append(staff_slice)

    COLORS = [
        (255, 0, 0),
        (255, 165, 0),
        (255, 255, 0),
        (0, 255, 0),
        (0, 0, 255),
    ]

    def detect_merged_lines(self, image, params_set) -> List:
        """Detect merged horizontal lines using ParamSet values."""
        import math

        import cv2

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, params_set.canny_low, params_set.canny_high, apertureSize=3)
        raw_lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=math.pi / 180,
            threshold=params_set.threshold,
            minLineLength=params_set.min_len_ratio * image.shape[0],
            maxLineGap=params_set.max_gap,
        )

        return self.normalize_horizontal_lines(raw_lines)

    def draw_lines(self, image, params_set):
        """Detect and draw merged horizontal lines on a copy of the image."""
        import cv2

        merged = self.detect_merged_lines(image, params_set)
        image_with_lines = image.copy()
        for i, line in enumerate(merged):
            x1, y1, x2, y2 = line[0]
            color = self.COLORS[i % len(self.COLORS)]
            cv2.line(image_with_lines, (x1, y1), (x2, y2), color, 1)
        return image_with_lines, merged

    @staticmethod
    def normalize_horizontal_lines(lines, threshold: int = 5) -> List:
        """Merge nearby horizontal lines and normalize all to a global x-range."""
        if lines is None or lines.size == 0:
            return []

        normalized = []
        for line_coords in lines:
            x1, y1, x2, y2 = line_coords[0]
            if x1 > x2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            normalized.append((x1, y1, x2, y2))
        normalized.sort(key=lambda ln: (ln[1] + ln[3]) / 2)

        global_x1 = min(ln[0] for ln in normalized)
        global_x2 = max(ln[2] for ln in normalized)

        merged = []
        used = [False] * len(normalized)
        for i, curr in enumerate(normalized):
            if used[i]:
                continue
            avg_y_curr = (curr[1] + curr[3]) / 2
            for j, cmp in enumerate(normalized):
                if i == j or used[j]:
                    continue
                if abs(avg_y_curr - (cmp[1] + cmp[3]) / 2) < threshold:
                    used[j] = True
            merged_y = int(round((curr[1] + curr[3]) / 2))
            merged.append((global_x1, merged_y, global_x2, merged_y))
            used[i] = True

        return [np.array([line]) for line in merged]

    def split_staff_slices(
        self,
        image,
        merged_lines: List,
        threshold: int = 0,
        attach: bool = True,
    ) -> List[tuple[StaffSlice, object]]:
        """Split image into staff slices and optionally attach to this page.

        Returns:
            list[tuple[StaffSlice, np.ndarray]]: StaffSlice with its image fragment.
        """
        if not merged_lines:
            return []

        height, width = image.shape[:2]

        normalized: List[tuple[int, int, int]] = []
        for line in merged_lines:
            x1, y1, x2, y2 = line[0]
            x_start, x_end = sorted((x1, x2))
            y = int(round((y1 + y2) / 2))
            normalized.append((x_start, x_end, y))

        normalized.sort(key=lambda item: item[2])

        sections: List[tuple[int, int, int, int]] = []
        for i in range(0, len(normalized) - 4, 5):
            x_start, x_end, y_start = normalized[i]
            if i + 4 >= len(normalized):
                break
            _, _, y_end = normalized[i + 4]
            sections.append((y_start, y_end, x_start, x_end))

        results: List[tuple[StaffSlice, object]] = []
        for staff_index, (y1, y2, x1, x2) in enumerate(sections):
            top = max(0, y1 - threshold)
            bottom = min(height, y2 + threshold)
            left = max(0, x1 - threshold)
            right = min(width, x2 + threshold)

            staff_slice = StaffSlice(
                staff_index=staff_index,
                parent_page_path=self.image_path,
                x_start=left,
                x_end=right,
                y_start=top,
                y_end=bottom,
            )
            if attach:
                self.add_staff_slice(staff_slice)

            cut_image = image[top:bottom, left:right]
            results.append((staff_slice, cut_image))

        return results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_path": self.image_path,
            "staff_count": self.staff_count,
            "bar_line_count": self.bar_line_count,
            "staff_line_count": self.staff_line_count,
            "possible_vertical_lines": self.possible_vertical_lines,
            "staff_slices": [staff.to_dict() for staff in self.staff_slices],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PageRecord":
        image_path = str(data["image_path"])
        raw_staff_count: Optional[Any] = data.get("staff_count", data.get("stave_count", data.get("stave")))
        raw_bar_line_count: Optional[Any] = data.get("bar_line_count", data.get("bar_lines"))

        if raw_staff_count is None or raw_bar_line_count is None:
            raise ValueError("Missing required metadata fields for page record.")

        staff_count = int(cast(SupportsInt, raw_staff_count))
        bar_line_count = int(cast(SupportsInt, raw_bar_line_count))

        staff_data = data.get("staff_slices", [])
        staff_slices = [StaffSlice.from_dict(item) for item in staff_data]

        return cls(
            image_path=image_path,
            staff_count=staff_count,
            bar_line_count=bar_line_count,
            staff_slices=staff_slices,
        )


@dataclass
class PageDataset:
    """Container for all page records."""

    pages: List[PageRecord] = field(default_factory=list)
    schema_version: int = 1
    data_dir: Path = field(default_factory=lambda: CLEAN_DIR)

    def add_page(self, page: PageRecord) -> None:
        self.pages.append(page)

    def extend(self, pages: Iterable[PageRecord]) -> None:
        self.pages.extend(pages)

    def known_paths(self) -> set[str]:
        return {page.image_path for page in self.pages}

    def find_new_paths(self, extensions: Optional[Set[str]] = None) -> List[str]:
        """Return relative image paths not yet present in this dataset."""
        if not self.data_dir.exists():
            return []
        if extensions is None:
            extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
        known = self.known_paths()
        new_paths: List[str] = []
        for path in sorted(self.data_dir.rglob("*")):
            if path.is_file() and path.suffix.lower() in extensions:
                relative = path.relative_to(self.data_dir).as_posix()
                if relative not in known:
                    new_paths.append(relative)
        return new_paths

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "pages": [page.to_dict() for page in self.pages],
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PageDataset":
        pages_data = payload.get("pages", [])
        pages = [PageRecord.from_dict(item) for item in pages_data]
        return cls(pages=pages, schema_version=int(payload.get("schema_version", 1)))
