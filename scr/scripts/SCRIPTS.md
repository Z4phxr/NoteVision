# Scripts

This folder contains runnable entry points for dataset preparation, parameter analysis, and visualization.

## Available Scripts

- `dataset_sync.py`
  - Command: `python -m scr.scripts.dataset_sync`
  - Scans `data/` for new images, asks for metadata, and updates `data/dataset.json`.

- `param_analysis.py`
  - Command: `python -m scr.scripts.param_analysis`
  - Runs full parameter analysis and saves ranked results to `data/param_analysis.json`.

- `find_best_params.py`
  - Command: `python -m scr.scripts.find_best_params`
  - Runs progressive filtering on first photos from dataset and saves good sets to `data/settings.json`.

- `visualize_param_search.py`
  - Command: `python -m scr.scripts.visualize_param_search`
  - Draws top results from `data/param_analysis.json` on all dataset photos.

- `visualize_settings_top3.py`
  - Command: `python -m scr.scripts.visualize_settings_top3`
  - Draws first 3 parameter sets from `data/settings.json` on all dataset photos.

- `visualize_photo_params.py`
  - Command:
    - `python -m scr.scripts.visualize_photo_params <photo_path>`
  - Draws all ranked parameter sets from `param_analysis.json` for one selected photo.

## Typical Run Order

1. `python -m scr.scripts.dataset_sync`
2. `python -m scr.scripts.find_best_params`
3. `python -m scr.scripts.visualize_settings_top3`

Alternative full-analysis flow:

1. `python -m scr.scripts.param_analysis`
2. `python -m scr.scripts.visualize_param_search`
