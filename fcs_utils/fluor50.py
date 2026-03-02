import logging
import os
import re
from copy import deepcopy
from pathlib import Path
# Thirdparty
import flowkit as fk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.optimize import curve_fit
from sklearn.linear_model import TheilSenRegressor
# local
from fcs_utils.visualization import get_parent_membership, draw_gate, draw_fig_verbose

logger = logging.getLogger(__name__)

COLOR_BG = "#C0C0C0"
COLOR_POS = "#6495ED"
COLOR_THRESH = "#696969"
SUBPLOT_W = 6
SUBPLOT_H = 4
FONTSIZE_TICK = 11
FONTSIZE_LABEL = 13
FONTSIZE_TITLE = 15
FIG_DPI = 300


def sigmoid(x, y_min, y_max, k, x0):
    """
    Sigmoid function for EC50-like curve fitting.

    Output is constrained to [y_min, y_max] by parameterization.

    Args:
        x: Input values
        y_min: Minimum value (bottom plateau)
        y_max: Maximum value (top plateau)
        k: Steepness of the curve (positive = increasing, negative = decreasing)
        x0: x value at the midpoint (EC50)

    Returns:
        Sigmoid values in range [y_min, y_max]
    """
    return y_min + (y_max - y_min) / (1 + np.exp(-k * (x - x0)))


def fit_sigmoid_and_get_ec50(x_data, y_data, target_ratio=0.5):
    """
    Fit a sigmoid curve to data and find x value at target ratio.

    Args:
        x_data: x values (marker fluorescence)
        y_data: y values (target ratio, 0-1)
        target_ratio: Target ratio to find x value for (default 0.5)

    Returns:
        fitted_y: Fitted y values
        ec50: x value where y = target_ratio
        popt: Optimal parameters (y_min, y_max, k, x0)
    """
    # Initial parameter guesses
    y_min_init = np.min(y_data)
    y_max_init = np.max(y_data)
    x0_init = np.median(x_data)
    k_init = 1.0 if y_data.iloc[-1] > y_data.iloc[0] else -1.0  # Determine direction

    # Bounds for parameters: y_min and y_max constrained to [0, 1]
    bounds = (
        [0.0, 0.0, -10, np.min(x_data)],   # Lower bounds: y_min, y_max, k, x0
        [1.0, 1.0, 10, np.max(x_data)]      # Upper bounds: y_min, y_max, k, x0
    )

    try:
        popt, _ = curve_fit(
            sigmoid,
            x_data,
            y_data,
            p0=[y_min_init, y_max_init, k_init, x0_init],
            bounds=bounds,
            maxfev=5000
        )
        fitted_y = sigmoid(x_data, *popt)

        # Calculate EC50 (x value where y = target_ratio)
        y_min, y_max, k, x0 = popt
        # Solve: target_ratio = y_min + (y_max - y_min) / (1 + exp(-k * (x - x0)))
        # (target_ratio - y_min) / (y_max - y_min) = 1 / (1 + exp(-k * (x - x0)))
        # (y_max - y_min) / (target_ratio - y_min) = 1 + exp(-k * (x - x0))
        # (y_max - y_min) / (target_ratio - y_min) - 1 = exp(-k * (x - x0))
        L = y_max - y_min
        if (target_ratio - y_min) > 0 and (target_ratio - y_min) < L:
            ec50 = x0 - np.log(L / (target_ratio - y_min) - 1) / k
        else:
            ec50 = np.nan

    except (RuntimeError, ValueError) as e:
        logger.warning(f"Sigmoid fitting failed: {e}. Using linear interpolation.")
        fitted_y = y_data.copy()
        # Fallback: linear interpolation to find EC50
        idx = np.argmin(np.abs(y_data - target_ratio))
        ec50 = x_data.iloc[idx]
        popt = None

    return fitted_y, ec50, popt


def extract_day_rep(input_data_dir):
    """
    Extract day and rep information from input_data_dir.

    Args:
        input_data_dir: Sample identifier string

    Returns:
        day: Day number (int or None)
        rep: Replicate number (int or None)
    """
    # Match patterns like "day3", "Day3", "d3", "D3"
    day_match = re.search(r'[Dd]ay?(\d+)', input_data_dir)
    day = int(day_match.group(1)) if day_match else None
    print(input_data_dir)

    # Match patterns like "rep1", "Rep1", "r1", "R1"
    rep_match = re.search(r'[Rr]ep?(\d+)', input_data_dir)
    rep = int(rep_match.group(1)) if rep_match else None

    return day, rep


