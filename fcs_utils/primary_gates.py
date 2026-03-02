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
from scipy.ndimage import gaussian_filter
from sklearn.linear_model import TheilSenRegressor
# local
from fcs_utils.visualization import get_parent_membership, draw_gate, draw_fig_verbose

logger = logging.getLogger(__name__)

def init_session(
    input_dir: Path,
    input_gml: Path,
    max_val: int = 262144,
) -> fk.Session:
    """
    Load samples and initialize the flow analysis session in flowkit.

    Args:
        input_dir: A path to the directory containing .fcs files to analyze.
        input_gml: A path to the gml file containing a gating strategy to start with (default: None).
        max_val: Max possible values within the fcs file. 262144 for regular 18-bit flowcytometer detectors.

    Returns:
        session: Loaded and initialized session.
    """
    if input_gml.suffix.lower() == ".gml":
        session = fk.Session(gating_strategy=str(input_gml), fcs_samples=input_dir)
    else:
        session = fk.Session(fcs_samples=input_dir)
    
    for tmp_file in os.listdir(input_dir):
        if "compensation" in tmp_file.lower():
            comp_path = input_dir / Path(tmp_file)
            df_comp = pd.read_csv(comp_path)
            detectors = list(df_comp.columns)

            comp_matrix = fk.Matrix(
                str(comp_path),
                detectors,
            )
        else:
            comp_matrix = None

    gs = session.gating_strategy
    
    # Renaming channel pnn_labels (e.g. FL-2) with labels from the flow machine (e.g. B525-A)
    for sample_id in session.get_sample_ids():
        sample = session.get_sample(sample_id)
        for pns_label, pnn_label in zip(sample.pns_labels, sample.pnn_labels):
            sample.rename_channel(pnn_label, pns_label)

    # Adding transformations to the gating strategy
    # For details, see https://github.com/whitews/FlowKit/blob/master/docs/notebooks/flowkit-tutorial-part02-transforms-module-matrix-class.ipynb
    existing_xform = gs.transformations
    for channel in sample.pnn_labels:
        if channel in existing_xform:
            continue
        
        if "FSC" in channel or "SSC" in channel:
            gs.add_transform(
                channel,
                fk.transforms.LogTransform(
                    param_t=max_val,
                    param_m=4.5,
                )
            )
        elif "time" in channel.lower():
            gs.add_transform(
                channel,
                fk.transforms.LinearTransform(
                    param_t=1,
                    param_a=0,
                )
            )
        elif "-A" in channel or "-W" in channel or "-H" in channel:
            gs.add_transform(
                channel,
                fk.transforms.LogicleTransform(
                    param_t=max_val,
                    param_w=0.5,
                    param_m=4.5,
                    param_a=0.5,
                )
            )
    
    # Apply transformations to samples
    for sample_id in session.get_sample_ids():
        sample = session.get_sample(sample_id)
        if comp_matrix is not None:
            sample.apply_compensation(comp_matrix)
        sample.apply_transform(session.get_transforms())

    return session

