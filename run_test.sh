#!/bin/zsh

poetry run python .claude/skills/quant_fluor50/scripts/quant_fluor50_main.py \
--input_dir ./examples/260105_HEK293T_GFPDisruption/ \
--flowcytometer CytoFlex \
--color_marker mCherry-A \
--color_50 GFP-A