# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flow Cytometry Standard (FCS) analysis pipeline built on top of FlowKit. It provides semi-automated gating strategy definition and quantification of fluorescently-distinguishable populations within mammalian cells.

**Key capabilities:**
- Automated primary gating (TimeQC → Viable → Singlets)
- Secondary gating for markers and quantification
- Gaussian Mixture Model-based threshold detection
- Visualization of gating results
- GatingML 2.0 export with schema compliance fixes

## Repository Structure

```
claude-fcsanalysis/
├── fcs_utils/                    # Main Python package
│   ├── __init__.py
│   ├── primary_gates.py          # TimeQC, Viable, Singlet gates
│   ├── secondary_gates.py        # Marker and quantification gates
│   ├── visualization.py          # Plotting and figure generation
│   ├── process_id.py             # Sample ID processing utilities
│   └── utils_functions.py        # GML conversion utilities
├── gating_strategies/            # Default GML gating strategy templates
│   ├── default_gates_CytoFlex_*.gml
│   └── default_gates_ZE5_*.gml
├── examples/                     # Example datasets with FCS files
├── .claude/skills/fcsprocess/    # Claude Code skill for FCS processing
│   └── scripts/fcs_main.py       # Main entry point
├── color_info.csv                # Fluorophore-to-channel mapping
├── logs/                         # Log files (gitignored)
└── pyproject.toml                # Poetry dependencies
```

## Build and Run

```bash
# Install dependencies
poetry install

# Run FCS processing (via skill or directly)
python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir <path_to_fcs_files> \
    --input_gml <path_to_gating_strategy.gml> \
    --color_quant "mCherry+/GFP-"
```

## Key Dependencies

- **flowkit**: Core FCS file handling and gating (v1.3.0)
- **scipy**: Statistical functions
- **scikit-learn**: Gaussian Mixture Models for threshold detection
- **lxml**: XML processing for GatingML
- **seaborn/matplotlib**: Visualization

## Important Technical Details

### FlowKit GatingML Issues

FlowKit v1.3.0 has GatingML export/import issues:

1. **Gate IDs with special characters**: Gate names like `mCherry+` fail XML schema validation (`xs:ID` requires valid NCName)
2. **Schema validation**: `fk.Session()` validates against GatingML 2.0 schema before parsing

**Solution**: Use `utils_functions.convert_gml_to_standard()` to sanitize gate IDs:
- `mCherry+` → `mCherry_pos`
- `CD4-` (trailing minus) → `CD4_neg`

```python
from fcs_utils.utils_functions import convert_gml_to_standard

# Convert after FlowKit export
convert_gml_to_standard("gating_strategy.gml", "gating_strategy.gml")

# Now fk.Session() works
session = fk.Session(gating_strategy="gating_strategy.gml", fcs_samples=input_dir)
```

### Flowcytometer Settings

Different flowcytometers have different bit depths:
- **CytoFlex**: 18-bit (max value: 2^18-1 = 262143)
- **ZE5**: 24-bit (max value: 2^24-1)

### Visualization Module

Key functions in `fcs_utils/visualization.py`:
- `_setup_channel_lims()`: Calculates axis limits across all samples (handles empty parent arrays)
- `_generate_ticks()`: Generates "nice" tick values (prioritizes integers, 0.5, 0.2 increments)
- `process_data()`: Main visualization entry point

### Gating Workflow

1. **Primary gates** (automatic):
   - TimeQC: Filters time-based anomalies
   - Viable: FSC-A vs SSC-A polygon gate for cell identification
   - Singlets: SSC-A vs SSC-H for doublet exclusion

2. **Secondary gates** (configurable):
   - Live/Dead (optional): Based on viability dye
   - Marker gates: For population identification
   - Quantification gates: Rectangle or Quadrant gates for final quantification

## Claude Configuration

**Logging Directory**: Use `logs/` for any Claude-generated logs or outputs. This directory is gitignored.

**Skill Available**: `/fcsprocess` - Runs the FCS processing pipeline with hierarchical gating analysis.

## Common Tasks

### Adding a new gating strategy
1. Create a new `.gml` file in `gating_strategies/`
2. Define TimeQC and Viable gates with appropriate channel names
3. Use `convert_gml_to_standard()` if gate names contain special characters

### Debugging gating issues
1. Run with `--verbose` flag for diagnostic figures
2. Check `fcs_utils/visualization.py` for plot generation
3. Logs are saved to `output_dir/fcsprocess_<timestamp>.log`