def setup_time_gate(
        session: fk.Session,
        gate_name: str = "TimeQC",
        parent_gate: str = "root",
        time_window: float = 0.5,
        thresh_leftside: bool = True,
        thresh_rightside: bool = False,
) -> None:
    """
    Optimize the per-sample rectangular gate on Time vs FSC-A plot using the overdispersion relative to Poisson noise as a measure.
    For more stringent quality control, additional implementations similar to flowAI (Monaco G., Bioinformatics, 2016) would be required.

    Args:
        session: A flowkit Session object with samples and gating strategy to optimize.
        gate_name: Name of the time gate to optimize (default: "TimeQC").
        parent_gate: Name of the parent gate to add the time gate (default: "root").
        time_window: Window size to measure event rates (default: 0.5 sec).
        thresh_leftside: Flag to turn on the left side thresholding i.e. at the beginning of flow sample collection (default: True).
        thresh_rightside: Flag to turn on the right side thresholding i.e. at the end of flow sample collection (default: False).

    Returns:
        None: Just updating the mutable fk.Session.
    """

    gs = session.gating_strategy
        
    # Get time channel data
    time_channel = None
    sample = session.get_sample(session.get_sample_ids()[0])
    for ch in sample.pnn_labels:
        if "time" in ch.lower():
            time_channel = ch
            break
    if time_channel is None:
        raise ValueError("No time channel found in sample")

    for sample_id in session.get_sample_ids():
        sample = session.get_sample(sample_id)
        t_start, t_end = _compute_time_bounds(
                            sample,
                            time_window,
                            thresh_leftside,
                            thresh_rightside,
                        )
        if t_end == -1:
            dim_t = fk.Dimension(
                time_channel,
                range_min=t_start,
            )
        elif t_start == 0:
            dim_t = fk.Dimension(
                time_channel,
                range_max=t_end,
            )

        # Adding per-sample TimeQC gate to the gating strategy
        custom_time_gate = fk.gates.RectangleGate(
            gate_name=gate_name,
            dimensions=[dim_t,],
        )
        
        gs.add_gate(custom_time_gate, gate_path=find_gate_path(gs, parent_gate), sample_id=sample_id)
    return

def setup_viable_gate(
        session: fk.Session,
        gate_name: str = "Viable",
        opt_scale: float = 0.15,
        opt_scale_rot: float = 0.05,
        n_step: int = 10,
        verbose: bool = False,
        fig_dir: Path = Path("")
) -> None:
    """
    Optimize the polygonal gate to extract viable cells on the FSC-A vs SSC-A plot in a grid search style.
    First optimize xy coordinates by altering the initial gate position for "opt_scale" relative to the gate scale.
    Subsequently, the rotation of the gate is optimized for "opt_scale" relative to pi.

    Args:
        session: A flowkit Session object with samples and gating strategy to optimize.
        gate_name: Name of the gate to extract viable cells to optimize (default: "Viable").
        opt_scale: The scale of optimization relative to the size of the gate for xy coordinates.
        opt_scale_rot: The scale of optimization relative to pi for rotation.
        n_step: Number of optimization steps per direction and rotation.
        verbose: Verbose mode

    Returns:
        None: Just updating the mutable fk.Session.
    """

    gs = session.gating_strategy
    gate = gs.get_gate(gate_name)

    for dimension in gate.dimensions:
        dimension.transformation_ref = dimension.id

    original_vertices = deepcopy(np.array(gate.vertices))
    if not isinstance(gate, fk.gates.PolygonGate):
        raise ValueError(f"Gate '{gate_name}' must be a PolygonGate, got {type(gate)}")
    
    # Get FSC-A and SSC-A channel data
    fsc_a_ch = None
    ssc_a_ch = None
    sample = session.get_sample(session.get_sample_ids()[0])
    for ch in sample.pnn_labels:
        if "SSC" in ch and "-A" in ch:
                ssc_a_ch = ch
        elif "FSC" in ch and "-A" in ch:
                fsc_a_ch = ch
    if fsc_a_ch is None or ssc_a_ch is None:
        raise ValueError("FSC-A and SSC-A channel could not be found in sample.")

    # Calculate gate scale from bounding box
    gate_width = original_vertices[:, 0].max() - original_vertices[:, 0].min()
    gate_height = original_vertices[:, 1].max() - original_vertices[:, 1].min()

    # Grid search steps
    xy_steps = np.linspace(-opt_scale, opt_scale, n_step)
    rotation_steps = np.linspace(-opt_scale_rot * np.pi, opt_scale_rot * np.pi, n_step)

    best_score = -np.inf
    best_vertices = original_vertices

    # Phase 1: Optimize xy position
    fig_count = 0
    best_fig_count = 0
    for dx_scale in xy_steps:
        for dy_scale in xy_steps:
            fig_count += 1
            dx = dx_scale * gate_width
            dy = dy_scale * gate_height
            shifted_vertices = _shift_polygon(original_vertices, dx, dy)
            gate.vertices = shifted_vertices

            # Score the gate
            scores = _score_gate(
                session, 
                gate_name, 
                x_channel=fsc_a_ch, 
                y_channel=ssc_a_ch
                )
            if verbose:
                sample_idx = 0
                fig_path = fig_dir / Path(f"tmpsinglets_opt{fig_count}_sample{sample_idx}.png")
                draw_fig_verbose(session, scores, fig_path, sample_idx)
            if scores[0] > best_score:
                best_score = scores[0]
                best_vertices = shifted_vertices
                best_fig_count = fig_count
    if verbose:
        logger.info(f"Best figure count: {best_fig_count}")


    # Restore best position from phase 1
    gate.vertices = best_vertices
    phase1_vertices = deepcopy(best_vertices)
    phase1_center = phase1_vertices.mean(axis=0)

    # Phase 2: Optimize rotation
    for angle in rotation_steps:
        rotated_vertices = _rotate_polygon(phase1_vertices, angle, phase1_center)
        gate.vertices = rotated_vertices

        scores = _score_gate(
            session, 
            gate_name, 
            x_channel=fsc_a_ch, 
            y_channel=ssc_a_ch
            )
        if scores[0] > best_score:
            best_score = scores[0]
            best_vertices = rotated_vertices

    # Set final optimized gate
    gate.vertices = best_vertices
    return

