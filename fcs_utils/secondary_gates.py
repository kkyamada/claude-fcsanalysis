import logging
import re
from pathlib import Path
# Thirdparty
import flowkit as fk
import numpy as np
from scipy.stats import norm
from sklearn.mixture import BayesianGaussianMixture
# Local
from fcs_utils.primary_gates import find_gate_path
from fcs_utils.visualization import draw_fig_verbose

logger = logging.getLogger(__name__)


def setup_quant_gates(
        session: fk.Session,
        dict_color: dict,
        fluor_keys: str,
        parent_gate: str,
        gate_for_thresh: str,
        sample_id_list: list,
        thresh_ratio: float = 0.995,
        n_components: int = 1,
        verbose: bool = False,
        fig_dir: Path = Path(""),
) -> str:
    """
    Set up the gates for quantification of the cell population of interest using a mixture model.

    Args:
        session: A flowkit Session object with samples and gating strategy to optimize.
        dict_color: A dict object to map the marker colors to the channel names in the session.
        fluoro_keys: Key parameters to describe the stain used and the direction (+/- symbol) to define which population to extract.
        parent_gate: Name of the parent gate to add the marker gate.
        gate_for_thresh: Name of the parent/grandparent gate to extract events used for threshold determination.
        sample_id_list: List of samples to use for thresholding.
        thresh_ratio: Ratio to define the threshold in the fitted distribution (default: 0.99).
        n_components: Number of mixture model components for threshold detection (default: 1).

    Returns:
        new_gate: Name of the gate added last.
    """
    num_keys = len(fluor_keys.split("/"))
    if num_keys == 1:
        # Rectangule gate
        new_gate = setup_rectangle_gate(
            session,
            dict_color,
            fluor_key = fluor_keys,
            gate_name = fluor_keys,
            parent_gate = parent_gate,
            gate_for_thresh = gate_for_thresh,
            sample_id_list = sample_id_list,
            thresh_ratio = thresh_ratio,
            mode = "single_reverse",
            init_n_components = n_components
        )
    elif num_keys == 2:
        # Qudrant gate
        new_gate = setup_quadrant_gate(
            session,
            dict_color,
            fluor_keys = fluor_keys,
            gate_name = "Quadrant",
            parent_gate = parent_gate,
            gate_for_thresh = gate_for_thresh,
            sample_id_list = sample_id_list,
            thresh_ratio = thresh_ratio,
            n_components = n_components,
        )
    else:
        raise ValueError(f"Detected {num_keys} dimensions in {fluor_keys}. Consider reducing it <=2 for quantification.")
    
    if verbose:
        for sample_idx in range(len(session.get_sample_ids())):
            fig_path = fig_dir / Path(f"tmpquant_sample{sample_idx}.png")
            draw_fig_verbose(session, (), fig_path, sample_idx)
        
    return new_gate


def setup_marker_gates(
        session: fk.Session,
        dict_color: dict,
        fluor_keys: str,
        parent_gate: str,
        sample_id_list: list,
        thresh_ratio: float = 0.995,
        marker_mode: str = "single",
        marker_n_components: int = 2
) -> str:
    """
    Set up the marker gating to extract the cell population of interest using a mixture model.

    Args:
        session: A flowkit Session object with samples and gating strategy to optimize.
        dict_color: A dict object to map the marker colors to the channel names in the session.
        fluoro_key: Key parameters to describe the stain used and the direction (+/- symbol) to define which population to extract.
        parent_gate: Name of the parent gate to add the marker gate.
        sample_id_list: List of samples to use for thresholding.
        thresh_ratio: Ratio to define the threshold in the fitted distribution (default: 0.99).

    Returns:
        gate_name: Name of the gate added last.
    """

    for fluor_key in fluor_keys.split("/"):
        if marker_mode not in ["single", "single_reverse"]:
            raise ValueError(f"Detected mode {marker_mode} for marker gate. Acceptable modes are single or single_reverse")
        gate_name = setup_rectangle_gate(
            session,
            dict_color,
            fluor_key = fluor_key,
            gate_name = fluor_key,
            parent_gate = parent_gate,
            gate_for_thresh = parent_gate,
            sample_id_list = sample_id_list,
            thresh_ratio = thresh_ratio,
            mode = marker_mode,
            init_n_components = marker_n_components
        )

    return gate_name

