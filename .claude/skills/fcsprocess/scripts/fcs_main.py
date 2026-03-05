import argparse
import json
import logging
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
# Thirdparty
import flowkit as fk
import numpy as np
import pandas as pd
# Local
import fcs_utils.process_id as process_id
import fcs_utils.primary_gates as primary_gates
import fcs_utils.secondary_gates as secondary_gates
import fcs_utils.visualization as visualization
import fcs_utils.utils_functions as utils

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

import warnings
warnings.filterwarnings('ignore')

def process_single_dir(args, input_dir, output_dir):
    """Process a single directory containing .fcs files."""
    # Path settings
    if not output_dir.exists():
        os.makedirs(output_dir)
    fig_path = output_dir / Path("figures")
    if not fig_path.exists():
        os.makedirs(fig_path)
    try:
        assert args.flowcytometer in str(args.input_gml)
    except:
        raise ValueError(f"Found conflict between {args.flowcytometer} and {args.input_gml}")


    # Set up file handler for logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = output_dir / Path(f"fcsprocess_{timestamp}.log")
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logging.getLogger().addHandler(file_handler)

    # Initialize settings
    df_color = pd.read_csv(args.color_csv)
    dict_color = df_color.set_index("Info")[args.flowcytometer].to_dict()
    max_bit = dict_color["max_bit"].strip("bit")
    max_val = 2**int(max_bit)-1
    mypalette = process_id.setup_fcsprocess(input_dir, dict_color)
    logger.info(f"Initializing the gating strategy with {args.input_gml}")
    session = primary_gates.init_session(input_dir, args.input_gml, max_val=max_val)
    
    # Set up primary gates (TimeQC -> Viable -> Singlets)
    logger.info(f"Optimizing the time gate based on event rates within each sample...")
    if args.turnoff_timeqc:
        primary_gates.setup_time_gate(
            session,
            thresh_leftside = False,
            thresh_rightside = False,
        )
    else:
        primary_gates.setup_time_gate(session)
    logger.info(f"Optimizing the singlet identification using all samples...")
    primary_gates.setup_viable_gate(session, verbose=args.verbose, fig_dir=fig_path)
    primary_gates.setup_singlet_gate(session)

    # Set up live/dead gating if stained.
    if args.color_live is not None:
        logger.info(f"Optimizing the stained live/dead gate using all samples...")
        last_gate = secondary_gates.setup_rectangle_gate(
            session,
            dict_color,
            fluor_key = args.color_live,
            gate_name = "Live",
            parent_gate = "Singlets",
            gate_for_thresh = "Singlets",
            sample_id_list = session.get_sample_ids(),
            thresh_ratio = 0.995,
            mode = "range",
            init_n_components = 2   # Always assume some dead cells
        )
        gate_thresh = last_gate
    else:
        last_gate = "Singlets"
        gate_thresh = "Singlets"

    # Extract ids for control samples
    ctrl_id_list = []
    for sample_id in session.get_sample_ids():
        if args.ctrl_key in sample_id:
            ctrl_id_list.append(sample_id)
    logger.info(f"Detected control samples: {ctrl_id_list}")
    
    # Set up experiment-specific secondary gates
    if args.color_marker is not None:
        logger.info(f"Setting up marker gates {args.color_marker} using all samples...")
        last_gate = secondary_gates.setup_marker_gates(
            session,
            dict_color,
            fluor_keys = args.color_marker,
            parent_gate = last_gate,
            sample_id_list = ctrl_id_list,
            thresh_ratio = args.marker_thresh,
            marker_mode = args.marker_mode,
            marker_n_components = args.marker_n_components
        )

    # Set up gates for quantification (either rectangle or quandrant).
    logger.info(f"Setting up quantification gates {args.color_quant} using control samples...")
    last_gate = secondary_gates.setup_quant_gates(
        session,
        dict_color,
        fluor_keys = args.color_quant,
        parent_gate = last_gate,
        gate_for_thresh = gate_thresh,
        sample_id_list = ctrl_id_list,
        thresh_ratio = args.quant_thresh,
        n_components = args.quant_n_components,
        verbose = args.verbose,
        fig_dir = fig_path,
    )
    gs_path = Path(output_dir) / "gating_strategy.gml"
    with open(gs_path, "wb") as fh:
        fk.export_gatingml(session.gating_strategy, fh)
    # flowkit==1.3.0 cannot output GatingML 2.0 compliant format. Convert and overwrite it manually.
    # conv_path = Path(output_dir) / "gating_strategy_standard.gml"
    utils.convert_gml_to_standard(gs_path, gs_path)
    logger.info(f"Finished setting up gates. Gating strategy is saved to {gs_path}.")


    # Process all samples
    logger.info(f"Processing samples and visualizing results...")
    visualization.process_data(
        session,
        fig_dir = Path(output_dir) / Path("figures"),
        output_dir = output_dir,
        max_val = max_val,
        savefig = True,
        verbose = args.verbose,
        vis_mode = args.vis_mode
    )

    # Save arguments to output directory
    args_path = output_dir / f"args_{timestamp}.json"
    args_dict = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}
    args_dict["input_dir"] = str(input_dir)  # Add the actual input_dir used
    args_dict["output_dir"] = str(output_dir)  # Add the actual output_dir used
    with open(args_path, "w") as f:
        json.dump(args_dict, f, indent=2)
    logger.info(f"Arguments saved to {args_path}")
    logger.info(f"Logs saved to {log_path}")

    # Remove file handler
    logging.getLogger().removeHandler(file_handler)
    file_handler.close()