def setup_singlet_gate(
        session: fk.Session,
        gate_name: str = "Singlets",
        parent_gate: str = "Viable",
        thresh_ratio: float = 0.75,
) -> None:
    """
    Optimize the polygonal (parallelogram) gate to extract singlets on the SSC-A vs SSC-H plot.
    This function first finds the line traversing the singlet population by using Theil-Sen regression.
    The parallelogram region is formed around the line such that it covers the population around the line.

    Args:
        session: A flowkit Session object with samples and gating strategy to optimize.
        gate_name: Name of the gate to extract singlet cells to optimize (default: "Singlets").
        parent_gate: Name of the parent gate to add the singlet gate (default: "Viable").
        thresh_ratio: Ratio of population above the regression line to cover (default: 0.75).

    Returns:
        None: Just updating the mutable fk.Session.
    """
    gs = session.gating_strategy

    if not parent_gate in dict(gs.get_gate_ids()).keys():
        raise ValueError(f"{parent_gate} not found in the gating strategy.")
    if thresh_ratio <= 0.0 or thresh_ratio > 1.0:
        raise ValueError(f"The argument thresh_ratio must be a float value between 0 and 1")
    
    # Get SSC-A and SSC-H channel data
    ssc_a_ch = None
    ssc_h_ch = None
    sample = session.get_sample(session.get_sample_ids()[0])
    for ch in sample.pnn_labels:
        if "SSC" in ch:
            if "-A" in ch:
                ssc_a_ch = ch
            elif "-H" in ch:
                ssc_h_ch = ch
    if ssc_a_ch is None or ssc_h_ch is None:
        raise ValueError("SSC-A and SSC-H channel could not be found in sample.")
    idx_a = sample.get_channel_index(ssc_a_ch)
    idx_h = sample.get_channel_index(ssc_h_ch)
    
    # Compute the representative line traversing singlets across samples
    coeffs = []
    intercepts = []
    for sample_id in session.get_sample_ids():
        sample = session.get_sample(sample_id)
        gated_sample = gs.gate_sample(sample)
        gate_membership = gated_sample.get_gate_membership(parent_gate)
        events = sample.get_events(source='xform', event_mask=gate_membership)
        # Fitting a line with Theil-Sen regression
        estimator = TheilSenRegressor(random_state=42)
        estimator.fit(events[:, idx_a:idx_a+1], events[:, idx_h])
        coeffs.append(estimator.coef_[0])
        intercepts.append(estimator.intercept_)
    med_coeff, med_intercept = np.median(coeffs), np.median(intercepts)

    # Compute parallelogram regions around the line
    width_half = 0.0
    min_xy = np.inf
    max_xy = 0.0
    for sample_id in session.get_sample_ids():
        sample = session.get_sample(sample_id)
        gated_sample = gs.gate_sample(sample)
        gate_membership = gated_sample.get_gate_membership(parent_gate)
        events = sample.get_events(source='xform', event_mask=gate_membership)
        # Distance between points and the fitted line
        dist_events = med_coeff*events[:, idx_a] - events[:, idx_h] + med_intercept
        # 99% coverage above the line.
        dist_events = np.sort(dist_events[dist_events>0]).flatten()
        if len(dist_events)>0:
            idx_tmp = min(int(len(dist_events) * thresh_ratio), len(dist_events) - 1)    
        tmp_width = dist_events[idx_tmp]
        if tmp_width > width_half:
            width_half = tmp_width
        tmp_max = np.max(np.concatenate([events[:, idx_a], events[:, idx_h]]))
        tmp_min = np.min(np.concatenate([events[:, idx_a], events[:, idx_h]]))
        if tmp_max > max_xy:
            max_xy = tmp_max
        if tmp_min < min_xy:
            min_xy = tmp_min
    
    # Compute vertices
    unit_dist = np.sqrt(med_coeff**2+1)
    x_offset = med_coeff * width_half / unit_dist
    y_offset = width_half / unit_dist
    x1 = min_xy + x_offset
    x2 = min_xy - x_offset
    x3 = max_xy - x_offset
    x4 = max_xy + x_offset
    y1 = med_coeff * min_xy + med_intercept - y_offset
    y2 = med_coeff * min_xy + med_intercept + y_offset
    y3 = med_coeff * max_xy + med_intercept + y_offset
    y4 = med_coeff * max_xy + med_intercept - y_offset

    # Apply gating
    vertices = np.array([[x1, y1],[x2, y2],[x3, y3],[x4, y4]])
    
    dim_a = fk.Dimension(ssc_a_ch, transformation_ref=ssc_a_ch)
    dim_b = fk.Dimension(ssc_h_ch, transformation_ref=ssc_h_ch)
    polygate = fk.gates.PolygonGate(
        gate_name,
        dimensions=[dim_a, dim_b],
        vertices=vertices
    )
    if gate_name in dict(gs.get_gate_ids()).keys():
        gs.remove_gate(gate_name)
    gs.add_gate(polygate, gate_path=find_gate_path(gs, parent_gate))
    return