def compute_fluor50(
    session: fk.Session,
    color_marker: str,
    color_50: str,
    output_dir: Path,
    input_data_path: Path,
    target_name: str = "Target Ratio",
    window_size: int = 100,
    savefig: bool = True,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Compute the fluorescence level (Fluor50) at which 50% of cells are in the target population.

    This function performs EC50-like analysis by:
    1. Sorting cells by marker fluorescence intensity
    2. Calculating a sliding window ratio of target-positive cells
    3. Fitting a sigmoid curve to the ratio vs. marker intensity
    4. Finding the marker intensity at 50% target ratio

    Args:
        session: FlowKit Session with gating strategy applied
        color_marker: Channel name for marker (x-axis, used for EC50 calculation)
        color_50: Channel name for target population (used in gating)
        output_dir: Directory to save output files
        input_data_path: Path to input data (used for naming output files)
        target_name: Label for target ratio in plots (default: "Target Ratio")
        window_size: Number of cells in sliding window for ratio calculation (default: 100)
        savefig: Whether to save the figure (default: True)
        verbose: Enable verbose output (default: False)

    Returns:
        DataFrame with columns: Sample, day, rep, num_events, fluor50
    """
    # Create output directories if they don't exist
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    fig = plt.figure(
        figsize=(8,6),
        facecolor=(0,0,0,0)
    )
    ax = fig.subplots(nrows=1, ncols=1)

    # Extract day and rep from sample_id
    day, rep = extract_day_rep(input_data_path.name)
    
    gs = session.gating_strategy
    df_data = pd.DataFrame([],columns=["Sample","day","rep","num_events","fluor50"])
    for sample_id in session.get_sample_ids():
        logger.info(f"Processing {sample_id}...")
        # Gate samples
        sample = session.get_sample(sample_id)
        gated_sample = gs.gate_sample(sample)
        gate_data = pd.DataFrame(gated_sample.report)
        num_vis = np.max(gate_data["level"])

        # Retrieve channel information
        x_idx, y_idx = sample.get_channel_index(color_marker), sample.get_channel_index(color_50)
        marker_transform = session.get_transform(color_marker)

        # Retrieve gate information
        tmp_df = gate_data[gate_data["level"]==num_vis]
        sample_id, gate_path, gate_name, gate_type, quad, parent, _, _, rel_perc, _= tmp_df.values[0]
        
        # Retrieve events to analyze
        gate_membership = gated_sample._raw_results[(gate_name, "/".join(gate_path))]["events"]
        n_total = len(gate_membership)
        parent_membership = get_parent_membership(gate_path, parent, n_total, gated_sample)
        events = sample.get_events(source="xform",)
        df_events = pd.DataFrame(events[:,[x_idx,y_idx]], columns=[color_marker,color_50])
        df_events["Marker"] = parent_membership
        df_events["Target"] = gate_membership

        # Extract marker gated events
        df_events = df_events[df_events["Marker"]==True].drop("Marker", axis=1)
        df_events = df_events.sort_values(by=color_marker, ascending=True).reset_index(drop=True)
        logger.info(f"\tDetected number of events: {len(df_events)}")
        try:
            assert len(df_events) > window_size
        except:
            logger.info(f"Number of gated events for {sample_id} is smaller than window_size {window_size}. Maybe a control sample?")
            continue
        
        # Calculate target ratio around each event point
        target_ratio = np.zeros(len(df_events))
        for i in range(len(df_events)):
            min_idx, max_idx = i - int(window_size/2), i + int(window_size/2)
            if min_idx < 0:
                min_idx = 0
                max_idx = min_idx + window_size
            elif max_idx > len(df_events):
                max_idx = len(df_events)
                min_idx = max_idx - window_size
            tmp_df = df_events.iloc[min_idx:max_idx,:]
            tmp_target_ratio = np.sum(tmp_df["Target"])/len(tmp_df)
            target_ratio[i] = tmp_target_ratio
        df_events[target_name] = target_ratio

        # EC50-like value estimation using sigmoid curve fitting
        fitted_y, fluor50, popt = fit_sigmoid_and_get_ec50(
            df_events[color_marker],
            df_events[target_name],
            target_ratio=0.5
        )
        df_events["Fitted"] = fitted_y
        logger.info(f"\tFluor50 value: {fluor50:.4f}" if not np.isnan(fluor50) else "\tFluor50: Could not determine")

        # Draw fitted curve
        sns.lineplot(data=df_events, x=color_marker, y="Fitted", ax=ax, label=sample_id)

        # Add horizontal line at 50%
        ax.axhline(y=0.5, color=COLOR_THRESH, linestyle='--', alpha=0.5)

        fluor50_raw = marker_transform.inverse(np.array(fluor50).reshape(-1,1)).flatten()[0]
        new_row = pd.DataFrame(
            [[sample_id, day, rep, len(df_events), fluor50, fluor50_raw]],
            columns=["Sample", "day", "rep", "num_events", "fluor50", "fluor50_raw"]
        )
        df_data = pd.concat([df_data, new_row], axis=0, ignore_index=True)
    
    # Finalize figure
    ax.set_xlabel(f"{color_marker} (transformed)", fontsize=FONTSIZE_LABEL)
    ax.set_ylabel(f"{target_name}", fontsize=FONTSIZE_LABEL)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc='best', fontsize=FONTSIZE_TICK - 2)
    ax.set_title(f"Fluor50 Analysis: {color_50}", fontsize=FONTSIZE_TITLE)

    # Save figure
    plt.tight_layout()
    if savefig:
        figfile = str(input_data_path.name) + "_fluor50.png"
        fig.savefig(output_dir / Path(figfile), dpi=FIG_DPI)
    plt.close(fig)

    # Save data
    # csv_file = str(input_data_path.name) + "_fluor50.csv"
    # df_data.to_csv(output_dir / Path(csv_file), index=False)
    # logger.info(f"Saved results to {output_dir / Path(csv_file)}")

    return df_data