def setup_quadrant_gate(
        session: fk.Session,
        dict_color: dict,
        fluor_keys: str,
        gate_name: str,
        parent_gate: str,
        gate_for_thresh: str,
        sample_id_list: list,
        thresh_ratio: float = 0.995,
        n_components: int = 1,
) -> str:
    """
    Set up a quadrant gate on two channels to extract the cell population of interest using a mixture model.

    Args:
        session: A flowkit Session object with samples and gating strategy to optimize.
        dict_color: A dict object to map the live/dead stain to the channel name in the session.
        fluoro_key: A key parameter to describe the stain used and the direction (+/- symbol) to define which population to extract.
        gate_name: Name of the gate to optimize.
        parent_gate: Name of the parent gate to add the new gate.
        gate_for_thresh: Name of the parent/grandparent gate to extract events used for threshold determination.
        sample_id_list: List of samples to use for thresholding.
        thresh_ratio: Ratio to define the threshold in the fitted distribution (default: 0.995).
        n_components: Number of mixture model components for threshold detection (default: 1).

    Returns:
        gate_name: Name of the gate added.
    """
    # Extracte necessary arguments and information
    channel_idx = []
    directions = []
    fluor_list = fluor_keys.split("/")
    if not len(fluor_list)==2:
        raise ValueError(f"The argument --color_quant, {fluor_keys}, must be two dimensional for quadrant gate.")
    for fluor_key in fluor_list:
        channel = f"{fluor_key[:-1]}-A"
        sample = session.get_sample(session.get_sample_ids()[0])
        channel_idx.append(sample.get_channel_index(channel))
        direction = fluor_key[-1]
        if not direction in ("+", "-"):
            raise ValueError("+/- symbol required for the argument (--live_stain, --color_marker, and --color_quant).")
        directions.append(direction)
    
    # Aggregate events across samples using parent_gate
    gs = session.gating_strategy
    events_list = []
    for sample_id in sample_id_list:
        sample = session.get_sample(sample_id)
        gated_sample = gs.gate_sample(sample)
        gate_membership = gated_sample.get_gate_membership(gate_for_thresh)
        events = sample.get_events(source="xform", event_mask=gate_membership)
        events_list.append(events[:, channel_idx])
    events_all = np.concatenate(events_list, axis=0)

    # Fit GMM
    logger.info(f"Fitting GMM for defining the gate {gate_name}.")
    range_mins, range_maxes = _estimate_multivariate_range(
        data = events_all,
        directions = directions,
        thresh_ratio = thresh_ratio,
        model_key = "GMM",
        init_n_components = n_components,
    )

    # Set up quadrant gate sub modules (QuadrantDivider)
    quad_divs = []
    div_refs = []
    thresh_values = []
    for i, fluor_key in enumerate(fluor_list):
        channel = f"{fluor_key[:-1]}-A"
        range_min, range_max = range_mins[i], range_maxes[i]
        direction = directions[i]
        if direction == "+":
            value = range_min
        elif direction == "-":
            value = range_max
        quad_div = fk.QuadrantDivider(
            divider_id = fluor_key[:-1],
            dimension_ref = channel,
            compensation_ref = "uncompensated",
            transformation_ref = channel,
            values = [value]
        )
        div_refs.append(fluor_key[:-1])
        quad_divs.append(quad_div)
        thresh_values.append(value)
    
    # Set up quadrant gate sub modules (Quadrant)
    quads = []
    fluor_key1, fluor_key2 = fluor_list[0][:-1], fluor_list[1][:-1]
    for dir1 in ["-", "+"]:
        for dir2 in ["-", "+"]:
            div_ranges = []
            if dir1 == "-":
                div_ranges.append((None, thresh_values[0]))
            else:
                div_ranges.append((thresh_values[0], None))

            if dir2 == "-":
                div_ranges.append((None, thresh_values[1]))
            else:
                div_ranges.append((thresh_values[1], None))

            quad = fk.gates.Quadrant(
                quadrant_id = f"{fluor_key1}{dir1}{fluor_key2}{dir2}",
                divider_refs = div_refs,
                divider_ranges = div_ranges,
            )
            quads.append(quad)

    # Create and add the gate
    gate = fk.gates.QuadrantGate(
        gate_name,
        dividers = quad_divs, 
        quadrants = quads
    )
    if gate_name in dict(gs.get_gate_ids()).keys():
        gs.remove_gate(gate_name)
    gs.add_gate(gate, gate_path=find_gate_path(gs, parent_gate))
    return gate_name
    


