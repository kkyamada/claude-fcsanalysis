# quant_fluor50

Experiment-specific analysis protocol for quantifying marker fluorescence level to achieve 50% disruption/generation.

## Description

This skill calculates an EC50-like "Fluor50" value - the marker fluorescence intensity at which 50% of cells are in the target population (positive or negative).

**Use case**: After running `/fcsprocess` to gate populations, use this to determine the dose-response relationship between a marker (e.g., delivered protein amount) and a phenotypic outcome (e.g., gene disruption).

## How it works

1. Loads pre-computed gating strategies from `/fcsprocess` output
2. For each sample, sorts cells by marker fluorescence intensity
3. Calculates a sliding window ratio of target-positive cells
4. Fits a sigmoid curve to the data
5. Determines the Fluor50 (marker intensity at 50% target ratio)

## Usage

```bash
poetry run python .claude/skills/quant_fluor50/scripts/quant_fluor50_main.py \
    --input_dir <experiment_data_dir> \
    --color_marker <marker_fluorophore> \
    --color_50 <target_fluorophore>
```

## Arguments

| Argument | Description | Required | Default |
|----------|-------------|----------|---------|
| `--input_dir` | Path to experiment directory with data subdirectories | Yes | - |
| `--output_dir` | Output directory | No | `input_dir/output_fluor50` |
| `--color_csv` | Fluorophore-to-channel mapping file | No | `./color_info.csv` |
| `--flowcytometer` | Flowcytometer type | No | `CytoFlex` |
| `--color_marker` | Marker fluorophore (x-axis for EC50) | Yes | - |
| `--color_50` | Target fluorophore for 50% determination | Yes | - |
| `--window_size` | Sliding window size for ratio calculation | No | `100` |
| `--verbose` | Enable verbose output | No | `False` |

## Prerequisites

- Run `/fcsprocess` first to generate gating strategies
- Gating strategy files must exist at: `{input_dir}/../output/{data_dir}/gating_strategy.gml`

## Output

```
output_fluor50/
├── {data_dir}_fluor50.png       # Sigmoid fit plot for each dataset
├── {data_dir}_fluor50.csv       # Per-sample results for each dataset
├── fluor50_summary_{timestamp}.csv  # Aggregated results
├── args_{timestamp}.json        # Arguments used
└── quant_fluor50_{timestamp}.log    # Processing log
```

### Results CSV columns

| Column | Description |
|--------|-------------|
| Sample | Sample filename |
| day | Extracted day number from sample name |
| rep | Extracted replicate number from sample name |
| num_events | Number of gated events analyzed |
| fluor50 | Marker intensity at 50% target ratio |
| data_dir | Source data directory |

## Example

```bash
# After running fcsprocess on experiment data:
poetry run python .claude/skills/quant_fluor50/scripts/quant_fluor50_main.py \
    --input_dir ./examples/260105_HEK293T_GFPDisruption/data \
    --color_marker mCherry \
    --color_50 GFP \
    --flowcytometer CytoFlex \
    --window_size 100
```
