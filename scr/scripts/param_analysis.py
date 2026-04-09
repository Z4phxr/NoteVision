from pathlib import Path

from scr.pipeline.param_analyzer import ParamAnalyzer


def run() -> None:
    ParamAnalyzer.create_param_set()
    ParamAnalyzer.run_full_analysis(
        dataset_path=Path("data/dataset.json"),
        data_dir=Path("data"),
        output_path=Path("data/param_analysis.json"),
    )


if __name__ == "__main__":
    run()

