from scr.config.paths import CLEAN_DIR, DATASET_PATH, DATA_DIR
from scr.pipeline.param_analyzer import ParamAnalyzer


def run() -> None:
    ParamAnalyzer.create_param_set()
    ParamAnalyzer.run_full_analysis(
        dataset_path=DATASET_PATH,
        data_dir=CLEAN_DIR,
        output_path=DATA_DIR / "param_analysis.json",
    )


if __name__ == "__main__":
    run()