def main(args):
    """Main entry point that processes all data directories under experiment_dir/data/."""
    experiment_dir = args.experiment_dir
    data_dir = experiment_dir / "data"

    if not data_dir.exists():
        raise ValueError(f"Data directory not found: {data_dir}")

    # Find all subdirectories under data/
    data_subdirs = [d for d in data_dir.iterdir() if d.is_dir()]

    if not data_subdirs:
        raise ValueError(f"No subdirectories found under {data_dir}")

    logger.info(f"Found {len(data_subdirs)} data directories to process: {[d.name for d in data_subdirs]}")

    # Process each data directory
    for input_dir in sorted(data_subdirs):
        # Check if directory contains .fcs files
        fcs_files = list(input_dir.glob("*.fcs"))
        if not fcs_files:
            logger.warning(f"Skipping {input_dir.name}: no .fcs files found")
            continue

        logger.info(f"Processing {input_dir.name} ({len(fcs_files)} .fcs files)...")

        # Set output directory
        output_dir = experiment_dir / "output" / input_dir.name

        try:
            process_single_dir(args, input_dir, output_dir)
            logger.info(f"Successfully processed {input_dir.name}")
        except Exception as e:
            logger.error(f"Failed to process {input_dir.name}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            continue

    logger.info("All directories processed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment_dir", type=Path, required=True,
                        help="Path to experiment directory. The script will automatically find and process all directories under 'experiment_dir/data/'."
    )
    parser.add_argument("--input_gml", type=Path, required=True,
                        help="Path to an input gml file to specify gating strategy to start with for cell/single identifications with FSC/SSC plots."
    )
    parser.add_argument("--color_csv", type=Path, required=False, default="./color_info.csv",
                        help="Path to the .csv file containing the information of fluorophores and channels for flowcytometers."
    )
    parser.add_argument("--flowcytometer", type=str, required=False, default="CytoFlex",
                        help="Type of flowcytometer used to collect the input .fcs data. Used to map colors to channel names within the .csv file passed with --color_csv."
    )

    # Turn-off time gates
    parser.add_argument("--turnoff_timeqc", action="store_true",
                        help="Turn off time QC gate (threshold for everything)."
    )
    # Verbose mode for diagnosis
    parser.add_argument("--verbose", action="store_true",
                        help="Verbose output + figures for diagnosis."
    )
    
    # Arguments for fluorescent channels
    parser.add_argument("--ctrl_key", type=str, required=False, default="Mock",
                        help="Key to indicate control samples. fcs files containing this key in the filename will be used for determining thresholds for --color_marker and --color_quant."
    )
    parser.add_argument("--color_live", type=str, required=False, default=None,
                        help="Name of fluorophore for stained live/dead cells with +/- to indicate direction to select (default: None, example: LDAqua-)."
    )
    parser.add_argument("--color_marker", type=str, required=False, default=None,
                        help="Keys of additional fluorescent markers to identify populations to be quantified. Up to two markers can be used with a slash separation (default: None, example: mCherry+/GFP-)."
    )
    parser.add_argument("--marker_n_components", type=int, required=False, default=2,
                        help="Number of mixture model components for marker detection (default: 2 i.e. bimodal distribution). Set it to 1 if the control sample is unimodal."
    )
    parser.add_argument("--marker_mode", type=str, required=False, default="single",
                        help="Mode key for marker direction. Either sinlge or single_reverse is accepted."
    )
    parser.add_argument("--marker_thresh", type=float, required=False, default=0.95,
                        help="Threshold ratio for marker gate detection (default: 0.95). Used with --color_marker to define population boundaries."
    )
    parser.add_argument("--color_quant", type=str, required=True,
                        help="Keys of fluorescent channels used for quantification. Up to three markers can be used with a slash separation (example: mCherry+/APC-)."
    )
    parser.add_argument("--quant_thresh", type=float, required=False, default=0.98,
                        help="Threshold ratio for quantification gate detection (default: 0.98). Used with --color_quant to define quantification boundaries."
    )
    parser.add_argument("--quant_n_components", type=int, required=False, default=1,
                        help="Number of mixture model components for quantification gate detection (default: 1 i.e. unimodal distribution). Set it to 2 for bimodal distributions."
    )
    parser.add_argument("--vis_mode", type=str, required=False, default="default",
                        help="Mode key to define visualization for the quantified population. Only relevant for single-color quantification. default: Quant vs SSC-A. last: Quant vs last x-axis.")

    # Arguments for 
    args = parser.parse_args()
    logger.info(f"Arguments used:\n{args}")
    main(args)