# Models

This folder contains core data models used across the project.


## Main files and responsibilities

- `analysis.py`
  - `ParamSet`
    - Represents one horizontal line detection parameter combination.
    - Fields: `threshold`, `min_len_ratio`, `max_gap`, `canny_low`, `canny_high`.
    - Used by `ParamAnalyzer` to run grid search and filtering.
  - `PhotoResult`
    - Stores result for one image under one `ParamSet`.
    - Fields: `path`, `found_lines`, `target_lines`.
    - `matched` property indicates if detection matched expected count.
  - `ParamSetResult`
    - Aggregates one `ParamSet` performance across many photos.
    - Contains `photos` list and global `score`.
    - Used to rank candidates in full analysis flow.

- `page.py`
  - `PageRecord`
    - Metadata for one sheet page (`image_path`, `staff_count`, `bar_line_count`).
    - Provides computed properties:
      - `staff_line_count = staff_count * 5`
      - `possible_vertical_lines = bar_line_count + (2 * staff_count)`
    - Contains image-processing helpers (line detection, line normalization, drawing).
  - `StaffSlice`
    - One extracted staff area from a page (bounding coordinates + optional path).
    - Can hold child `ChunkSlice` items.
  - `ChunkSlice`
    - Smaller vertical segment extracted from a `StaffSlice`.
    - Useful for later symbol-level processing.
  - `PageDataset`
    - Container for all `PageRecord` items.
    - Supports operations like adding pages, listing known paths, and finding new image paths in `data/`.

## Model relationships

- `PageDataset` -> contains many `PageRecord`.
- `PageRecord` -> can contain many `StaffSlice`.
- `StaffSlice` -> can contain many `ChunkSlice`.
- `ParamSetResult` -> contains one `ParamSet` and many `PhotoResult`.

These two groups serve different concerns:
- `page.py` models describe dataset/page structure,
- `analysis.py` models describe experiment/evaluation results.

## Serialization and persistence

- `scr/io/dataset_store.py`
  - Saves/loads `PageDataset` to/from `data/dataset.json`.
- `ParamAnalyzer.run_full_analysis(...)`
  - Saves list of `ParamSetResult` to `data/param_analysis.json`.
- `ParamAnalyzer.find_best_param_sets(..., save=True)`
  - Saves filtered list of `ParamSet` to `data/settings.json`.

Keeping these formats explicit makes debugging and script interoperability easier.


## Usage Context

- `scr/io/` reads and writes `PageDataset` from/to `data/dataset.json`.
- `scr/pipeline/param_analyzer.py` produces and consumes `ParamSet`/`ParamSetResult`.
- `scr/scripts/` orchestrates end-to-end flows using these models.
