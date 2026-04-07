import json
from pathlib import Path

from scr.DataInput.models import PageDataset


class DatasetJsonStore:
    """Read/write `PageDataset` objects from/to a JSON file.
    """

    @staticmethod
    def load(path: Path | str) -> PageDataset:
        """Load dataset from JSON. Returns empty dataset if file does not exist."""
        path = Path(path)
        if not path.exists():
            return PageDataset()

        payload = json.loads(path.read_text(encoding="utf-8"))
        return PageDataset.from_dict(payload)

    @staticmethod
    def save(dataset: PageDataset, path: Path | str) -> None:
        """Save dataset to JSON."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset.to_dict(), indent=2), encoding="utf-8")


