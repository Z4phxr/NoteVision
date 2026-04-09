from pathlib import Path
import argparse

from scr.config.paths import DATA_DIR
from scr.pipeline.param_analyzer import ParamAnalyzer


def run() -> None:
    parser = argparse.ArgumentParser(description="Visualize all ParamSet results for one photo.")
    parser.add_argument("photo_path", help="Path to the image (absolute or relative to data dir).")
    parser.add_argument(
        "--input",
        dest="input_path",
        default=str(DATA_DIR / "param_analysis.json"),
        help="Path to param_analysis.json.",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        default=str(DATA_DIR / "param_analysis_visualization"),
        help="Output directory for rendered images.",
    )
    args = parser.parse_args()

    ParamAnalyzer.visualize_photo_params(
        input_path=Path(args.input_path),
        photo_path=Path(args.photo_path),
        output_path=Path(args.output_path),
    )


if __name__ == "__main__":
    run()

