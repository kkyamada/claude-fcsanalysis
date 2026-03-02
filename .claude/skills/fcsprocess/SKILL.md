---
name: fcsprocess
description: FCS data processing script to semi-automatically define gating strategy and quantify fluorescently-distinguishable populations within mammalian cells. Use when processing flow cytometry data with hierarchical gating analysis.
---

## Overview
This skill processes flow cytometry analysis data to quantify the mCherry OFF population using hierarchical gating on specified plots.

## How to use
To process FCS files, run the processing script with an input directory containing .fcs files and an output directory:

```bash
poetry run python path/to/this/repository/.claude/skills/fcsprocess/scripts/fcs_main.py
```
Use the required arguments as follows.

## Required arguments
- `--input_dir`: Path to the input directory containing .fcs files (and optionally a .csv compensation file, but compensation is not implemented yet.)
- `--input_gml`: Path to the default gating strategy for the cell type and flowcytometer used. Default gates can be manually generated using `claude-fcsanalysis/notebooks/gate_initialization.ipynb` and saved under `claude-fcsanalysis/gating_strategies`.
- `--color_quant`: String to indicate fluorophores and +/- symbols to indicate thresholding directions to define cell populations to be quantified. e.g. mCherry+/APC-

## Optional arguments
- `--output_dir`: Path to the output directory where results will be saved. Used when this need to be manually specified.
- `--color_csv`: Path to the .csv file containing the information of fluorophores and channels for flowcytometers. By default, it should use `claude-fcsanalysis/color_info.csv`
- `--flowcytometer`: String to specify the type of flowcytometer used to collect data in .fcs file.
- `--ctrl_key`: String to indicate control samples. These should appear in at least one of the input .fcs filenames. Set to Mock by default.
- `--color_live`: String to indicate fluorophores and +/- symbol to indicate thresholding direction to define stained live/dead cell populations. e.g. LDAqua-
- `--color_marker`: String to indicate marker fluorophores and +/- symbol to indicate thresholding direction to define cell populations of interest. Up to two keys can be combined with a slash symbol. e.g. mCherry+/GFP-
- `--thresh_ratio`: Ratio to determine the final quantification threshold when using the control samples. This could be experiment/cell type specific.
- `--marker_mode`: Mode to define if the control sample defined with `--crtl_key` contains the expected marker color. Set as either single (default) or single_reverse. The single mode expects the control sample has the expected marker color, and the single_reverse mode expects the control sample has no marker color.
- `--marker_n_components`: Number of mixture model components to define marker threshold value (default: 2). 2 for bimodal and 1 for unimodal marker distribution in the control samples.
- `--vis_mode`: Mode for visualization only relevant if `--color_quant` has one color for quantification. Set as either default (default) or last. The default mode visualize quantification channel vs SSC-A, and the last mode visualize quantification channel vs last used channel during gating.


## Things to verify before running
1. Make sure your `input_gml` is correct. Usually the `--input_dir` have the following nomenclature, so you should be able to tell the cell type at least. If not sure about flowcytometer used, ask to clarity before running the script.
   - DATE_EXPERIMENT
      - data
         - DATE_EXPERIMENT_DAY_REPLICATE
            - CELLTYPE_TREATMENT_CONDITION.fcs
2. By default without `--output_dir`, the output direcotry is generated as follows, and this layer structure is what's expected.
   - DATE_EXPERIMENT
      - data
         - DATE_EXPERIMENT_DAY_REPLICATE
            - fcs files
      - output
         - DATE_EXPERIMENT_DAY_REPLICATE
            - output files and directories
3. Make sure you use right arguments for `--color_live`, `--color_marker`, and `--color_quant`. These arguments can be experiment-specific, so ask to clarity before running the script if you were not sure.

## Process
When this skill is invoked:
1. Verify the input directory exists and contains .fcs files
2. Create the output directory if it doesn't exist
3. Run the processing script with the provided input and output directories
4. The script will:
   - Initialize gating strategy from input GML file
   - Set up primary gates:
     - TimeQC: Optimize time gate based on event rates within each sample
        - This part is based on noise detection in Time vs SSC-A.
     - Viable: Identify viable cells using FSC-A vs SSC-A
        - This part requires default gate from `--input_gml` and modulate its coordinates and rotation to maximize inner population density.
     - Singlets: Identify singlets using FSC-A vs FSC-H
        - This part uses robust Theil-Sen regression on the viable population to detect parallelogram-shape gate.
   - Set up optional live/dead gate (if `--color_live` specified)
   - Detect control samples using `--ctrl_key` pattern matching
   - Set up marker gates (if `--color_marker` specified) using control samples
        - This can be done in one dimension using a Rectangular gate or two dimensions using a Quadrant gate.
   - Set up quantification gates using `--color_quant` and control samples
        - This can be done in one dimension using a Rectangular gate or two dimensions using a Quadrant gate.
   - Generate scatter plots with gate boundaries for each sample
   - Save outputs:
     - Figures to `<output_dir>/figures/`
     - Gating strategy to `<output_dir>/gating_strategy.gml`
     - CSV results to `<output_dir>/`
     - Arguments to `<output_dir>/args_<timestamp>.json`
     - Logs to `<output_dir>/fcsprocess_<timestamp>.log`

## Additional resources
Usage examples are to be written in [examples.md](examples.md)

## Utility scripts
Utility scripts to validate input files are to be written.
