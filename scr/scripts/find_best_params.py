from scr.config.paths import CLEAN_DIR, DATASET_PATH
from scr.pipeline.param_analyzer import ParamAnalyzer


def run() -> None:
    """Find best parameter sets and save them to settings.json."""
    best_params = ParamAnalyzer.find_best_param_sets(
        data_dir=CLEAN_DIR,
        dataset_path=DATASET_PATH,
        max_photos=3,
        save=True,
    )
    print(f"Final good param combos: {len(best_params)}")


if __name__ == "__main__":
    run()