def setup_rectangle_gate(
        session: fk.Session,
        dict_color: dict,
        fluor_key: str,
        gate_name: str,
        parent_gate: str,
        gate_for_thresh: str,
        sample_id_list: list,
        thresh_ratio: float = 0.995,
        mode: str = "range",
        init_n_components: int = 2
) -> str:
    """
    Set up a rectangle gate on a single channel to extract the cell population of interest using a mixture model.

    Args:
        session: A flowkit Session object with samples and gating strategy to optimize.
        dict_color: A dict object to map the live/dead stain to the channel name in the session.
        fluoro_key: A key parameter to describe the stain used and the direction (+/- symbol) to define which population to extract.
        gate_name: Name of the gate to optimize.
        parent_gate: Name of the parent gate to add the gate.
        gate_for_thresh: Name of the parent/grandparent gate to extract events used for threshold determination.
        sample_id_list: List of samples to use for thresholding.
        thresh_ratio: Ratio to define the threshold in the fitted distribution (default: 0.995).
        mode: Thresholding mode to extract the range of population ("range") or to set a single thresholding value ("single").
        init_n_components: Initial number of components to strart with for the mixture model.

    Returns:
        gate_name: Name of the gate added.
    """
    channel = f"{fluor_key[:-1]}-A"
    sample = session.get_sample(session.get_sample_ids()[0])
    idx = sample.get_channel_index(channel)
    direction = fluor_key[-1]
    if not direction in ("+", "-"):
        raise ValueError("+/- symbol required for the argument (--live_stain, --color_marker, and --color_quant).")
    
    # Aggregate events across samples using parent_gate
    gs = session.gating_strategy
    events_list = []
    for sample_id in sample_id_list:
        sample = session.get_sample(sample_id)
        gated_sample = gs.gate_sample(sample)
        gate_membership = gated_sample.get_gate_membership(gate_for_thresh)
        events = sample.get_events(source="xform", event_mask=gate_membership)
        events_list.append(events[:, idx])
    events_all = np.concatenate(events_list)

    logger.info(f"Fitting GMM for defining the gate {gate_name}.")
    if mode == "single_reverse":
        # Mode to reverse the direction of the gate, when the negative control is used for thresholding.
        tmp_direction = {"+":"-", "-":"+"}[direction]
    else:
        tmp_direction = direction
    range_min, range_max = _estimate_1d_range(
        data = events_all.flatten(),
        direction = tmp_direction,
        thresh_ratio = thresh_ratio,
        model_key = "GMM",
        init_n_components = init_n_components
    )
    
    if mode == "range":
        dim = fk.Dimension(
            channel,
            transformation_ref=channel,
            range_min=range_min,
            range_max=range_max,
        )
    elif mode == "single":
        if direction == "-":
            dim = fk.Dimension(
                channel,
                transformation_ref=channel,
                range_max=range_max,
            )
        elif direction == "+":
            dim = fk.Dimension(
                channel,
                transformation_ref=channel,
                range_min=range_min,
            )
    elif mode == "single_reverse":
        if direction == "-":
            dim = fk.Dimension(
                channel,
                transformation_ref=channel,
                range_max=range_min,
            )
        elif direction == "+":
            dim = fk.Dimension(
                channel,
                transformation_ref=channel,
                range_min=range_max,
            )
    else:
        raise ValueError(f"Detected mode parameter {mode}, which must be 'range', 'single', or 'single_reverse'.")

    # Create and add the gate
    gate = fk.gates.RectangleGate(
        gate_name=gate_name,
        dimensions=[dim],
    )
    if gate_name in dict(gs.get_gate_ids()).keys():
        gs.remove_gate(gate_name)
    gs.add_gate(gate, gate_path=find_gate_path(gs, parent_gate))
    return gate_name


