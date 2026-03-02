"""
quant_fluor50: Experiment-specific analysis protocol for quantifying marker fluorescence level to achieve 50% disruption/generation of color_quant
"""
# python default
import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path
# thirdparty
import pandas as pd
# local
import fcs_utils.primary_gates as primary_gates
from fcs_utils.fluor50 import compute_fluor50

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def main(args):
    """Main entry point for quant_fluor50 analysis."""
    # Path settings
    if args.output_dir is None:
        args.output_dir = args.input_dir / Path("output_fluor50")
    if not args.output_dir.exists():
        os.makedirs(args.output_dir)

    # Set up file handler for logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = args.output_dir / Path(f"quant_fluor50_{timestamp}.log")
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logging.getLogger().addHandler(file_handler)

    logger.info(f"Starting quant_fluor50 analysis")
    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Output directory: {args.output_dir}")

    # Read color/channel mapping
    df_color = pd.read_csv(args.color_csv)
    dict_color = df_color.set_index("Info")[args.flowcytometer].to_dict()
    max_bit = dict_color["max_bit"].strip("bit")
    max_val = 2 ** int(max_bit) - 1

    # Get channel names from fluorophore names
    color_marker_channel = dict_color.get(args.color_marker, args.color_marker)
    color_50_channel = dict_color.get(args.color_50, args.color_50)
    logger.info(f"Marker channel: {args.color_marker} -> {color_marker_channel}")
    logger.info(f"Target channel: {args.color_50} -> {color_50_channel}")

    # Process each data directory
    all_results = []
    search_dir = args.input_dir / Path("data")
    for data_dir in sorted(os.listdir(search_dir)):
        if data_dir.startswith(".") or not (search_dir / Path(data_dir)).is_dir():
            continue

        input_data_path = search_dir / Path(data_dir)
        input_gml = args.input_dir / Path("output") / Path(data_dir) / Path("gating_strategy.gml")

        # Check if gating strategy exists
        if not input_gml.exists():
            logger.warning(f"Gating strategy not found: {input_gml}. Skipping {data_dir}.")
            continue

        logger.info(f"Processing {input_data_path}...")
        
        session = primary_gates.init_session(input_data_path, input_gml, max_val=max_val)

        # Compute fluor50 for this dataset
        df_result = compute_fluor50(
            session=session,
            color_marker=color_marker_channel,
            color_50=color_50_channel,
            output_dir=args.output_dir,
            input_data_path=input_data_path,
            window_size=args.window_size,
            savefig=True,
            verbose=args.verbose,
        )
        df_result["data_dir"] = data_dir
        all_results.append(df_result)

    # Aggregate all results
    if all_results:
        df_all = pd.concat(all_results, axis=0, ignore_index=True)
        output_csv = args.output_dir / f"fluor50_summary.csv"
        df_all.to_csv(output_csv, index=False)
        logger.info(f"Saved aggregated results to {output_csv}")

        # Print summary statistics
        logger.info(f"=== Fluor50 Summary ===")
        logger.info(f"Total samples processed: {len(df_all)}")
        logger.info(f"Mean Fluor50: {df_all['fluor50_raw'].mean():.4f}")
        logger.info(f"Std Fluor50: {df_all['fluor50_raw'].std():.4f}")
    else:
        logger.warning("No results to aggregate.")

    logger.info("Analysis complete.")

    # Save arguments to output directory
    args_path = args.output_dir / f"args_{timestamp}.json"
    args_dict = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}
    with open(args_path, "w") as f:
        json.dump(args_dict, f, indent=2)
    logger.info(f"Arguments saved to {args_path}")
    logger.info(f"Logs saved to {log_path}")

    # Remove file handler
    logging.getLogger().removeHandler(file_handler)
    file_handler.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="quant_fluor50: Experiment-specific fluorescence quantification protocol"
    )
    parser.add_argument(
        "--input_dir",
        type=Path,
        required=True,
        help="Path to input experiment directory containing data subdirectories"
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        required=False,
        default=None,
        help="Path to output directory. By default, creates 'output_fluor50' under input_dir."
    )
    parser.add_argument(
        "--color_csv",
        type=Path,
        required=False,
        default="./color_info.csv",
        help="Path to the .csv file containing fluorophore-to-channel mapping."
    )
    parser.add_argument(
        "--flowcytometer",
        type=str,
        required=False,
        default="CytoFlex",
        help="Flowcytometer type for channel mapping (default: CytoFlex)."
    )
    parser.add_argument(
        "--color_marker",
        type=str,
        required=True,
        help="Fluorophore name for marker channel. EC50-like Fluor50 value is calculated for this channel."
    )
    parser.add_argument(
        "--color_50",
        type=str,
        required=True,
        help="Fluorophore name for target channel to determine 50%% disruption/generation."
    )
    parser.add_argument(
        "--window_size",
        type=int,
        required=False,
        default=100,
        help="Sliding window size for calculating target ratio (default: 100)."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output and diagnostic plots."
    )

    args = parser.parse_args()
    logger.info(f"Arguments: {args}")
    main(args)
