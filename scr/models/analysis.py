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

    def __str__(self):
        return (f"ParamSet(threshold={self.threshold}, min_len_ratio={self.min_len_ratio}, "
                f"max_gap={self.max_gap}, canny_low={self.canny_low}, canny_high={self.canny_high})")


@dataclass(frozen=True)
class PhotoResult:
    """Analysis result for one photo under a ParamSet."""

    path: str
    found_lines: Optional[int]
    target_lines: int


    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "found_lines": self.found_lines,
            "target_lines": self.target_lines,
            "matched": self.matched,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PhotoResult":
        return cls(
            path=str(data["path"]),
            found_lines=data.get("found_lines"),
            target_lines=int(data["target_lines"]),
        )

    @property
    def matched(self) -> bool:
        return self.found_lines == self.target_lines


@dataclass(frozen=True)
class ParamSetResult:
    """Analysis results for one ParamSet across all photos."""

    param_set: ParamSet
    photos: List[PhotoResult]
    score: float

    def __str__(self):
        print(f"for {self.param_set} score is {self.score}")

    def to_dict(self) -> dict:
        return {
            "param_set": asdict(self.param_set),
            "summary": {
                "matched": self.matched,
                "evaluated": len(self.photos),
                "score": self.score,
            },
            "photos": [photo.to_dict() for photo in self.photos],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ParamSetResult":
        param_set = ParamSet(**data["param_set"])
        photos = [PhotoResult.from_dict(item) for item in data.get("photos", [])]
        summary = data.get("summary", {})
        score = summary.get("score")
        if score is None:
            score = cls._compute_score(photos)
        return cls(
            param_set=param_set,
            photos=photos,
            score=float(score),
        )

    @property
    def matched(self) -> int:
        return sum(1 for photo in self.photos if photo.matched)

    @staticmethod
    def _compute_score(photos: List[PhotoResult]) -> float:
        if not photos:
            return 0.0
        matched = sum(1 for photo in photos if photo.matched)
        return matched / len(photos)
