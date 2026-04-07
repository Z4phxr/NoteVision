import json
from pathlib import Path

from scr.ParametersSearch.models import ParamSet


def load_best_horizontal_params(settings_path: Path) -> list[ParamSet]:
    """Load BestHorizontalParameters from settings.json as ParamSet objects."""
    payload = json.loads(settings_path.read_text(encoding="utf-8"))
    raw_params = payload.get("BestHorizontalParameters", [])
    return [ParamSet(**item) for item in raw_params]


def get_first_param_set(settings_path: Path) -> ParamSet | None:
    """Return first ParamSet from settings or None when list is empty."""
    param_sets = load_best_horizontal_params(settings_path)
    return param_sets[0] if param_sets else None
