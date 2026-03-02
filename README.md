# FCS Analysis Pipeline

A semi-automated flow cytometry analysis pipeline for processing FCS files with hierarchical gating strategies. Built on [FlowKit](https://github.com/whitews/FlowKit).

## What It Does

This tool helps you:

1. **Automatically identify cells** - Filters debris and identifies viable single cells using FSC/SSC gating
2. **Set fluorescence thresholds** - Uses Gaussian Mixture Models to find optimal thresholds based on control samples
3. **Quantify populations** - Calculates percentages of positive/negative populations for your markers of interest
4. **Generate figures** - Creates publication-ready scatter plots showing your gating strategy

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-fcsanalysis.git
cd claude-fcsanalysis

# Install with Poetry
poetry install
```

## Quick Start

### Basic Usage

```bash
python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir path/to/fcs_files/ \
    --input_gml gating_strategies/default_gates_CytoFlex_HEK293T.gml \
    --color_quant "mCherry+"
```

This will:
- Load all `.fcs` files from the input directory
- Apply the gating strategy (TimeQC → Viable → Singlets)
- Set a threshold for mCherry+ cells based on control samples
- Output results to `path/to/output/`

### Common Examples

#### Example 1: Single-color quantification
Quantify mCherry-positive cells in HEK293T samples:

```bash
python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir examples/260106_HEK293T_mCherry/data/260106_HEK293T_mCherry_day3_rep1 \
    --input_gml gating_strategies/default_gates_CytoFlex_HEK293T.gml \
    --flowcytometer CytoFlex \
    --ctrl_key "Mock" \
    --color_quant "mCherry+"
```

#### Example 2: Two-color quantification
Quantify both GFP and mCherry populations:

```bash
python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir path/to/fcs_files/ \
    --input_gml gating_strategies/default_gates_CytoFlex_HEK293T.gml \
    --color_quant "GFP+/mCherry+"
```

#### Example 3: With live/dead staining
Include a viability gate before quantification:

```bash
python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir path/to/fcs_files/ \
    --input_gml gating_strategies/default_gates_CytoFlex_HEK293T.gml \
    --color_live "LDAqua-" \
    --color_quant "mCherry+"
```

#### Example 4: With marker pre-gating
Gate on a marker population before quantification:

```bash
python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir path/to/fcs_files/ \
    --input_gml gating_strategies/default_gates_CytoFlex_HEK293T.gml \
    --color_marker "mCherry+" \
    --color_quant "GFP+"
```

## Input Requirements

### FCS Files
- Place all `.fcs` files for one experiment in a single directory
- Include control samples (e.g., "Mock" in filename) for threshold determination
- Supported flowcytometers: CytoFlex (18-bit), ZE5 (24-bit)

### Gating Strategy (GML file)
The pipeline uses a GatingML file to define initial gates. Pre-configured templates are available in `gating_strategies/`:

| File | Cell Type | Flowcytometer |
|------|-----------|---------------|
| `default_gates_CytoFlex_HEK293T.gml` | HEK293T | CytoFlex |
| `default_gates_CytoFlex_EL4.gml` | EL4 | CytoFlex |
| `default_gates_ZE5_MOLM13.gml` | MOLM13 | ZE5 |

### Color Info CSV
The `color_info.csv` file maps fluorophore names to channel names for each flowcytometer:

```csv
Fluorophore,CytoFlex,ZE5
mCherry,mCherry-A,mCherry-A
GFP,GFP-A,GFP-A
APC,APC-A,APC-A
```

## Output

The pipeline generates:

```
output/
├── figures/              # Scatter plots for each sample
│   ├── Sample1.png
│   └── Sample2.png
├── gating_strategy.gml   # Final gating strategy (can be reused)
├── results.csv           # Quantification results
├── args_*.json           # Arguments used for this run
└── fcsprocess_*.log      # Processing log
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input_dir` | Directory containing FCS files | Required |
| `--input_gml` | Path to gating strategy GML file | Required |
| `--output_dir` | Output directory | `../output/<input_dir_name>` |
| `--flowcytometer` | Flowcytometer type (`CytoFlex` or `ZE5`) | `CytoFlex` |
| `--ctrl_key` | Keyword to identify control samples | `Mock` |
| `--color_live` | Live/dead marker (e.g., `LDAqua-`) | None |
| `--color_marker` | Marker for pre-gating (e.g., `mCherry+`) | None |
| `--color_quant` | Markers for quantification | Required |
| `--thresh_ratio` | Percentile for threshold (0-1) | `0.98` |
| `--verbose` | Enable diagnostic output | False |

### Marker Syntax
Use `+` or `-` suffix to indicate positive or negative selection:
- `mCherry+` - Select mCherry-positive cells
- `GFP-` - Select GFP-negative cells
- `mCherry+/GFP-` - Two markers (creates quadrant gate)

## Gating Hierarchy

```
root
└── TimeQC          (Time-based quality control)
    └── Viable      (FSC-A vs SSC-A: cell identification)
        └── Singlets    (SSC-A vs SSC-H: doublet exclusion)
            └── [Live]      (Optional: viability dye)
                └── [Marker]    (Optional: marker pre-gate)
                    └── Quant   (Final quantification gate)
```

## Troubleshooting

### Cell type of interest or flowcytometer is not listed.
This pipeline requires default gate setting for each combination of cell type and flowcytometer. By default, celltypes and flowcytoemter available can be found uner `./gating_strategies` and `color_info.csv`.
For a new cell type or flowcytometer, first visit `notebooks/gate_initialization.ipynb`. This file provides an initial setup to create a default gating strategy for the cell type of interest and flowcytoemter. Then, add appropriate information in `color_info.csv`.

### Poor gating results
1. Run with `--verbose` to generate diagnostic plots
2. Check that `--ctrl_key` matches your control sample naming
3. Adjust `--thresh_ratio` for quantification (lower = more stringent threshold)

### Channel not found
Ensure your fluorophore is defined in `color_info.csv` with the correct channel name for your flowcytometer.

## License

MIT License
