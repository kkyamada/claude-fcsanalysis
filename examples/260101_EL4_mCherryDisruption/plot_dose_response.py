"""
Dose response curve plotting script for EL4 mCherry disruption experiment.
Uses fcs_utils plotting utilities.
"""

import matplotlib.pyplot as plt
import pandas as pd
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

    # Prepare data for mCherry- gate
    df_quant = plot_utils.prepare_summary_data(combined, 'mCherry-', 'relative_percent')

    # Create the plot
    figsize = plot_config.get_config_value(config, 'figure', 'figsize_single', default=[5, 4])
    fig, ax = plt.subplots(figsize=figsize)

    # Use plot_line for dose response
    plot_utils.plot_line(
        df_quant,
        x='conc_value',
        y='value',
        hue='cell_type',
        ax=ax,
        config=config,
        title='Dose Response: mCherry Disruption in EL4 Cells',
        xlabel='Concentration (nM)',
        ylabel='mCherry- (%)',
    )

    ax.set_xlim(-20, 420)

    # Save figure
    output_path = experiment_dir / 'dose_response.png'
    plot_utils.save_figure(fig, output_path, config)
    plt.close(fig)


if __name__ == '__main__':
    main()
