---
name: fcsplot
description: Generate publication-ready plots from FCS analysis summary data. Supports bar plots, line plots, heatmaps with configurable styling via presets or YAML config files.
---

## Overview
This skill generates visualizations from processed flow cytometry data (summary_processed.csv files). It provides a flexible configuration system that balances ease of use with customizability.

## How to use
Run the plotting script with an experiment directory that contains processed output:

```bash
poetry run python .claude/skills/fcsplot/scripts/fcs_plot.py \
    --experiment_dir <path_to_experiment>
```

## Required arguments
- `--experiment_dir`: Path to experiment directory containing `output/` subdirectory with `summary_processed.csv` files from fcsprocess.

## Optional arguments
- `--output_dir`: Path to output directory for plots (default: `experiment_dir/`)
- `--preset`: Style preset - "publication" (default), "exploratory", or "presentation"
- `--plot_type`: Type of plots to generate - "all", "bar", "line", "heatmap", or "multi"
- `--gate_name`: Specific gate to plot (default: all quantification gates)
- `--x_col`: Column for x-axis - "treatment", "condition" (treatment + concentration), "conc_value", or "cell_type"
- `--hue`: Column for color grouping - "cell_type" (default), "treatment", or "concentration"
- `--x_scale`: X-axis scale for line plots - "linear" (default) or "symlog" (for wide concentration ranges including 0)
- `--x_lim MIN MAX`: X-axis limits (e.g., `--x_lim -20 450`)
- `--ylabel`: Custom y-axis label (default: gate_name + %)
- `--output_name`: Custom output filename (without extension)
- `--generate_config`: Generate a default `plot_config.yaml` template in the experiment directory

## Configuration System

The skill uses a layered configuration system:

1. **Built-in defaults** - Sensible defaults for all settings
2. **Style presets** - Quick presets for common use cases
3. **User config file** - `plot_config.yaml` in experiment directory for custom settings
4. **Runtime arguments** - Command-line overrides

### Style Presets

| Preset | Use Case | Key Settings |
|--------|----------|--------------|
| `publication` | Journal figures | 300 DPI, small fonts, no grid |
| `exploratory` | Quick analysis | 100 DPI, larger figures, grid enabled |
| `presentation` | Slides/posters | 150 DPI, large fonts, thick lines |

### Custom Configuration

Generate a template config file:
```bash
poetry run python .claude/skills/fcsplot/scripts/fcs_plot.py \
    --experiment_dir <path> --generate_config
```

Then edit `plot_config.yaml` in your experiment directory:
```yaml
style: "publication"

figure:
  dpi: 300
  figsize_single: [4, 3]
  max_cols: 4

font:
  size_title: 14
  size_label: 12

colors:
  palette: "Set2"

bar:
  show_points: true
  width: 0.7
```

## Plot Types

### Bar Plot (`--plot_type bar`)
Compares gate percentages across treatments/conditions. Includes:
- Grouped bars by treatment
- Error bars (standard deviation)
- Individual data points overlay (configurable)

### Line Plot (`--plot_type line`)
Shows concentration-response relationships:
- X-axis: concentration values extracted from sample IDs
- Error bands or bars (configurable)

### Heatmap (`--plot_type heatmap`)
Displays gate values across cell types and treatments:
- Rows: cell types
- Columns: treatments
- Color intensity: percentage values

### Multi-panel (`--plot_type multi`)
Creates a grid of bar plots for all quantification gates in one figure.

## Expected Directory Structure

```
experiment_dir/
├── output/
│   ├── run_day1_rep1/
│   │   └── summary_processed.csv
│   ├── run_day1_rep2/
│   │   └── summary_processed.csv
│   └── ...
├── plot_config.yaml  # Optional custom config
└── plots/            # Generated output
    ├── bar_mCherry+_treatment.png
    ├── line_mCherry+_concentration.png
    └── ...
```

## Sample ID Parsing

The script parses sample IDs to extract experimental metadata:
- Format: `CellType_Treatment_Concentration.fcs`
- Example: `HEK293TChe_ProteinA_100nM.fcs` → cell_type="HEK293TChe", treatment="ProteinA", concentration="100nM"

## Examples

### Basic usage (all plot types with default settings)
```bash
poetry run python .claude/skills/fcsplot/scripts/fcs_plot.py \
    --experiment_dir examples/260106_HEK293T_mCherry
```

### Bar plot for specific gate with custom x-axis and hue
```bash
poetry run python .claude/skills/fcsplot/scripts/fcs_plot.py \
    --experiment_dir examples/260106_HEK293T_mCherry \
    --plot_type bar \
    --gate_name "mCherry+" \
    --x_col condition \
    --hue cell_type
```

### Dose response with symlog x-scale (for wide concentration ranges)
```bash
poetry run python .claude/skills/fcsplot/scripts/fcs_plot.py \
    --experiment_dir examples/260102_EL4_GFPTransfection \
    --plot_type line \
    --gate_name "GFP+" \
    --hue treatment \
    --x_scale symlog
```

### Dose response with custom x-axis limits
```bash
poetry run python .claude/skills/fcsplot/scripts/fcs_plot.py \
    --experiment_dir examples/260106_HEK293T_mCherry \
    --plot_type line \
    --gate_name "mCherry+" \
    --x_lim -20 450
```

### Publication-quality bar plot with custom labels and output name
```bash
poetry run python .claude/skills/fcsplot/scripts/fcs_plot.py \
    --experiment_dir examples/260105_HEK293T_GFPDisruption \
    --preset publication \
    --plot_type bar \
    --gate_name "GFP-" \
    --ylabel "GFP- Population (%)" \
    --output_name gfp_disruption_bar
```

## Past Experiment Examples

See `EXAMPLES.md` in this skill directory for detailed configurations and scripts from past experiments:

- **260101_EL4_mCherryDisruption**: Bar plots, dose-response curves for mCherry- quantification
- **260102_EL4_GFPTransfection**: Dose-response with symlog scale, multi-panel histograms with threshold

These examples include:
- Complete plot_config.yaml settings
- Full plotting scripts with comments
- Design decisions for specific visualization needs (e.g., histogram normalization to mode, Mock as baseline row)