def _estimate_multivariate_range(
        data: np.ndarray,
        directions: list[str],
        thresh_ratio: float,
        model_key: str = "GMM",
        init_n_components: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Estimate the range of the target population by using a mixutre model in a multi-dimensional space.
    Current implementation assumes clear biomodal distributions with minimal overlaps or unimodal distributions + small noise.

    Args:
        data: Data to fit the mixture model. Must be >=2-dimensional.
        directions: List of direction (+/- symbol) to define which population to extract.
        thresh_ratio: Ratio of target population within the fitted model.
        model_key: Key string to choose a mixture model (default: GMM).
        init_n_components: Initial number of components to start with for the mixture model.

    Returns:
        range_mins, range_maxes: Tuple of min and max values in each dimension to define the range of the target population.
    """
    if data.ndim != 2:
        raise ValueError(f"Input data must be 2D array with shape (n_samples, n_features).")

    n_samples, n_dims = data.shape
    if len(directions) != n_dims:
        raise ValueError(f"Number of directions ({len(directions)}) must match data dimensions ({n_dims}).")

    for d in directions:
        if d not in ("+", "-"):
            raise ValueError(f"Direction must be '+' or '-', got '{d}'.")

    # Assume bimodal distribution or unimodal distribution + noise.
    if model_key == "GMM":
        # Bayesian Gaussian Mixture Model
        gmm = BayesianGaussianMixture(
            random_state=42,
            weight_concentration_prior=1.0,
            n_components=init_n_components
        )
        gmm.fit(data)
        n_components = int(gmm.get_params()["n_components"])
        logger.info(f"Number of mixture components: {n_components}")

        # Get fitted mixture model info
        # means: shape (n_components, n_dims)
        # covariances: shape (n_components, n_dims, n_dims) for 'full' covariance type
        means = np.array(gmm.means_)
        covariances = np.array(gmm.covariances_)
        resp = gmm.predict_proba(data)
        expected_counts = resp.sum(axis=0)
        majority_idx = int(np.argmax(expected_counts))

        for i in range(n_components):
            logger.info(f"Component {i}: expected_count={expected_counts[i]:.1f}, mean={means[i]}")

        # Select target component based on directions
        # Score each component: +1 if direction matches (e.g., "+" and has higher mean), -1 otherwise
        # Pick the component with highest score
        scores = np.zeros(n_components)
        for comp_idx in range(n_components):
            for dim_idx, direction in enumerate(directions):
                comp_mean = means[comp_idx, dim_idx]
                # Compare this component's mean to other components' means in this dimension
                other_means = np.delete(means[:, dim_idx], comp_idx)
                if len(other_means) == 0:
                    # Only one component, score is neutral
                    continue
                avg_other_mean = np.mean(other_means)
                if direction == "+" and comp_mean > avg_other_mean:
                    scores[comp_idx] += 1
                elif direction == "-" and comp_mean < avg_other_mean:
                    scores[comp_idx] += 1
                else:
                    scores[comp_idx] -= 1

        target_idx = int(np.argmax(scores))
        logger.info(f"Component scores: {scores}")
        logger.info(f"Selected component: {target_idx}")

        if majority_idx != target_idx:
            logger.warning(f"Component {target_idx} was selected, but majority of data was assigned to component {majority_idx}.")

        # Extract target component parameters
        target_means = means[target_idx]
        target_cov = covariances[target_idx]
        # Get standard deviations from diagonal of covariance matrix
        target_stds = np.sqrt(np.diag(target_cov))

        # Calculate range for each dimension using thresh_ratio
        # For symmetric coverage around the mean
        lower_q = (1 - thresh_ratio) / 2
        upper_q = (1 + thresh_ratio) / 2
        range_mins = norm.ppf(lower_q, loc=target_means, scale=target_stds)
        range_maxes = norm.ppf(upper_q, loc=target_means, scale=target_stds)

    elif model_key == "Skew-t":
        raise NotImplementedError
    else:
        raise ValueError(f"model_key {model_key} not recognized.")

    return range_mins, range_maxes


def _estimate_1d_range(
        data: np.ndarray,
        direction: str,
        thresh_ratio: float,
        model_key: str = "GMM",
        init_n_components: int = 2,
) -> tuple[float, float]:
    """
    Estimate the range of the target population by using a mixutre model.
    Current implementation assumes clear biomodal distribution with minimal overlap or unimodal distribution + small noise.

    Args:
        data: Data to fit the mixture model. Must be 1-dimensional.
        direction: Direction (+/- symbol) to define which population to extract.
        thresh_ratio: Ratio of target population within the fitted model.
        model_key: Key string to choose a mixture model (default: GMM).

    Returns:
        range_min, range_max: Min and max values to define the range of the target population.
    """
    try:
        assert data.ndim == 1
    except:
        raise ValueError(f"Input data must be one-dimensional.")
    
    # Assume biomodal distribution or unimodal distribution + noise.
    if model_key == "GMM":
        # Bayesian Gaussian Mixture Model
        gmm = BayesianGaussianMixture(
            random_state=42,
            weight_concentration_prior=1.0,
            n_components=init_n_components
        )
        gmm.fit(data.reshape(-1, 1))
        n_components = int(gmm.get_params()["n_components"])
        logger.info(f"Number of mixture components: {n_components}")

        # Get fitted mixture model info
        means = np.array(gmm.means_).flatten()
        stds = np.sqrt(np.array(gmm.covariances_).flatten())
        resp = gmm.predict_proba(data.reshape(-1,1))
        expected_counts = resp.sum(axis=0)
        majority_idx = np.argmax(expected_counts)
        logger.info(f"Expected counts: {expected_counts}")
        logger.info(f"Means:\n{np.array(gmm.means_)}")
        logger.info(f"Covariances:\n{np.array(gmm.covariances_)}")

        # If the direction is +, pick the component with larger mean value, and vice versa.
        if direction == "+":
            target_idx = np.argmax(means)
        elif direction == "-":
            target_idx = np.argmin(means)
        target_mean = means[target_idx]
        target_std = stds[target_idx]

        logger.info(f"Selected component: {target_idx}")
        if majority_idx != target_idx:
            logger.warning(f"The component idx {target_idx} was chosen, but the majority of data was assigned to {majority_idx}.")

        # Set the threshold to capture mean ± std region based on thresh_ratio.
        # For symmetric coverage of thresh_ratio around the mean:
        # lower bound at (1 - thresh_ratio)/2 quantile, upper bound at (1 + thresh_ratio)/2 quantile
        range_min = norm.ppf((1 - thresh_ratio) / 2, loc=target_mean, scale=target_std)
        range_max = norm.ppf((1 + thresh_ratio) / 2, loc=target_mean, scale=target_std)
    elif model_key == "Skew-t":
        # I tried pymc-based implementation before. But achieving stable conversions was challenging and computationally heavy.
        # Using EM-based implementation would be preferred in future.
        # The advantage of Skew-t mixture models over GMM for flow analysis is discussed in (Pyne S., PNAS, 2009).
        raise NotImplementedError
    else:
        raise ValueError(f"model_key {model_key} not recognized.")
    
    return float(range_min), float(range_max)