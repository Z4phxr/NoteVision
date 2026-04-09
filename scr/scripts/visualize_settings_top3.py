from scr.config.paths import CLEAN_DIR, DATA_DIR, DATASET_PATH, SETTINGS_PATH
from scr.pipeline.param_analyzer import ParamAnalyzer


def run() -> None:
    """Draw first 3 ParamSets from settings.json on all dataset photos."""
    ParamAnalyzer.visualize_settings(
        settings_path=SETTINGS_PATH,
        dataset_path=DATASET_PATH,
        data_dir=CLEAN_DIR,
        output_path=DATA_DIR / "settings_top3_visualization",
        top_k=3,
    )


if __name__ == "__main__":
    run()

