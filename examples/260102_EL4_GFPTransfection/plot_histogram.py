"""
Histogram plotting script for EL4 GFP Transfection experiment.
Shows GFP fluorescence distribution with threshold line.
Uses one replicate (rep1).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from lxml import etree

import flowkit as fk
import fcs_utils.plot_config as plot_config


def extract_threshold_from_gml(gml_path: Path, gate_name: str) -> float:
    """Extract threshold value from GatingML file for a rectangle gate."""
    tree = etree.parse(str(gml_path))
    root = tree.getroot()

    # Define namespaces
    ns = {
        'gating': 'http://www.isac-net.org/std/Gating-ML/v2.0/gating',
        'data-type': 'http://www.isac-net.org/std/Gating-ML/v2.0/datatypes'
    }

    # Find the gate
    gate = root.find(f".//gating:RectangleGate[@gating:id='{gate_name}']", ns)
    if gate is None:
        raise ValueError(f"Gate '{gate_name}' not found in {gml_path}")

    # Get the min value from dimension
    dim = gate.find("gating:dimension", ns)
    if dim is not None:
        min_val = dim.get(f"{{{ns['gating']}}}min")
        if min_val:
            return float(min_val)

    raise ValueError(f"Could not extract threshold for gate '{gate_name}'")


def get_channel_index_by_pns(sample, channel_name: str) -> int:
    """Get channel index using PNS (description) label."""
    channels = sample.channels
    match = channels[channels['pns'] == channel_name]
    if len(match) == 0:
        raise ValueError(f"Channel '{channel_name}' not found in PNS labels")
    return match.index[0]


def parse_concentration(conc_str: str) -> float:
    """Parse concentration string to numeric value in nM for sorting."""
    if 'uM' in conc_str:
        return float(conc_str.replace('uM', '')) * 1000
    elif 'nM' in conc_str:
        return float(conc_str.replace('nM', ''))
    return 0.0


def main():
    # Paths - use rep1
    experiment_dir = Path(__file__).parent
    rep1_dir = experiment_dir / 'output' / '260102_EL4_GFPuptake_rep1'
    data_dir = experiment_dir / 'data' / '260102_EL4_GFPuptake_rep1'
    gml_path = rep1_dir / 'gating_strategy.gml'

    # Load configuration
    config_path = experiment_dir / 'plot_config.yaml'
    config = plot_config.ensure_config_exists(config_path)

    # Extract threshold from gating strategy
    threshold = extract_threshold_from_gml(gml_path, 'GFP_pos')
    print(f"GFP+ threshold (transformed): {threshold:.4f}")

    # Load session with gating strategy
    session = fk.Session(gating_strategy=str(gml_path), fcs_samples=str(data_dir))

    # Get sample IDs
    sample_ids = session.get_sample_ids()

    # Get GFP-A channel index using PNS label
    sample = session.get_sample(sample_ids[0])
    gfp_idx = get_channel_index_by_pns(sample, 'GFP-A')

    # Colors based on treatment
    colors = {
        'Mock': '#808080',
        'ProteinA': '#66c2a5',  # Set2 color 1
        'ProteinB': '#fc8d62'   # Set2 color 2
    }

    # Parse all samples to get treatments and concentrations
    sample_info = []
    mock_sample = None
    for sample_id in sample_ids:
        name = sample_id.replace('.fcs', '')
        parts = name.split('_')
        treatment = parts[1] if len(parts) > 1 else 'Unknown'
        conc = parts[2] if len(parts) > 2 else '0nM'
        conc_value = parse_concentration(conc)
        info = {
            'sample_id': sample_id,
            'treatment': treatment,
            'concentration': conc,
            'conc_value': conc_value
        }
        sample_info.append(info)
        if treatment == 'Mock':
            mock_sample = info

    # Get non-Mock treatments (columns) and their concentrations (rows)
    non_mock_treatments = sorted(set(
        s['treatment'] for s in sample_info if s['treatment'] != 'Mock'
    ))
    non_mock_concentrations = sorted(set(
        s['conc_value'] for s in sample_info if s['treatment'] != 'Mock'
    ))

    # Rows: Mock at top, then concentrations
    row_labels = ['Mock'] + [
        next(s['concentration'] for s in sample_info
             if s['conc_value'] == c and s['treatment'] != 'Mock')
        for c in non_mock_concentrations
    ]

    n_rows = 1 + len(non_mock_concentrations)  # Mock + concentrations
    n_cols = len(non_mock_treatments)

    # Flatter panels
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(3.5 * n_cols, 1.5 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    if n_cols == 1:
        axes = axes.reshape(-1, 1)

    # First pass: collect all data to determine common x-axis limits
    all_data = {}
    x_min, x_max = float('inf'), float('-inf')

    for info in sample_info:
        sample = session.get_sample(info['sample_id'])
        gs = session.gating_strategy
        gated_sample = gs.gate_sample(sample)
        singlets_result = gated_sample.get_gate_membership('Singlets')

        raw_events = sample.get_events(source='raw')
        gfp_raw = raw_events[singlets_result, gfp_idx]

        logicle = fk.transforms.LogicleTransform(
            param_t=262143, param_w=0.5, param_m=4.5, param_a=0.5
        )
        gfp_data = logicle.apply(gfp_raw)

        all_data[info['sample_id']] = gfp_data
        x_min = min(x_min, np.nanmin(gfp_data))
        x_max = max(x_max, np.nanmax(gfp_data))

    # Add some padding to x limits
    x_range = x_max - x_min
    x_min -= 0.05 * x_range
    x_max += 0.05 * x_range

    # Build grid mapping: (row, col) -> sample_info
    grid = {}
    for col_idx, treatment in enumerate(non_mock_treatments):
        # Row 0: Mock (same for all columns)
        grid[(0, col_idx)] = mock_sample
        # Remaining rows: treatment concentrations
        for row_idx, conc_value in enumerate(non_mock_concentrations, start=1):
            matching = [s for s in sample_info
                       if s['treatment'] == treatment and s['conc_value'] == conc_value]
            if matching:
                grid[(row_idx, col_idx)] = matching[0]

    # Second pass: plot histograms
    for (row_idx, col_idx), info in grid.items():
        ax = axes[row_idx, col_idx]
        gfp_data = all_data[info['sample_id']]

        # Use gray for Mock row, treatment color for others
        if row_idx == 0:
            color = colors.get('Mock', '#808080')
        else:
            color = colors.get(non_mock_treatments[col_idx], '#808080')

        # Compute histogram normalized to mode
        counts, bin_edges = np.histogram(gfp_data, bins=100, range=(x_min, x_max))
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

        # Calculate % above threshold
        pct_above = (gfp_data > threshold).sum() / len(gfp_data) * 100

        # Title with concentration and percentage (Mock for row 0)
        if row_idx == 0:
            ax.set_title(f'Mock ({pct_above:.1f}%)', fontsize=9, pad=2)
        else:
            ax.set_title(f'{info["concentration"]} ({pct_above:.1f}%)', fontsize=9, pad=2)

        # Set common x limits
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(0, 1.05)

        # Only show x-axis label on bottom row
        if row_idx == n_rows - 1:
            ax.set_xlabel('GFP-A', fontsize=9)
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

    # Add treatment labels as column headers
    for col_idx, treatment in enumerate(non_mock_treatments):
        axes[0, col_idx].annotate(
            treatment, xy=(0.5, 1.15), xycoords='axes fraction',
            ha='center', va='bottom', fontsize=11, fontweight='bold'
        )

    plt.tight_layout()
    plt.subplots_adjust(top=0.90)  # Make room for column headers

    # Save figure
    output_path = experiment_dir / 'histogram_rep1.png'
    dpi = plot_config.get_config_value(config, 'figure', 'dpi', default=300)
    fig.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved histogram plot to {output_path}")


if __name__ == '__main__':
    main()
