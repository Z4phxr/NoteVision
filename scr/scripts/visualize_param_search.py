from pathlib import Path

from scr.config.paths import DATA_DIR
from scr.pipeline.param_analyzer import ParamAnalyzer


def run() -> None:
    ParamAnalyzer.visualize(
        input_path=DATA_DIR / "param_analysis.json",
        output_path=DATA_DIR / "param_analysis_visualization",
    )


if __name__ == "__main__":
    run()
