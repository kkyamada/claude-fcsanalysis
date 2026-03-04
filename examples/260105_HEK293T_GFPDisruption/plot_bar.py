"""
Bar plot script for HEK293T GFP disruption experiment.
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

    # Prepare data for GFP- gate
    df_quant = plot_utils.prepare_summary_data(combined, 'GFP-', 'relative_percent')

    # Create condition label for x-axis
    df_quant['condition'] = df_quant['treatment'] + ' (' + df_quant['concentration'] + ')'

    # Create the plot
    figsize = plot_config.get_config_value(config, 'figure', 'figsize_single', default=[6, 4])
    fig, ax = plt.subplots(figsize=figsize)

    # Use plot_bar
    plot_utils.plot_bar(
        df_quant,
        x='condition',
        y='value',
        hue='cell_type',
        ax=ax,
        config=config,
        title='GFP Disruption in HEK293T Cells',
        xlabel='Treatment',
        ylabel='GFP- (%)',
    )

    # Save figure
    output_path = experiment_dir / 'bar_plot.png'
    plot_utils.save_figure(fig, output_path, config)
    plt.close(fig)
    print(f"Saved bar plot to {output_path}")


if __name__ == '__main__':
    main()
