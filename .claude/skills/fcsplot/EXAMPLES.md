# FCS Plot Examples

Reference configurations and scripts from past experiments. Use these when working with similar cell types and experimental designs.

**Note:** Most plots can now be generated using the unified `/fcsplot` skill CLI. Example scripts are kept for reference and for complex plots (e.g., histograms with raw FCS data).

---

## EL4 Cell Line (Mouse Lymphoma)

**Instrument**: CytoFlex (18-bit, T=262143)

### Common Configuration

All EL4 experiments use these settings in `plot_config.yaml`:

```yaml
style: "publication"
colors:
  control_color: "#808080"
  highlight_color: "#4A7FE8"
bar:
  error_capsize: 8
  error_linewidth: 2.0
  show_title: false
  show_points: true
  point_size: 18
  point_facecolor: "white"
  point_edgecolor: "#333333"
  control_first: true
line:
  error_style: "bars"
  error_capsize: 8
  error_linewidth: 2.0
  show_title: false
```

### 260101_EL4_mCherryDisruption

| Property | Value |
|----------|-------|
| Marker | mCherry |
| Gate | `mCherry-` (negative) |
| Treatments | Control vs treatment at multiple concentrations |

**Scripts:**
- `examples/260101_EL4_mCherryDisruption/plot_bar.py` - Bar plot grouped by cell_type
- `examples/260101_EL4_mCherryDisruption/plot_dose_response.py` - Line plot, x=concentration

**CLI equivalent:**
```bash
# Bar plot
python .claude/skills/fcsplot/scripts/fcs_plot.py --experiment_dir examples/260101_EL4_mCherryDisruption --plot_type bar --gate_name "mCherry-" --x_col condition --hue cell_type

# Dose response
python .claude/skills/fcsplot/scripts/fcs_plot.py --experiment_dir examples/260101_EL4_mCherryDisruption --plot_type line --gate_name "mCherry-"
```

### 260102_EL4_GFPTransfection

| Property | Value |
|----------|-------|
| Marker | GFP |
| Gate | `GFP+` (positive, threshold is `min`) |
| Treatments | Mock, ProteinA, ProteinB at 1nM-1uM |

**Scripts:**
- `examples/260102_EL4_GFPTransfection/plot_dose_response.py` - Line plot with symlog x-scale, distinct colors per treatment
- `examples/260102_EL4_GFPTransfection/plot_histogram.py` - Multi-panel histograms (requires raw FCS data)

**CLI equivalent:**
```bash
# Dose response with symlog scale
python .claude/skills/fcsplot/scripts/fcs_plot.py --experiment_dir examples/260102_EL4_GFPTransfection --plot_type line --gate_name "GFP+" --hue treatment --x_scale symlog
```

**Histogram layout:** (use script - requires raw FCS data)
- Columns = treatments (ProteinA, ProteinB)
- Rows = Mock (top, as baseline) + concentrations
- Colors: Mock=gray, each treatment=distinct color from Set2

---

## MOLM13 Cell Line (Human AML)

**Instrument**: ZE5 (24-bit, T=16777215)

### 260103_MOLM13_MarkerDisruption

| Property | Value |
|----------|-------|
| Marker | APC |
| Gate | `APC-` (negative, threshold is `max`) |
| Treatments | Mock, ProteinA/B (Control/Target) |

**Scripts:**
- `examples/260103_MOLM13_MarkerDisruption/plot_histogram.py` - Standard grid layout

**Key settings:**
- Colors: Mock=gray (`#808080`), all others=default blue (`#4A7FE8`)
- Standard grid layout (not Mock-at-top like EL4 GFP)
- Gate threshold extracted from `max` value (below = negative)

### 260104_MOLM13_LentiMarkerDisruption

| Property | Value |
|----------|-------|
| Marker | APC (with mCherry+ parent gate) |
| Gate | `APC-` (negative, nested under `mCherry_pos`) |
| Treatments | MOLM13Control/Target × Mock/ProteinA |

**Scripts:**
- `examples/260104_MOLM13_LentiMarkerDisruption/plot_histogram.py` - Standard grid layout

**Key settings:**
- Same as 260103: Mock=gray, all others=default blue
- Parent gate: `mCherry_pos` (not `Live`)

---

## HEK293T Cell Line (Human Embryonic Kidney)

**Instrument**: CytoFlex (18-bit, T=262143)

### 260105_HEK293T_GFPDisruption

| Property | Value |
|----------|-------|
| Marker | GFP (with mCherry+ parent gate) |
| Gate | `GFP-` (negative, nested under `mCherry+`) |
| Treatments | Mock, Mutant, WT at various concentrations |

**Scripts:**
- `examples/260105_HEK293T_GFPDisruption/plot_bar.py` - Bar plot grouped by cell_type

**CLI equivalent:**
```bash
python .claude/skills/fcsplot/scripts/fcs_plot.py --experiment_dir examples/260105_HEK293T_GFPDisruption --plot_type bar --gate_name "GFP-" --x_col condition --hue cell_type
```

**Key settings:**
- Same bar plot settings as EL4 mCherryDisruption
- Mock=gray, others=blue (via control_patterns detection)

### 260106_HEK293T_mCherry

| Property | Value |
|----------|-------|
| Marker | mCherry |
| Gate | `mCherry+` (positive) |
| Treatments | Mock, ProteinA at 0nM, 100nM, 400nM |
| Cell types | HEK293TChe (mCherry+), HEK293TControl |

**Scripts:**
- `examples/260106_HEK293T_mCherry/plot_bar.py` - Bar plot grouped by cell_type
- `examples/260106_HEK293T_mCherry/plot_dose_response.py` - Line plot, x=concentration

**CLI equivalent:**
```bash
# Bar plot
python .claude/skills/fcsplot/scripts/fcs_plot.py --experiment_dir examples/260106_HEK293T_mCherry --plot_type bar --gate_name "mCherry+" --x_col condition --hue cell_type

# Dose response
python .claude/skills/fcsplot/scripts/fcs_plot.py --experiment_dir examples/260106_HEK293T_mCherry --plot_type line --gate_name "mCherry+" --x_lim -20 450
```

**Key settings:**
- Same as EL4 mCherryDisruption

---

## Quick Reference

### Instrument Parameters

| Instrument | Bit Depth | T Parameter |
|------------|-----------|-------------|
| CytoFlex | 18-bit | 262143 |
| ZE5 | 24-bit | 16777215 |

### Gate Threshold Extraction

| Gate Type | Threshold From | Example |
|-----------|----------------|---------|
| Positive (`+`) | `min` value | GFP+ |
| Negative (`-`) | `max` value | APC-, mCherry- |

### Color Schemes

| Scheme | Use Case |
|--------|----------|
| Mock=gray, others=single blue | Simple comparison (MOLM13) |
| Mock=gray, treatments=Set2 colors | Multiple treatment comparison (EL4 GFP) |
| Control=gray, treatment=blue | Control vs treatment (EL4 mCherry) |

### Histogram Layouts

| Layout | Use Case | Example |
|--------|----------|---------|
| Standard grid | Simple multi-sample | MOLM13 |
| Mock-at-top columns | Dose-response with baseline | EL4 GFP |

---

## File Locations

- **Example experiments**: `examples/` directory
- **Plot utilities**: `fcs_utils/plot_utils.py`
- **Config system**: `fcs_utils/plot_config.py`
