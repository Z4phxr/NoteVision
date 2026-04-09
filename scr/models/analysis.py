from dataclasses import asdict, dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ParamSet:
    """Single Hough/Canny parameter combination."""

    threshold: int
    min_len_ratio: float
    max_gap: int
    canny_low: int
    canny_high: int


@dataclass(frozen=True)
class PhotoResult:
    """Analysis result for one photo under a ParamSet."""

    path: str
    found_lines: Optional[int]
    target_lines: int
    matched: bool

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "found_lines": self.found_lines,
            "target_lines": self.target_lines,
            "matched": self.matched,
        }


@dataclass(frozen=True)
class ParamSetResult:
    """Analysis results for one ParamSet across all photos."""

    param_set: ParamSet
    photos: List[PhotoResult]

    def to_dict(self) -> dict:
        return {
            "param_set": asdict(self.param_set),
            "photos": [photo.to_dict() for photo in self.photos],
            "summary": {
                "matched": sum(1 for photo in self.photos if photo.matched),
                "evaluated": len(self.photos),
            },
        }

