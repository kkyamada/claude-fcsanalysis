"""
FCS Plot - Visualization script for FCS analysis summary data.

This script generates various plots from summary_processed.csv files
with configurable styling via plot_config.yaml.

Usage examples:
    # Bar plot for mCherry- gate
    python fcs_plot.py --experiment_dir path/to/exp --plot_type bar --gate_name "mCherry-"

    # Dose response with symlog scale
    python fcs_plot.py --experiment_dir path/to/exp --plot_type line --gate_name "GFP+" --x_scale symlog

    # Bar plot with custom x-axis and hue
    python fcs_plot.py --experiment_dir path/to/exp --plot_type bar --gate_name "mCherry+" --x_col condition --hue cell_type
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

# Local imports
import fcs_utils.plot_config as plot_config
import fcs_utils.plot_utils as plot_utils

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def load_summary_data(experiment_dir: Path) -> pd.DataFrame:
    """
    Load and combine all summary_processed.csv files from experiment output directories.

    Args:
        experiment_dir: Path to experiment directory

    Returns:
        Combined DataFrame with all summary data
    """
    output_dir = experiment_dir / "output"
    if not output_dir.exists():
        raise ValueError(f"Output directory not found: {output_dir}")

    csv_files = list(output_dir.glob("*/summary_processed.csv"))
    if not csv_files:
        raise ValueError(f"No summary_processed.csv files found in {output_dir}")

    logger.info(f"Found {len(csv_files)} summary files")

    dfs = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        # Add source directory info
        df["data_dir"] = csv_file.parent.name
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    logger.info(f"Loaded {len(combined)} total records")

    return combined


def plot_gate_comparison(
    df: pd.DataFrame,
    gate_name: str,
    config: dict,
    output_dir: Path,
    x_col: str = "treatment",
    hue: str = "cell_type",
    value_col: str = "relative_percent",
    ylabel: Optional[str] = None,
    output_name: Optional[str] = None,
) -> None:
    """
    Create bar plot comparing gate percentages across conditions.

    Args:
        df: Summary DataFrame
        gate_name: Gate to plot (e.g., "mCherry+")
        config: Plot configuration
        output_dir: Output directory for figures
        x_col: Column for x-axis ("treatment", "condition", "cell_type")
        hue: Column for color grouping
        value_col: Value column to plot
        ylabel: Custom y-axis label
        output_name: Custom output filename
    """
    # Prepare data
    df_plot = plot_utils.prepare_summary_data(df, gate_name, value_col)
    if df_plot.empty:
        return

    # Create condition column if needed
    if x_col == "condition" and "condition" not in df_plot.columns:
        df_plot["condition"] = df_plot["treatment"] + " (" + df_plot["concentration"] + ")"

    # Create figure
    figsize = plot_config.get_config_value(config, "figure", "figsize_single", default=[6, 4])
    fig, ax = plt.subplots(figsize=figsize)

    # Determine hue - only use if multiple values exist
    hue_col = hue if hue in df_plot.columns and df_plot[hue].nunique() > 1 else None

    # Create bar plot
    plot_utils.plot_bar(
        df_plot,
        x=x_col,
        y="value",
        hue=hue_col,
        ax=ax,
        config=config,
        xlabel=x_col.replace("_", " ").title(),
        ylabel=ylabel or f"{gate_name} (%)",
    )

    # Save
    if output_name:
        output_path = output_dir / f"{output_name}.png"
    else:
        output_path = output_dir / f"bar_plot.png"
    plot_utils.save_figure(fig, output_path, config)
    plt.close(fig)
    print(f"Saved bar plot to {output_path}")


def plot_concentration_response(
    df: pd.DataFrame,
    gate_name: str,
    config: dict,
    output_dir: Path,
    hue: str = "cell_type",
    value_col: str = "relative_percent",
    x_scale: str = "linear",
    x_lim: Optional[list] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    output_name: Optional[str] = None,
) -> None:
    """
    Create line plot showing response across concentrations.

    Args:
        df: Summary DataFrame
        gate_name: Gate to plot
        config: Plot configuration
        output_dir: Output directory
        hue: Column to color lines by
        value_col: Value column to plot
        x_scale: X-axis scale ("linear" or "symlog")
        x_lim: X-axis limits as [min, max]
        xlabel: Custom x-axis label
        ylabel: Custom y-axis label
        output_name: Custom output filename
    """
    # Prepare data
    df_plot = plot_utils.prepare_summary_data(df, gate_name, value_col)
    if df_plot.empty:
        return

    # Need concentration values
    if df_plot["conc_value"].nunique() < 2:
        logger.info(f"Skipping concentration response plot for {gate_name}: insufficient concentration levels")
        return

    # Create figure
    figsize = plot_config.get_config_value(config, "figure", "figsize_single", default=[6, 4])
    fig, ax = plt.subplots(figsize=figsize)

    # Create line plot
    plot_utils.plot_line(
        df_plot,
        x="conc_value",
        y="value",
        hue=hue if df_plot[hue].nunique() > 1 else None,
        ax=ax,
        config=config,
        title=f"{gate_name} Concentration Response",
        xlabel=xlabel or "Concentration",
        ylabel=ylabel or f"{gate_name} (%)",
    )

    # Apply x-axis scale
    if x_scale == "symlog":
        ax.set_xscale("symlog", linthresh=1)

    # Apply x-axis limits
    if x_lim:
        ax.set_xlim(x_lim[0], x_lim[1])

    # Save
    if output_name:
        output_path = output_dir / f"{output_name}.png"
    else:
        output_path = output_dir / f"line_plot.png"
    plot_utils.save_figure(fig, output_path, config)
    plt.close(fig)
    print(f"Saved line plot to {output_path}")


def plot_treatment_heatmap(
    df: pd.DataFrame,
    gate_name: str,
    config: dict,
    output_dir: Path,
    value_col: str = "relative_percent",
) -> None:
    """
    Create heatmap showing gate values across cell types and treatments.

    Args:
        df: Summary DataFrame
        gate_name: Gate to plot
        config: Plot configuration
        output_dir: Output directory
        value_col: Value column to plot
    """
    # Prepare data
    df_plot = plot_utils.prepare_summary_data(df, gate_name, value_col)
    if df_plot.empty:
        return

    # Need multiple cell types or treatments for heatmap
    if df_plot["cell_type"].nunique() < 2 or df_plot["treatment"].nunique() < 2:
        logger.info(f"Skipping heatmap for {gate_name}: insufficient dimensions")
        return

    # Pivot for heatmap
    pivot_df = df_plot.pivot_table(
        values="value",
        index="cell_type",
        columns="treatment",
        aggfunc="mean"
    )

    # Create figure
    figsize = plot_config.get_config_value(config, "figure", "figsize_single", default=[6, 4])
    fig, ax = plt.subplots(figsize=figsize)

    # Create heatmap
    plot_utils.plot_heatmap(
        pivot_df,
        ax=ax,
        config=config,
        title=f"{gate_name} Heatmap",
    )

    # Save
    output_path = output_dir / f"heatmap_{gate_name}.png"
    plot_utils.save_figure(fig, output_path, config)
    plt.close(fig)


def plot_multi_gate_comparison(
    df: pd.DataFrame,
    config: dict,
    output_dir: Path,
    value_col: str = "relative_percent",
) -> None:
    """
    Create multi-panel figure comparing all quantification gates.

    Args:
        df: Summary DataFrame
        config: Plot configuration
        output_dir: Output directory
        value_col: Value column to plot
    """
    # Find quantification gates (highest level)
    max_level = df["level"].max()
    quant_gates = df[df["level"] == max_level]["gate_name"].unique()

    if len(quant_gates) == 0:
        logger.warning("No quantification gates found")
        return

    # Prepare data for each gate
    data_list = []
    for gate_name in quant_gates:
        df_plot = plot_utils.prepare_summary_data(df, gate_name, value_col)
        if not df_plot.empty:
            kwargs = {
                "x": "treatment",
                "y": "value",
                "title": gate_name,
                "ylabel": f"{gate_name} (%)",
            }
            data_list.append((df_plot, kwargs))

    if not data_list:
        return

    # Create multi-panel figure
    fig = plot_utils.create_multi_panel(
        plot_utils.plot_bar,
        data_list,
        config=config,
        suptitle="Gate Comparison",
    )

    # Save
    output_path = output_dir / "multi_gate_comparison.png"
    plot_utils.save_figure(fig, output_path, config)
    plt.close(fig)


def main(args):
    """Main entry point for FCS plotting."""
    experiment_dir = args.experiment_dir

    # Set up output directory (default to experiment_dir, not plots/)
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = experiment_dir

    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    logger.info(f"Output directory: {output_dir}")

    # Load configuration (auto-generate if not exists)
    config_path = experiment_dir / "plot_config.yaml"
    config = plot_config.ensure_config_exists(config_path)
    if args.preset:
        config = plot_config.load_config(config_path=config_path, preset=args.preset)
    logger.info(f"Using style preset: {config.get('style', 'publication')}")

    # Generate default config if requested
    if args.generate_config:
        config_output = experiment_dir / "plot_config.yaml"
        with open(config_output, "w") as f:
            f.write(plot_config.generate_default_config_yaml())
        logger.info(f"Generated default config at {config_output}")
        return

    # Load data
    df = load_summary_data(experiment_dir)

    # Filter out excluded treatments if specified
    if args.exclude_treatments:
        # Parse sample IDs to get treatment for filtering
        treatments = df["sample_id"].apply(
            lambda x: plot_utils.parse_sample_id(x)["treatment"]
        )
        df = df[~treatments.isin(args.exclude_treatments)]
        logger.info(f"Excluded treatments: {args.exclude_treatments}")

    # Determine which gates to plot
    if args.gate_name:
        gate_names = [args.gate_name]
    else:
        # Use quantification gates (highest level)
        max_level = df["level"].max()
        gate_names = df[df["level"] == max_level]["gate_name"].unique().tolist()

    logger.info(f"Plotting gates: {gate_names}")

    # Generate plots
    for gate_name in gate_names:
        logger.info(f"Creating plots for {gate_name}...")

        if args.plot_type in ["all", "bar"]:
            plot_gate_comparison(
                df, gate_name, config, output_dir,
                x_col=args.x_col or "treatment",
                hue=args.hue,
                ylabel=args.ylabel,
                output_name=args.output_name,
            )

        if args.plot_type in ["all", "line"]:
            plot_concentration_response(
                df, gate_name, config, output_dir,
                hue=args.hue,
                x_scale=args.x_scale,
                x_lim=args.x_lim,
                xlabel=args.xlabel,
                ylabel=args.ylabel,
                output_name=args.output_name,
            )

        if args.plot_type in ["all", "heatmap"]:
            plot_treatment_heatmap(df, gate_name, config, output_dir)

    # Multi-panel comparison
    if args.plot_type in ["all", "multi"]:
        plot_multi_gate_comparison(df, config, output_dir)

    logger.info("Plotting complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate plots from FCS analysis summary data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Bar plot for specific gate
  python fcs_plot.py --experiment_dir path/to/exp --plot_type bar --gate_name "mCherry-"

  # Dose response curve with cell_type as hue
  python fcs_plot.py --experiment_dir path/to/exp --plot_type line --gate_name "mCherry+" --hue cell_type

  # Dose response with symlog x-scale (for wide concentration ranges)
  python fcs_plot.py --experiment_dir path/to/exp --plot_type line --gate_name "GFP+" --hue treatment --x_scale symlog

  # Bar plot with custom x-axis (condition = treatment + concentration)
  python fcs_plot.py --experiment_dir path/to/exp --plot_type bar --gate_name "GFP-" --x_col condition --hue cell_type
        """
    )
    parser.add_argument(
        "--experiment_dir",
        type=Path,
        required=True,
        help="Path to experiment directory containing output/ with summary_processed.csv files"
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=None,
        help="Output directory for plots (default: experiment_dir/)"
    )
    parser.add_argument(
        "--preset",
        type=str,
        choices=["publication", "exploratory", "presentation"],
        default=None,
        help="Style preset to use (overrides config file)"
    )
    parser.add_argument(
        "--plot_type",
        type=str,
        choices=["all", "bar", "line", "heatmap", "multi"],
        default="all",
        help="Type of plots to generate"
    )
    parser.add_argument(
        "--gate_name",
        type=str,
        default=None,
        help="Specific gate to plot (default: all quantification gates)"
    )
    parser.add_argument(
        "--x_col",
        type=str,
        choices=["treatment", "condition", "conc_value", "cell_type"],
        default=None,
        help="Column for x-axis. 'condition' = treatment + concentration. Default: treatment for bar, conc_value for line"
    )
    parser.add_argument(
        "--hue",
        type=str,
        choices=["cell_type", "treatment", "concentration"],
        default="cell_type",
        help="Column for color grouping (default: cell_type)"
    )
    parser.add_argument(
        "--x_scale",
        type=str,
        choices=["linear", "symlog"],
        default="linear",
        help="X-axis scale for line plots (default: linear). Use symlog for wide concentration ranges including 0"
    )
    parser.add_argument(
        "--x_lim",
        type=float,
        nargs=2,
        default=None,
        metavar=("MIN", "MAX"),
        help="X-axis limits (e.g., --x_lim -20 450)"
    )
    parser.add_argument(
        "--ylabel",
        type=str,
        default=None,
        help="Custom y-axis label (default: gate_name + %%)"
    )
    parser.add_argument(
        "--xlabel",
        type=str,
        default=None,
        help="Custom x-axis label (default: 'Concentration' for line plots)"
    )
    parser.add_argument(
        "--output_name",
        type=str,
        default=None,
        help="Custom output filename (without extension)"
    )
    parser.add_argument(
        "--generate_config",
        action="store_true",
        help="Generate a default plot_config.yaml in the experiment directory"
    )
    parser.add_argument(
        "--exclude_treatments",
        type=str,
        nargs="+",
        default=None,
        help="Treatments to exclude from plot (e.g., --exclude_treatments Mock Control)"
    )

    args = parser.parse_args()
    main(args)
