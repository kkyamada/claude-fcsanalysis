#!/bin/zsh

# poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
# --experiment_dir ./examples/260101_EL4_mCherryDisruption \
# --input_gml ./gating_strategies/default_gates_CytoFlex_EL4.gml \
# --flowcytometer CytoFlex \
# --color_quant mCherry- \
# --ctrl_key Mock \
# --quant_thresh 0.95

poetry run python .claude/skills/quant_fluor50/scripts/quant_fluor50_main.py \
--experiment_dir ./examples/260105_HEK293T_GFPDisruption/ \
--flowcytometer CytoFlex \
--color_marker mCherry-A \
--color_50 GFP-A