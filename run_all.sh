#!/bin/zsh

# Experiment type: mCherry disruption assay in EL4 mCherry reporter cells
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--experiment_dir ./examples/260101_EL4_mCherryDisruption \
--input_gml ./gating_strategies/default_gates_CytoFlex_EL4.gml \
--flowcytometer CytoFlex \
--color_quant mCherry- \
--ctrl_key Mock \
--thresh_ratio 0.95

# Experiment type: GFP uptake assay in EL4 cells
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--experiment_dir ./examples/260102_EL4_GFPTransfection \
--input_gml ./gating_strategies/default_gates_CytoFlex_EL4.gml \
--flowcytometer CytoFlex \
--color_quant GFP+ \
--ctrl_key Mock \
--thresh_ratio 0.99


# Experiment type: Surface marker disruption assay in MOLM13 cells
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--experiment_dir ./examples/260103_MOLM13_MarkerDisruption \
--input_gml ./gating_strategies/default_gates_ZE5_MOLM13.gml \
--flowcytometer ZE5 \
--color_live LDAqua- \
--color_quant APC- \
--ctrl_key Mock \
--thresh_ratio 0.95

# Experiment type: Surface marker disruption assay in lentivirally transduced MOLM13 cells
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--experiment_dir ./examples/260104_MOLM13_LentiMarkerDisruption \
--input_gml ./gating_strategies/default_gates_ZE5_MOLM13.gml \
--flowcytometer ZE5 \
--color_live LDAqua- \
--color_marker mCherry+ \
--color_quant APC- \
--ctrl_key Mock \
--thresh_ratio 0.95 \
--marker_mode single \
--marker_n_components 2

# Experiment type: GFP dirsuption assay in HEK293Td2GFP cells
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--experiment_dir ./examples/260105_HEK293T_GFPDisruption \
--input_gml ./gating_strategies/default_gates_CytoFlex_HEK293T.gml \
--flowcytometer CytoFlex \
--color_marker mCherry+ \
--color_quant GFP- \
--ctrl_key Mock \
--thresh_ratio 0.95 \
--marker_mode single_reverse \
--marker_n_components 1 \
--vis_mode last

# Experiment type: mCherry transfection assay in HEK293T mCherry reporter cells
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--experiment_dir ./examples/260106_HEK293T_mCherry \
--input_gml ./gating_strategies/default_gates_CytoFlex_HEK293T.gml \
--flowcytometer CytoFlex \
--color_quant mCherry+ \
--ctrl_key Mock \
--thresh_ratio 0.99