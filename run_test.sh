#!/bin/zsh

poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--input_dir ./examples/260105_HEK293T_GFPDisruption/data/260106_HEK293T_GFPDisruption_day3_rep2 \
--input_gml ./gating_strategies/default_gates_CytoFlex_HEK293T.gml \
--flowcytometer CytoFlex \
--color_marker mCherry+ \
--color_quant GFP- \
--ctrl_key Mock \
--thresh_ratio 0.95 \
--marker_mode single_reverse \
--marker_n_components 1 \
--vis_mode last