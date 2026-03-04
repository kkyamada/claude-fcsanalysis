"""
Dose response curve plotting script for EL4 GFP Transfection experiment.
Uses fcs_utils plotting utilities.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

import fcs_utils.plot_config as plot_config
import fcs_utils.plot_utils as plot_utils


def main():
    # Paths
    experiment_dir = Path(__file__).parent
    output_dir = experiment_dir / 'output'

    # Load configuration (generate default if not exists)
    config_path = experiment_dir / 'plot_config.yaml'
    config = plot_config.ensure_config_exists(config_path)

    # Load and combine summary data
    csv_files = list(output_dir.glob('*/summary_processed.csv'))
    dfs = []
    for f in csv_files:
        df = pd.read_csv(f)
        df['rep'] = f.parent.name
        dfs.append(df)
    combined = pd.concat(dfs, ignore_index=True)

    # Prepare data for GFP+ gate
    df_quant = plot_utils.prepare_summary_data(combined, 'GFP+', 'relative_percent')

    # Parse concentration - handle both nM and uM
    def parse_conc_nM(conc_str):
        """Convert concentration string to nM."""
        if 'uM' in conc_str:
            return float(conc_str.replace('uM', '')) * 1000
        elif 'nM' in conc_str:
            return float(conc_str.replace('nM', ''))
        return 0.0

    df_quant['conc_nM'] = df_quant['concentration'].apply(parse_conc_nM)

    # Create the plot
    figsize = plot_config.get_config_value(config, 'figure', 'figsize_single', default=[6, 4])
    fig, ax = plt.subplots(figsize=figsize)

    # Use plot_line for dose response, colored by treatment
    plot_utils.plot_line(
        df_quant,
        x='conc_nM',
        y='value',
        hue='treatment',
        ax=ax,
        config=config,
        title='Dose Response: GFP Transfection in EL4 Cells',
        xlabel='Concentration (nM)',
        ylabel='GFP+ (%)',
    )

    # Use log scale for x-axis (skip 0)
    ax.set_xscale('symlog', linthresh=1)
    ax.set_xlim(-0.5, 2000)

    # Save figure
    output_path = experiment_dir / 'dose_response.png'
    plot_utils.save_figure(fig, output_path, config)
    plt.close(fig)
    print(f"Saved dose response plot to {output_path}")


if __name__ == '__main__':
    main()
