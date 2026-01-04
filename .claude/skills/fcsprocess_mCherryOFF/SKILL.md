---
name: fcsprocess_mCherryOFF
description: FCS data processing script to quantify mCherry OFF population within mammalian cells. Use when processing flow cytometry data with hierarchical gating analysis.
---

## Overview
This skill processes flow cytometry analysis data to quantify the mCherry OFF population using hierarchical gating on specified plots.

## How to use

To process FCS files, run the processing script with an input directory containing .fcs files and an output directory:

```bash
poetry run python /Users/keisuke/claude_codes/claude-fcsanalysis/.claude/skills/fcsprocess_mCherryOFF/scripts/process_fcs.py --input_dir <input_directory> --output_dir <output_directory>
```

Replace `<input_directory>` with the path to the directory containing .fcs files and `<output_directory>` with the path where results should be saved.

## Required arguments

- `--input_dir`: Path to the input directory containing .fcs files (and optionally a .csv compensation file)
- `--output_dir`: Path to the output directory where results will be saved

## Process

When this skill is invoked:
1. Verify the input directory exists and contains .fcs files
2. Create the output directory if it doesn't exist
3. Run the processing script with the provided input and output directories
4. The script will:
   - Perform hierarchical gating analysis (FSC-A vs SSC-A, FSC-A vs FSC-H, B525-A vs Y610-A)
   - Determine thresholds using Mock samples
   - Quantify mCherry OFF populations
   - Save figures to `<output_dir>/figures/<dir_name>/`
   - Save CSV results to `<output_dir>/curated_<dir_name>.csv`

## Additional resources
Usage examples are to be written in [examples.md](examples.md)

## Utility scripts
Utility scripts to validate input files are to be written.
