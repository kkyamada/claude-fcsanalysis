# FCS Processing Examples

This file contains working examples from `run_all.sh` for reference when running the `/fcsprocess` skill.

## Example 1: mCherry Disruption Assay (EL4 cells)

**Experiment**: Quantify mCherry-negative cells after disruption treatment in EL4 mCherry reporter cells.

```bash
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir ./examples/260101_EL4_mCherryDisruption/data/260101_EL4_mCherryDisruption_day3_rep1 \
    --input_gml ./gating_strategies/default_gates_CytoFlex_EL4.gml \
    --flowcytometer CytoFlex \
    --color_quant mCherry- \
    --ctrl_key Mock \
    --thresh_ratio 0.95
```

**Key parameters**:
- `color_quant mCherry-`: Quantify mCherry-negative (disrupted) population
- `thresh_ratio 0.95`: 95th percentile threshold

---

## Example 2: GFP Uptake Assay (EL4 cells)

**Experiment**: Quantify GFP-positive cells after GFP protein delivery in EL4 cells.

```bash
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir ./examples/260102_EL4_GFPTransfection/data/260102_EL4_GFPuptake_rep1 \
    --input_gml ./gating_strategies/default_gates_CytoFlex_EL4.gml \
    --flowcytometer CytoFlex \
    --color_quant GFP+ \
    --ctrl_key Mock \
    --thresh_ratio 0.99
```

**Key parameters**:
- `color_quant GFP+`: Quantify GFP-positive population
- `thresh_ratio 0.99`: Higher threshold (99th percentile) for cleaner separation

---

## Example 3: Surface Marker Disruption with Live/Dead (MOLM13 cells)

**Experiment**: Quantify APC-negative (marker-disrupted) cells in MOLM13, with live/dead gating.

```bash
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir ./examples/260103_MOLM13_MarkerDisruption/data/260103_MOLM13_MarkerDisruption_day7_rep1 \
    --input_gml ./gating_strategies/default_gates_ZE5_MOLM13.gml \
    --flowcytometer ZE5 \
    --color_live LDAqua- \
    --color_quant APC- \
    --ctrl_key Mock \
    --thresh_ratio 0.95
```

**Key parameters**:
- `flowcytometer ZE5`: ZE5 flowcytometer (24-bit)
- `color_live LDAqua-`: Gate on live cells (LDAqua-negative)
- `color_quant APC-`: Quantify APC-negative population

---

## Example 4: Lentiviral Transduction with Marker Pre-gating (MOLM13 cells)

**Experiment**: In lentivirally transduced MOLM13 cells (mCherry+), quantify APC-negative cells with live/dead gating.

```bash
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir ./examples/260104_MOLM13_LentiMarkerDisruption/data/260104_MOLM13_LentiMarkerDisruption_day7_rep1 \
    --input_gml ./gating_strategies/default_gates_ZE5_MOLM13.gml \
    --flowcytometer ZE5 \
    --color_live LDAqua- \
    --color_marker mCherry+ \
    --color_quant APC- \
    --ctrl_key Mock \
    --thresh_ratio 0.95 \
    --marker_mode single \
    --marker_n_components 2
```

**Key parameters**:
- `color_marker mCherry+`: Pre-gate on transduced (mCherry+) cells
- `marker_mode single`: Single-direction gating for marker
- `marker_n_components 2`: Expect bimodal distribution (transduced vs non-transduced)

---

## Example 5: GFP Disruption with Reverse Marker Gating (HEK293T cells)

**Experiment**: In mCherry-transfected HEK293T-d2GFP cells, quantify GFP-negative (disrupted) cells.

```bash
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir ./examples/260105_HEK293T_GFPDisruption/data/260105_HEK293T_GFPDisruption_day3_rep1 \
    --input_gml ./gating_strategies/default_gates_CytoFlex_HEK293T.gml \
    --flowcytometer CytoFlex \
    --color_marker mCherry+ \
    --color_quant GFP- \
    --ctrl_key Mock \
    --thresh_ratio 0.95 \
    --marker_mode single_reverse \
    --marker_n_components 1 \
    --vis_mode last
```

**Key parameters**:
- `marker_mode single_reverse`: Reverse direction for marker gating
- `marker_n_components 1`: Unimodal control (all cells are GFP+ baseline)
- `vis_mode last`: Visualize quantification vs last x-axis channel

---

## Example 6: Simple mCherry Quantification (HEK293T cells)

**Experiment**: Quantify mCherry-positive cells after transfection in HEK293T cells.

```bash
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
    --input_dir ./examples/260106_HEK293T_mCherry/data/260106_HEK293T_mCherry_day3_rep1 \
    --input_gml ./gating_strategies/default_gates_CytoFlex_HEK293T.gml \
    --flowcytometer CytoFlex \
    --color_quant mCherry+ \
    --ctrl_key Mock \
    --thresh_ratio 0.99
```

**Key parameters**:
- Simple quantification without live/dead or marker pre-gating
- `thresh_ratio 0.99`: Stringent threshold for clear positive population

---

## Summary Table

| Example | Cell Type | Flowcytometer | Live/Dead | Marker | Quantification |
|---------|-----------|---------------|-----------|--------|----------------|
| 1 | EL4 | CytoFlex | - | - | mCherry- |
| 2 | EL4 | CytoFlex | - | - | GFP+ |
| 3 | MOLM13 | ZE5 | LDAqua- | - | APC- |
| 4 | MOLM13 | ZE5 | LDAqua- | mCherry+ | APC- |
| 5 | HEK293T | CytoFlex | - | mCherry+ | GFP- |
| 6 | HEK293T | CytoFlex | - | - | mCherry+ |

## Gating Strategy Files

| Cell Type | Flowcytometer | GML File |
|-----------|---------------|----------|
| EL4 | CytoFlex | `gating_strategies/default_gates_CytoFlex_EL4.gml` |
| MOLM13 | ZE5 | `gating_strategies/default_gates_ZE5_MOLM13.gml` |
| HEK293T | CytoFlex | `gating_strategies/default_gates_CytoFlex_HEK293T.gml` |
