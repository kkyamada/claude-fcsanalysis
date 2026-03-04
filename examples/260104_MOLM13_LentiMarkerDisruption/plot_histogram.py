"""
Histogram plotting script for MOLM13 Lenti Marker Disruption experiment.
Shows APC fluorescence distribution with threshold line.
Uses one replicate (rep1).
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from lxml import etree

import flowkit as fk
import fcs_utils.plot_config as plot_config


def extract_threshold_from_gml(gml_path: Path, gate_name: str, use_max: bool = True) -> float:
    """Extract threshold value from GatingML file for a rectangle gate."""
    tree = etree.parse(str(gml_path))
    root = tree.getroot()

    ns = {
        'gating': 'http://www.isac-net.org/std/Gating-ML/v2.0/gating',
        'data-type': 'http://www.isac-net.org/std/Gating-ML/v2.0/datatypes'
    }

    gate = root.find(f".//gating:RectangleGate[@gating:id='{gate_name}']", ns)
    if gate is None:
        raise ValueError(f"Gate '{gate_name}' not found in {gml_path}")

    dim = gate.find("gating:dimension", ns)
    if dim is not None:
        if use_max:
            val = dim.get(f"{{{ns['gating']}}}max")
        else:
            val = dim.get(f"{{{ns['gating']}}}min")
        if val:
            return float(val)

    raise ValueError(f"Could not extract threshold for gate '{gate_name}'")


def get_channel_index_by_pns(sample, channel_name: str) -> int:
    """Get channel index using PNS (description) label."""
    channels = sample.channels
    match = channels[channels['pns'] == channel_name]
    if len(match) == 0:
        raise ValueError(f"Channel '{channel_name}' not found in PNS labels")
    return match.index[0]


def main():
    # Paths - use rep1
    experiment_dir = Path(__file__).parent
    rep1_dir = experiment_dir / 'output' / '260104_MOLM13_LentiMarkerDisruption_day7_rep1'
    data_dir = experiment_dir / 'data' / '260104_MOLM13_LentiMarkerDisruption_day7_rep1'
    gml_path = rep1_dir / 'gating_strategy.gml'

    # Load configuration
    config_path = experiment_dir / 'plot_config.yaml'
    config = plot_config.ensure_config_exists(config_path)

    # Extract threshold from gating strategy (APC_neg gate uses max as threshold)
    threshold = extract_threshold_from_gml(gml_path, 'APC_neg', use_max=True)
    print(f"APC- threshold (transformed): {threshold:.4f}")

    # Load session with gating strategy
    session = fk.Session(gating_strategy=str(gml_path), fcs_samples=str(data_dir))

    # Get sample IDs and sort
    sample_ids = sorted(session.get_sample_ids())

    # Get APC-A channel index using PNS label
    sample = session.get_sample(sample_ids[0])
    apc_idx = get_channel_index_by_pns(sample, 'APC-A')

    # Colors: Mock is gray, all others use default blue
    mock_color = '#808080'
    default_color = '#4A7FE8'

    # Create grid layout
    n_samples = len(sample_ids)
    n_cols = 2
    n_rows = (n_samples + n_cols - 1) // n_cols

    # Flatter panels
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(3.5 * n_cols, 1.5 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    axes = axes.flatten()

    # First pass: collect all data to determine common x-axis limits
    all_data = {}
    x_min, x_max = float('inf'), float('-inf')

    for sample_id in sample_ids:
        sample = session.get_sample(sample_id)
        gs = session.gating_strategy
        gated_sample = gs.gate_sample(sample)

        # Get mCherry_pos gate membership (parent of APC_neg)
        parent_result = gated_sample.get_gate_membership('mCherry_pos')

        # Get raw events and apply logicle transform manually
        raw_events = sample.get_events(source='raw')
        apc_raw = raw_events[parent_result, apc_idx]

        # Apply logicle transform (ZE5: T=16777215, W=0.5, M=4.5, A=0.5)
        logicle = fk.transforms.LogicleTransform(
            param_t=16777215, param_w=0.5, param_m=4.5, param_a=0.5
        )
        apc_data = logicle.apply(apc_raw)

        all_data[sample_id] = apc_data
        valid_data = apc_data[~np.isnan(apc_data)]
        if len(valid_data) > 0:
            x_min = min(x_min, np.nanmin(valid_data))
            x_max = max(x_max, np.nanmax(valid_data))

    # Add some padding to x limits
    x_range = x_max - x_min
    x_min -= 0.05 * x_range
    x_max += 0.05 * x_range

    # Second pass: plot histograms
    for i, sample_id in enumerate(sample_ids):
        ax = axes[i]
        apc_data = all_data[sample_id]

        # Parse sample name for label and color
        name = sample_id.replace('.fcs', '')
        parts = name.split('_')
        # Format: MOLM13CellType_Treatment_Marker
        cell_type = parts[0] if len(parts) > 0 else 'Unknown'
        treatment = parts[1] if len(parts) > 1 else 'Unknown'
        label = f'{cell_type}\n{treatment}'

        # Mock=gray, all others=blue
        color = mock_color if 'Mock' in name else default_color

        # Compute histogram normalized to mode
        valid_data = apc_data[~np.isnan(apc_data)]
        counts, bin_edges = np.histogram(valid_data, bins=100, range=(x_min, x_max))
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        # Normalize to mode (peak = 1.0)
        if counts.max() > 0:
            counts_normalized = counts / counts.max()
        else:
            counts_normalized = counts

        # Plot as filled area
        ax.fill_between(bin_centers, counts_normalized, alpha=0.7, color=color)
        ax.plot(bin_centers, counts_normalized, color=color, linewidth=0.5)

        # Add threshold line
        ax.axvline(x=threshold, color='black', linestyle='--', linewidth=1.0)

        # Calculate % below threshold (APC-)
        pct_below = (valid_data < threshold).sum() / len(valid_data) * 100

        # Title
        ax.set_title(f'{label}\n({pct_below:.1f}% APC-)', fontsize=9, pad=2)

        # Set common x limits
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(0, 1.05)

        # Determine row and column position
        row_idx = i // n_cols
        col_idx = i % n_cols

        # Only show x-axis label on bottom row
        if row_idx == n_rows - 1:
            ax.set_xlabel('APC-A', fontsize=9)
        else:
            ax.set_xticklabels([])

        # Only show y-axis label on leftmost column
        if col_idx == 0:
            ax.set_ylabel('Normalized', fontsize=9)
        else:
            ax.set_yticklabels([])

        ax.tick_params(labelsize=7)

        # Remove top/right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # Hide unused subplots
    for i in range(n_samples, len(axes)):
        axes[i].set_visible(False)

    plt.tight_layout()

    # Save figure
    output_path = experiment_dir / 'histogram_rep1.png'
    dpi = plot_config.get_config_value(config, 'figure', 'dpi', default=300)
    fig.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved histogram plot to {output_path}")


if __name__ == '__main__':
    main()
