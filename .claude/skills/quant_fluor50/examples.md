# quant_fluor50 Examples

This skill calculates the marker fluorescence intensity at which 50% of cells are in the target population (Fluor50), similar to EC50 analysis.

**Prerequisites**: Run `/fcsprocess` first to generate gating strategies for your data.

---

## Example 1: GFP Disruption Analysis (HEK293T cells)

**Experiment**: After running fcsprocess on HEK293T-d2GFP cells transfected with mCherry-tagged protein, determine the mCherry fluorescence level (delivery amount) needed to achieve 50% GFP disruption.

```bash
# First, run fcsprocess to generate gating strategies
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir ./examples/260105_HEK293T_GFPDisruption/data/260105_HEK293T_GFPDisruption_day3_rep1 \
    --input_gml ./gating_strategies/default_gates_CytoFlex_HEK293T.gml \
    --flowcytometer CytoFlex \
    --color_marker mCherry+ \
    --color_quant GFP- \
    --ctrl_key Mock \
    --thresh_ratio 0.95 \
    --marker_mode single_reverse \
    --marker_n_components 1

# Then, run quant_fluor50 analysis
poetry run python .claude/skills/quant_fluor50/scripts/quant_fluor50_main.py \
    --input_dir ./examples/260105_HEK293T_GFPDisruption/data \
    --color_marker mCherry \
    --color_50 GFP \
    --flowcytometer CytoFlex \
    --window_size 100
```

**Key parameters**:
- `color_marker mCherry`: X-axis marker for EC50-like calculation (delivered protein amount)
- `color_50 GFP`: Target channel for 50% determination (GFP disruption)
- `window_size 100`: Sliding window size for smoothing the ratio calculation

**Expected output**:
- `260105_HEK293T_GFPDisruption_day3_rep1_fluor50.png`: Sigmoid fit plot
- `260105_HEK293T_GFPDisruption_day3_rep1_fluor50.csv`: Per-sample results
- `fluor50_summary_*.csv`: Aggregated results across all data directories

---

## Example 2: mCherry Disruption with Multiple Replicates

**Experiment**: Analyze multiple replicates of an mCherry disruption experiment to get Fluor50 statistics.

```bash
# Run quant_fluor50 on all replicates
poetry run python .claude/skills/quant_fluor50/scripts/quant_fluor50_main.py \
    --input_dir ./examples/260101_EL4_mCherryDisruption/data \
    --color_marker GFP \
    --color_50 mCherry \
    --flowcytometer CytoFlex \
    --window_size 150 \
    --verbose
```

**Key parameters**:
- `window_size 150`: Larger window for smoother ratio calculation with more events
- `verbose`: Enable detailed logging and diagnostic information

---

## Example 3: Custom Output Directory

```bash
poetry run python .claude/skills/quant_fluor50/scripts/quant_fluor50_main.py \
    --input_dir ./examples/260105_HEK293T_GFPDisruption/data \
    --output_dir ./results/fluor50_analysis \
    --color_marker mCherry \
    --color_50 GFP \
    --flowcytometer CytoFlex
```

---

## Interpreting Results

The output CSV contains:

| Column | Description |
|--------|-------------|
| Sample | Sample filename (e.g., `sample_day3_rep1.fcs`) |
| day | Extracted day number from sample name |
| rep | Extracted replicate number from sample name |
| num_events | Number of gated events analyzed |
| fluor50 | Marker intensity at 50% target ratio |
| data_dir | Source data directory |

**Fluor50 interpretation**:
- Lower Fluor50 = More potent (less marker needed for 50% effect)
- Higher Fluor50 = Less potent (more marker needed for 50% effect)
- NaN = Could not determine (insufficient data range or poor fit)

---

## Directory Structure Requirements

```
experiment/
├── data/
│   ├── experiment_day3_rep1/    # FCS files
│   ├── experiment_day3_rep2/
│   └── experiment_day7_rep1/
└── output/                       # Created by fcsprocess
    ├── experiment_day3_rep1/
    │   └── gating_strategy.gml   # Required by quant_fluor50
    ├── experiment_day3_rep2/
    │   └── gating_strategy.gml
    └── experiment_day7_rep1/
        └── gating_strategy.gml
```
