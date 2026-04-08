# NoteVision

Work in progress

This project uses computer vision to extract musical notes from sheet music and convert them into MIDI format.

## Structure

- `scr/models/` - domain models and dataset manager
- `scr/pipeline/` - image processing and parameter search
- `scr/io/` - dataset storage and sync utilities
- `scr/config/paths.py` - paths to `data/` assets
- `data/` - dataset and images
- `assets/` - generated previews

## Run

```powershell
python -m scr.io.dataset_create
```

## Goals

- Detect notes and symbols from sheet images
- Convert them into structured musical data
- Export to MIDI
- Provide a visual piano interface showing which keys to press

## Status
Currently working on note detection and extraction (OMR stage).

## Future Plans
- Improve accuracy with ML models
- Real-time processing
- Interactive piano learning interface