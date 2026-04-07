# DataInput Module - Helper in data handling

Simple input + serialization flow for page metadata.

## Files

- `config.py` - set data folder once (`DATA_DIR`) and dataset file path (`DATASET_PATH`)
- `models.py` - `PageRecord` and `PageDataset`
- `storage.py` - JSON load/save (`DatasetJsonStore`)
- `discovery.py` - detect image files that are not yet in dataset
- `prompt.py` - user prompts with validation
- `data_create.py` - entry point (`sync_dataset`)

## How it works

1. Program loads `dataset.json` (or creates an empty dataset).
2. Program scans `data/` for images.
3. Program asks metadata only for new images not in dataset.
4. Program saves updated dataset.

## Data model

- `staff_count` means the number of staff groups on a page.
- The real number of staff lines is always `staff_count * 5`.
- `bar_line_count` is the accurate number of bar lines found on the page.
- `possible_vertical_lines` is the relaxed detection target computed as:

```text
bar_line_count + (2 * staff_count)
```

This allows staff-edge false positives during detection.

## Run

```powershell
python -m Piano.DataInput.data_create
```


