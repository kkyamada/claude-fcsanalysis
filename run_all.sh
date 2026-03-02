#!/bin/zsh

# Experiment type: mCherry disruption assay in EL4 mCherry reporter cells
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--input_dir ./examples/260101_EL4_mCherryDisruption/data/260101_EL4_mCherryDisruption_day3_rep1 \
--input_gml ./gating_strategies/default_gates_CytoFlex_EL4.gml \
--flowcytometer CytoFlex \
--color_quant mCherry- \
--ctrl_key Mock \
--thresh_ratio 0.95

poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--input_dir ./examples/260101_EL4_mCherryDisruption/data/260102_EL4_mCherryDisruption_day3_rep2 \
--input_gml ./gating_strategies/default_gates_CytoFlex_EL4.gml \
--flowcytometer CytoFlex \
--color_quant mCherry- \
--ctrl_key Mock \
--thresh_ratio 0.95

# Experiment type: GFP uptake assay in EL4 cells
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--input_dir ./examples/260102_EL4_GFPTransfection/data/260102_EL4_GFPuptake_rep1 \
--input_gml ./gating_strategies/default_gates_CytoFlex_EL4.gml \
--flowcytometer CytoFlex \
--color_quant GFP+ \
--ctrl_key Mock \
--thresh_ratio 0.99

poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--input_dir ./examples/260102_EL4_GFPTransfection/data/260103_EL4_GFPuptake_rep2 \
--input_gml ./gating_strategies/default_gates_CytoFlex_EL4.gml \
--flowcytometer CytoFlex \
--color_quant GFP+ \
--ctrl_key Mock \
--thresh_ratio 0.99

# Experiment type: Surface marker disruption assay in MOLM13 cells
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--input_dir ./examples/260103_MOLM13_MarkerDisruption/data/260103_MOLM13_MarkerDisruption_day7_rep1 \
--input_gml ./gating_strategies/default_gates_ZE5_MOLM13.gml \
--flowcytometer ZE5 \
--color_live LDAqua- \
--color_quant APC- \
--ctrl_key Mock \
--thresh_ratio 0.95

poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--input_dir ./examples/260103_MOLM13_MarkerDisruption/data/260104_MOLM13_MarkerDisruption_day7_rep2 \
--input_gml ./gating_strategies/default_gates_ZE5_MOLM13.gml \
--flowcytometer ZE5 \
--color_live LDAqua- \
--color_quant APC- \
--ctrl_key Mock \
--thresh_ratio 0.95

# Experiment type: Surface marker disruption assay in lentivirally transduced MOLM13 cells
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

poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--input_dir ./examples/260104_MOLM13_LentiMarkerDisruption/data/260105_MOLM13_LentiMarkerDisruption_day7_rep2 \
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

# Experiment type: mCherry transfection assay in HEK293T mCherry reporter cells
poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--input_dir ./examples/260106_HEK293T_mCherry/data/260106_HEK293T_mCherry_day3_rep1 \
--input_gml ./gating_strategies/default_gates_CytoFlex_HEK293T.gml \
--flowcytometer CytoFlex \
--color_quant mCherry+ \
--ctrl_key Mock \
--thresh_ratio 0.99

poetry run python .claude/skills/fcsprocess/scripts/fcs_main.py \
--input_dir ./examples/260106_HEK293T_mCherry/data/260107_HEK293T_mCherry_day3_rep2 \
--input_gml ./gating_strategies/default_gates_CytoFlex_HEK293T.gml \
--flowcytometer CytoFlex \
--color_quant mCherry+ \
--ctrl_key Mock \
--thresh_ratio 0.99