def find_gate_path(
        gs: fk.GatingStrategy,
        gate_name: str,
) -> tuple:
    """
    Find the path to the gate_name, within the given gating strategy.

    Args:
        gs: Gating strategy object to search for the gate.
        gate_name: A name of the gate to look for.

    Returns:
        gate_path: A tuple object to specify the path to the gate.

    Raises:
        ValueError: If the gate_name is not found in the gating strategy.
    """
    if gate_name == "root":
        return ("root",)
    # get_gate_ids() returns a list of tuples: (gate_name, gate_path)
    gate_ids = gs.get_gate_ids()

    for name, path in gate_ids:
        if name == gate_name:
            return path + (gate_name,)

    raise ValueError(f"Gate '{gate_name}' not found in the gating strategy.")

def _estimate_density_2d(
        sample: fk.Sample,
        gating_strategy: fk.GatingStrategy,
        gate_name: str,
        x_channel: str,
        y_channel: str,
        bins: int = 256,
        sigma: float = 3.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Estimate 2D density for gated events using a smoothed 2D histogram.

    Args:
        sample: A flowkit Sample object.
        gating_strategy: A flowkit GatingStrategy object.
        gate_name: Name of the gate to use for subsetting events.
        x_channel: Channel name for x-axis.
        y_channel: Channel name for y-axis.
        bins: Number of bins for the histogram (default: 256).
        sigma: Standard deviation for Gaussian smoothing (default: 3.0).

    Returns:
        A tuple of (density, x_edges, y_edges, event_densities):
            - density: 2D array of smoothed density values.
            - x_edges: Bin edges for x-axis.
            - y_edges: Bin edges for y-axis.
            - event_densities: Density value at each event's location.
    """
    gating_results = gating_strategy.gate_sample(sample)
    # Retrieving a 1D boolean array
    gate_membership = gating_results.get_gate_membership(gate_name)
    # Retrieving gated data with respective channels
    x_events = sample.get_channel_events(x_channel, source="xform", subsample=False)
    y_events = sample.get_channel_events(y_channel, source="xform", subsample=False)
    x_data = x_events[gate_membership]
    y_data = y_events[gate_membership]

    histogram, x_edges, y_edges = np.histogram2d(
        x_data, y_data, bins=bins
    )

    # 2D density estimation and normalization
    density = gaussian_filter(histogram, sigma=sigma)
    density = density / density.sum()

    # Map density values back to each event
    x_bin_indices = np.clip(
        np.digitize(x_data, x_edges) - 1, 0, bins - 1
    )
    y_bin_indices = np.clip(
        np.digitize(y_data, y_edges) - 1, 0, bins - 1
    )
    event_densities = density[x_bin_indices, y_bin_indices]

    return density, x_edges, y_edges, event_densities

def _score_gate(
        session: fk.Session,
        gate_name: str,
        x_channel: str,
        y_channel: str,
        penalty: float=0.5,
        center_penalty: float=10.0,
) -> tuple[float, float]:
    """
    Calculate gate scores for all samples in a session.
    The score is calculated as: event_count / gate_area.
    This provides a density-normalized measure of events within the gate.
    Additionally penalizes gates where the gate center is far from the data center.

    Args:
        session: A flowkit Session object with samples and gating strategy.
        gate_name: Name of the gate to score.
        penalty: Penalty parameter for the deviation across samples to ensure robustness (default: 0.5).
        center_penalty: Penalty parameter for distance between gate center and data center (default: 1.0).

    Returns:
        score: calculated score of the current gate with samples in the session
    """
    # Calculate density score per sample
    gs = session.gating_strategy
    # scores = []
    center_distances = []

    # Get gate center (geometric center of polygon vertices)
    gate = gs.get_gate(gate_name)
    gate_vertices = np.array(gate.vertices)
    gate_center = gate_vertices.mean(axis=0)

    # Calculate gate dimensions for normalizing distance
    gate_width = gate_vertices[:, 0].max() - gate_vertices[:, 0].min()
    gate_height = gate_vertices[:, 1].max() - gate_vertices[:, 1].min()
    gate_scale = np.sqrt(gate_width**2 + gate_height**2)

    for sample_id in session.get_sample_ids():
        sample = session.get_sample(sample_id)
        """
        _, _, _, event_densities = _estimate_density_2d(
            sample,
            gs,
            gate_name,
            x_channel,
            y_channel,
        )
        # Score = median events per unit area (density)
        scores.append(np.median(event_densities))
        """

        # Calculate distance between gate center and data median
        gating_results = gs.gate_sample(sample)
        gate_membership = gating_results.get_gate_membership(gate_name)
        x_events = sample.get_channel_events(x_channel, source="xform", subsample=False)
        y_events = sample.get_channel_events(y_channel, source="xform", subsample=False)
        x_data = x_events[gate_membership]
        y_data = y_events[gate_membership]

        if len(x_data) > 0:
            data_median = np.array([np.median(x_data), np.median(y_data)])
            # Normalized distance (relative to gate size)
            distance = np.linalg.norm(gate_center - data_median) / gate_scale
            center_distances.append(distance)

    """
    # Calculate a score across samples
    score_values = np.array(scores)
    iqr = np.percentile(score_values, 75) - np.percentile(score_values, 25)
    if iqr > 0:
        score_values /= iqr
    mad = np.median(np.abs(score_values - np.median(score_values)))
    density_score = np.median(score_values) - penalty*mad
    """

    # Calculate center distance penalty across samples
    if len(center_distances) > 0:
        center_distance_score = np.median(center_distances)
    else:
        center_distance_score = 1.0

    # Combined score: higher density is better, lower center distance is better
    # score = density_score - center_penalty * center_distance_score
    score = -center_distance_score

    return score, center_distance_score

def _rotate_polygon(vertices: np.ndarray, angle: float, center: np.ndarray) -> np.ndarray:
    """Rotate polygon vertices around a center point."""
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
    centered = vertices - center
    rotated = centered @ rotation_matrix.T
    return rotated + center

def _shift_polygon(vertices: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """Shift polygon vertices by dx, dy."""
    return vertices + np.array([dx, dy])

def _compute_time_bounds(
        sample: fk.Sample,
        time_window: float,
        thresh_leftside: bool,
        thresh_rightside: bool,
        stability_bins: int = 10,
        threshold: float = 0.3,
) -> tuple[float, float]:
    """
    Compute time boundaries per sample using Poisson-corrected CV as a stablity measure.
    Detects the longest consecutive region that are classified as stable.

    Args:
        sample: A flowkit Sample object.
        time_window: Window size in seconds to calculate event rates.
        thresh_leftside: Whether or not to cut off low-quality time points from the left side, i.e. at the beginning of flow sample collection.
        thresh_rightside: Whether or not to cut off low-quality time points from the right side, i.e. at the end of flow sample collection.
        stability_bins: Number of bins around the target bin to include for Poisson-corrected CV calculation.
        threshold: Highest Poisson-corrected CV threshold to consider the bin as stable (default: 0.3). The lower the more stable.

    Returns:
        Tuple of (t_start, t_end) representing stable acquisition boundaries.
    """

    # Get time channel data
    time_channel = None
    for ch in sample.pnn_labels:
        if "time" in ch.lower():
            time_channel = ch
            break

    if time_channel is None:
        raise ValueError("No time channel found in sample")

    time_data = sample.get_channel_events(time_channel, source="raw", subsample=False)
    time_min, time_max = time_data.min(), time_data.max()

    # Create time bins
    n_bins = max(1, int((time_max - time_min) / time_window))
    bin_edges = np.linspace(time_min, time_max, n_bins + 1)

    # Calculate event counts per bin
    event_counts, _ = np.histogram(time_data, bins=bin_edges)

    # Calculate the overdispersion relative to Poisson noise using centered sliding window
    # D = sqrt((variance - mean) / mean^2)
    # This subtracts the expected Poisson noise from the observed variance
    half_window = stability_bins // 2

    corrected_cvs = np.zeros(n_bins)
    for i in range(n_bins):
        # Center window around bin i, clamping at edges
        start_idx = max(0, i - half_window)
        end_idx = min(n_bins, i + half_window + 1)

        window_counts = event_counts[start_idx:end_idx]
        mean_count = np.mean(window_counts)
        variance = np.var(window_counts, ddof=1)

        if mean_count > 0 and len(window_counts) > 1:
            # Overdispersion relative to Poisson noise
            excess_variance = max(0, variance - mean_count)
            corrected_cvs[i] = np.sqrt(excess_variance) / mean_count
        else:
            corrected_cvs[i] = np.inf  # Mark empty or single-bin windows as unstable

    # Find bins where corrected CV is below threshold
    stable_mask = corrected_cvs <= threshold

    # Find contiguous stable regions
    stable_indices = np.where(stable_mask)[0]

    if len(stable_indices) == 0:
        # No stable region found, return full range
        return time_min, time_max

    # Find the longest contiguous segment
    breaks = np.where(np.diff(stable_indices) > 1)[0] + 1
    segments = np.split(stable_indices, breaks)

    # Select the longest contiguous segment
    longest_segment = max(segments, key=len)
    first_stable = longest_segment[0]
    last_stable = longest_segment[-1]

    # Convert bin indices to time bounds
    t_start = bin_edges[first_stable] if thresh_leftside else 0
    t_end = bin_edges[last_stable + 1] if thresh_rightside else -1

    return t_start, t_end