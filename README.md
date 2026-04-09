# NoteVision

This project uses computer vision to extract musical notes from sheet music and convert them into MIDI format.

## Project Overview

NoteVision is an Optical Music Recognition (OMR) project focused on:
- detecting music notation from sheet images,
- building structured metadata for pages/staves/symbols,
- preparing data for downstream MIDI conversion.

Current practical focus is robust detection of **treble clef** and **bass clef**, with parameter search pipelines used to tune line detection quality.

## Current Workflow

1. Sync page metadata and labels into `data/dataset.json`.
2. Run parameter search / filtering to find good `ParamSet` configurations.
3. Save filtered parameter sets to `data/settings.json`.
4. Visualize selected parameter sets on all pages.
5. Keep source photos in `data/clean/` (raw imports go through `data/raw/`).

## Project Structure

- `scr/models/` - domain models and dataset manager
- `scr/pipeline/` - image processing and parameter search
- `scr/io/` - dataset storage and sync utilities
- `scr/config/paths.py` - paths to `data/` assets
- `data/` - dataset files, analysis outputs, and `clean/` photos
- `assets/` - generated previews

## Documentation Index

- Models documentation: [`scr/models/MODELS.md`](scr/models/MODELS.md)
- Scripts documentation: [`scr/scripts/SCRIPTS.md`](scr/scripts/SCRIPTS.md)

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

## Dataset and License (DeepScoresV2)

The model currently being developed (treble and bass clef detection) is trained using the DeepScoresV2 dataset.

- Dataset is publicly available.
- License: Creative Commons Attribution 4.0 (CC BY 4.0).
- Original dataset source: [Zenodo - DeepScoresV2](https://zenodo.org/records/4012193).
- Original project repository (tools/annotations related to DeepScoresV2): [GitHub - obb_anns](https://github.com/yvan674/obb_anns).

The dataset is used in compliance with the license terms, and dataset authors are credited according to the official attribution guidelines.