from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, SupportsInt, cast


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

    def __post_init__(self) -> None:
        """Validate basic field types and values."""
        self.image_path = str(self.image_path)
        self.staff_count = int(self.staff_count)
        self.bar_line_count = int(self.bar_line_count)
        if self.staff_count < 0 or self.bar_line_count < 0:
            raise ValueError("staff_count and bar_line_count must be non-negative.")

    @property
    def staff_line_count(self) -> int:
        """Number of staff lines (5 lines per staff)."""
        return self.staff_count * 5

    @property
    def possible_vertical_lines(self) -> int:
        """Possible vertical-line target allowing staff-edge false positives."""
        return self.bar_line_count + (self.staff_count * 2)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize record to a JSON-friendly dictionary."""
        return {
            "image_path": self.image_path,
            "staff_count": self.staff_count,
            "bar_line_count": self.bar_line_count,
            "staff_line_count": self.staff_line_count,
            "possible_vertical_lines": self.possible_vertical_lines,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PageRecord":
        """Build a record from dict, supporting legacy key names."""
        image_path = str(data["image_path"])
        raw_staff_count: Optional[Any] = data.get("staff_count", data.get("stave_count", data.get("stave")))
        raw_bar_line_count: Optional[Any] = data.get("bar_line_count", data.get("bar_lines"))

        if raw_staff_count is None or raw_bar_line_count is None:
            raise ValueError("Missing required metadata fields for page record.")

        staff_count = int(cast(SupportsInt, raw_staff_count))
        bar_line_count = int(cast(SupportsInt, raw_bar_line_count))

        return cls(
            image_path=image_path,
            staff_count=staff_count,
            bar_line_count=bar_line_count,
        )


@dataclass
class PageDataset:
    """Container for all page records."""

    pages: List[PageRecord] = field(default_factory=list)
    schema_version: int = 1

    def add_page(self, page: PageRecord) -> None:
        """Add one page record."""
        self.pages.append(page)

    def extend(self, pages: Iterable[PageRecord]) -> None:
        """Add multiple page records."""
        self.pages.extend(pages)

    def known_paths(self) -> set[str]:
        """Return normalized image paths already present in dataset."""
        return {page.image_path for page in self.pages}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize dataset to dictionary."""
        return {
            "schema_version": self.schema_version,
            "pages": [page.to_dict() for page in self.pages],
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PageDataset":
        """Deserialize dataset from dictionary payload."""
        pages_data = payload.get("pages", [])
        pages = [PageRecord.from_dict(item) for item in pages_data]
        return cls(pages=pages, schema_version=int(payload.get("schema_version", 1)))


