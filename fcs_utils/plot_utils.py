"""
Plotting utility functions for FCS analysis visualization.

Provides functions for creating various plot types with consistent styling
based on the configuration system.
"""

import logging
import re
from pathlib import Path
from typing import Any, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from fcs_utils.plot_config import (
    auto_figsize,
    auto_layout,
    get_config_value,
    load_config,
)

logger = logging.getLogger(__name__)


def parse_sample_id(sample_id: str) -> dict:
    """
    Parse sample ID to extract cell type, treatment, and concentration.

    Expected format: CellType_Treatment_Concentration.fcs
    Example: HEK293TChe_ProteinA_100nM.fcs -> {
        "cell_type": "HEK293TChe",
        "treatment": "ProteinA",
        "concentration": "100nM",
        "conc_value": 100.0
    }

    Args:
        sample_id: Sample identifier string

    Returns:
        Dictionary with parsed components
    """
    # Remove .fcs extension
    name = sample_id.replace(".fcs", "")
    parts = name.split("_")

    result = {
        "cell_type": parts[0] if len(parts) > 0 else "",
        "treatment": parts[1] if len(parts) > 1 else "",
        "concentration": parts[2] if len(parts) > 2 else "",
        "conc_value": 0.0,
    }

    # Extract numeric concentration value with unit conversion to nM
    if result["concentration"]:
        match = re.search(r"(\d+\.?\d*)\s*(nM|uM|µM)?", result["concentration"], re.IGNORECASE)
        if match:
            value = float(match.group(1))
            unit = match.group(2)
            # Convert uM/µM to nM
            if unit and unit.lower() in ("um", "µm"):
                value *= 1000
            result["conc_value"] = value

    return result


def prepare_summary_data(
    df: pd.DataFrame,
    gate_name: str,
    value_col: str = "relative_percent",
) -> pd.DataFrame:
    """
    Prepare summary data for plotting by filtering to specific gate
    and parsing sample IDs.

    Args:
        df: Summary DataFrame from summary_processed.csv
        gate_name: Gate name to filter (e.g., "mCherry+")
        value_col: Column to use for values

    Returns:
        Processed DataFrame with parsed sample info
    """
    # Filter to specific gate
    df_gate = df[df["gate_name"] == gate_name].copy()

    if df_gate.empty:
        logger.warning(f"No data found for gate '{gate_name}'")
        return df_gate

    # Parse sample IDs
    parsed = df_gate["sample_id"].apply(parse_sample_id).apply(pd.Series)
    df_gate = pd.concat([df_gate, parsed], axis=1)

    # Rename value column for consistency
    df_gate["value"] = df_gate[value_col]

    return df_gate


def is_control_sample(value: str, config: dict) -> bool:
    """
    Check if a value indicates a control/mock sample.

    Args:
        value: String to check (e.g., cell_type, treatment, sample_id)
        config: Configuration dictionary

    Returns:
        True if value matches any control pattern
    """
    patterns = get_config_value(
        config, "colors", "control_patterns",
        default=["Control", "Mock", "Ctrl", "ctrl", "mock", "control"]
    )
    return any(pattern in str(value) for pattern in patterns)


def build_color_palette(
    categories: list,
    config: dict,
    hue_column_values: Optional[pd.Series] = None,
    use_distinct_colors: bool = True,
) -> dict:
    """
    Build a color palette that assigns gray to control/mock samples
    and distinct colors to non-control samples.

    Args:
        categories: List of unique category values
        config: Configuration dictionary
        hue_column_values: Optional series to check for control patterns
        use_distinct_colors: If True, use different colors for each non-control
                             category. If False, use single highlight_color.

    Returns:
        Dictionary mapping categories to colors
    """
    control_color = get_config_value(config, "colors", "control_color", default="#808080")
    highlight_color = get_config_value(config, "colors", "highlight_color", default="#4A7FE8")
    palette_name = get_config_value(config, "colors", "palette", default="Set2")

    # Separate control and non-control categories
    control_cats = [c for c in categories if is_control_sample(c, config)]
    non_control_cats = [c for c in categories if not is_control_sample(c, config)]

    # Build palette dict
    palette = {}

    # Assign gray to control samples
    for cat in control_cats:
        palette[cat] = control_color

    # Assign colors to non-control samples
    if use_distinct_colors and len(non_control_cats) > 1:
        # Use seaborn palette for distinct colors
        colors = sns.color_palette(palette_name, n_colors=len(non_control_cats))
        for cat, color in zip(non_control_cats, colors):
            palette[cat] = color
    else:
        # Use single highlight color
        for cat in non_control_cats:
            palette[cat] = highlight_color

    return palette


def apply_style(ax: plt.Axes, config: dict) -> None:
    """
    Apply consistent styling to an axes object.

    Args:
        ax: Matplotlib axes
        config: Configuration dictionary
    """
    # Spine visibility
    ax.spines["top"].set_visible(get_config_value(config, "axes", "spines_top", default=False))
    ax.spines["right"].set_visible(get_config_value(config, "axes", "spines_right", default=False))

    # Font sizes
    ax.tick_params(labelsize=get_config_value(config, "font", "size_tick", default=10))

    # Grid
    if get_config_value(config, "grid", "show", default=False):
        ax.grid(
            True,
            alpha=get_config_value(config, "grid", "alpha", default=0.3),
            linestyle=get_config_value(config, "grid", "linestyle", default="--"),
        )


def plot_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    config: Optional[dict] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs
) -> plt.Axes:
    """
    Create a bar plot with consistent styling.

    Args:
        df: DataFrame with data
        x: Column for x-axis
        y: Column for y-axis values
        hue: Column for color grouping
        ax: Existing axes (creates new if None)
        config: Configuration dictionary
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        **kwargs: Additional arguments for seaborn.barplot

    Returns:
        Matplotlib axes
    """
    if config is None:
        config = load_config()

    if ax is None:
        figsize = get_config_value(config, "figure", "figsize_single", default=[4, 3])
        fig, ax = plt.subplots(figsize=figsize)

    # Get bar configuration
    bar_config = config.get("bar", {})

    # Build color palette with control samples as gray
    hue_order = None
    if hue is not None:
        categories = df[hue].unique().tolist()
        # Sort so control samples come first if control_first is True
        if bar_config.get("control_first", True):
            control_cats = [c for c in categories if is_control_sample(c, config)]
            non_control_cats = [c for c in categories if not is_control_sample(c, config)]
            hue_order = control_cats + non_control_cats
        else:
            hue_order = categories
        palette = build_color_palette(hue_order, config)
    else:
        palette = get_config_value(config, "colors", "palette", default="Set2")

    # Create bar plot
    sns.barplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        hue_order=hue_order,
        ax=ax,
        palette=palette,
        width=bar_config.get("width", 0.7),
        edgecolor=bar_config.get("edgecolor", "black"),
        linewidth=bar_config.get("linewidth", 1.0),
        capsize=bar_config.get("error_capsize", 5) / 100,  # Convert to fraction
        err_kws={"linewidth": bar_config.get("error_linewidth", 1.0)},
        errorbar="sd",
        **kwargs
    )

    # Overlay individual points if configured
    if bar_config.get("show_points", True):
        strip = sns.stripplot(
            data=df,
            x=x,
            y=y,
            hue=hue,
            hue_order=hue_order,
            ax=ax,
            size=bar_config.get("point_size", 15) ** 0.5,  # stripplot uses diameter
            alpha=bar_config.get("point_alpha", 1.0),
            dodge=True if hue else False,
            legend=False,
        )
        # Style points with white fill and dark edge
        point_facecolor = bar_config.get("point_facecolor", "white")
        point_edgecolor = bar_config.get("point_edgecolor", "#333333")
        point_linewidth = bar_config.get("point_linewidth", 1.0)
        for collection in ax.collections:
            collection.set_facecolor(point_facecolor)
            collection.set_edgecolor(point_edgecolor)
            collection.set_linewidth(point_linewidth)

    # Remove legend title
    legend = ax.get_legend()
    if legend is not None:
        legend.set_title("")

    # Apply styling
    apply_style(ax, config)

    # Labels
    font_config = config.get("font", {})
    if title and bar_config.get("show_title", False):
        ax.set_title(title, fontsize=font_config.get("size_title", 14))
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=font_config.get("size_label", 12))
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=font_config.get("size_label", 12))

    # Y-axis percentage formatting
    if get_config_value(config, "axes", "y_percent", default=True):
        ax.set_ylabel(ylabel or "Percentage (%)", fontsize=font_config.get("size_label", 12))

    return ax


def plot_line(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    config: Optional[dict] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs
) -> plt.Axes:
    """
    Create a line plot with consistent styling.

    Args:
        df: DataFrame with data
        x: Column for x-axis
        y: Column for y-axis values
        hue: Column for color grouping
        ax: Existing axes (creates new if None)
        config: Configuration dictionary
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        **kwargs: Additional arguments for seaborn.lineplot

    Returns:
        Matplotlib axes
    """
    if config is None:
        config = load_config()

    if ax is None:
        figsize = get_config_value(config, "figure", "figsize_single", default=[4, 3])
        fig, ax = plt.subplots(figsize=figsize)

    # Get line configuration
    line_config = config.get("line", {})

    # Build color palette with control samples as gray
    hue_order = None
    if hue is not None:
        categories = df[hue].unique().tolist()
        # Sort so control samples come first
        control_cats = [c for c in categories if is_control_sample(c, config)]
        non_control_cats = [c for c in categories if not is_control_sample(c, config)]
        hue_order = control_cats + non_control_cats
        palette = build_color_palette(hue_order, config)
    else:
        palette = get_config_value(config, "colors", "palette", default="Set2")

    # Error bar styling
    err_kws = {
        "capsize": line_config.get("error_capsize", 5) / 100,
        "capthick": line_config.get("error_linewidth", 2.0),
        "elinewidth": line_config.get("error_linewidth", 2.0),
    }

    # Create line plot
    sns.lineplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        hue_order=hue_order,
        ax=ax,
        palette=palette,
        linewidth=line_config.get("linewidth", 2.0),
        marker=line_config.get("marker", "o"),
        markersize=line_config.get("markersize", 8),
        errorbar="sd",
        err_style=line_config.get("error_style", "bars"),
        err_kws=err_kws,
        **kwargs
    )

    # Remove legend title
    legend = ax.get_legend()
    if legend is not None:
        legend.set_title("")

    # Apply styling
    apply_style(ax, config)

    # Labels
    font_config = config.get("font", {})
    if title and line_config.get("show_title", False):
        ax.set_title(title, fontsize=font_config.get("size_title", 14))
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=font_config.get("size_label", 12))
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=font_config.get("size_label", 12))

    return ax


def plot_scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    config: Optional[dict] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs
) -> plt.Axes:
    """
    Create a scatter plot with consistent styling.

    Args:
        df: DataFrame with data
        x: Column for x-axis
        y: Column for y-axis
        hue: Column for color grouping
        ax: Existing axes (creates new if None)
        config: Configuration dictionary
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        **kwargs: Additional arguments for seaborn.scatterplot

    Returns:
        Matplotlib axes
    """
    if config is None:
        config = load_config()

    if ax is None:
        figsize = get_config_value(config, "figure", "figsize_single", default=[4, 3])
        fig, ax = plt.subplots(figsize=figsize)

    # Get scatter configuration
    scatter_config = config.get("scatter", {})

    # Build color palette with control samples as gray
    if hue is not None:
        categories = df[hue].unique().tolist()
        palette = build_color_palette(categories, config)
    else:
        palette = get_config_value(config, "colors", "palette", default="Set2")

    # Create scatter plot
    sns.scatterplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        ax=ax,
        palette=palette,
        s=scatter_config.get("point_size", 20),
        alpha=scatter_config.get("alpha", 0.7),
        edgecolor=scatter_config.get("edgecolor", "none"),
        **kwargs
    )

    # Apply styling
    apply_style(ax, config)

    # Labels
    font_config = config.get("font", {})
    if title:
        ax.set_title(title, fontsize=font_config.get("size_title", 14))
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=font_config.get("size_label", 12))
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=font_config.get("size_label", 12))

    return ax


def plot_heatmap(
    df: pd.DataFrame,
    ax: Optional[plt.Axes] = None,
    config: Optional[dict] = None,
    title: Optional[str] = None,
    **kwargs
) -> plt.Axes:
    """
    Create a heatmap with consistent styling.

    Args:
        df: DataFrame with data (index and columns define axes)
        ax: Existing axes (creates new if None)
        config: Configuration dictionary
        title: Plot title
        **kwargs: Additional arguments for seaborn.heatmap

    Returns:
        Matplotlib axes
    """
    if config is None:
        config = load_config()

    if ax is None:
        figsize = get_config_value(config, "figure", "figsize_single", default=[4, 3])
        fig, ax = plt.subplots(figsize=figsize)

    # Get heatmap configuration
    heatmap_config = config.get("heatmap", {})

    # Create heatmap
    sns.heatmap(
        df,
        ax=ax,
        cmap=heatmap_config.get("cmap", "RdYlBu_r"),
        annot=heatmap_config.get("annot", True),
        fmt=heatmap_config.get("fmt", ".1f"),
        linewidths=heatmap_config.get("linewidths", 0.5),
        **kwargs
    )

    # Labels
    font_config = config.get("font", {})
    if title:
        ax.set_title(title, fontsize=font_config.get("size_title", 14))

    return ax


def create_multi_panel(
    plot_func: callable,
    data_list: list[tuple[pd.DataFrame, dict]],
    config: Optional[dict] = None,
    suptitle: Optional[str] = None,
) -> plt.Figure:
    """
    Create a multi-panel figure with automatic layout.

    Args:
        plot_func: Plotting function to call for each panel
        data_list: List of (DataFrame, kwargs) tuples for each panel
        config: Configuration dictionary
        suptitle: Overall figure title

    Returns:
        Matplotlib figure
    """
    if config is None:
        config = load_config()

    n_panels = len(data_list)
    max_cols = get_config_value(config, "figure", "max_cols", default=4)
    n_rows, n_cols = auto_layout(n_panels, max_cols)

    base_size = get_config_value(config, "figure", "figsize_single", default=[4, 3])
    figsize = auto_figsize(n_rows, n_cols, base_size[0], base_size[1])

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    if n_panels == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    for i, (df, kwargs) in enumerate(data_list):
        plot_func(df, ax=axes[i], config=config, **kwargs)

    # Hide unused axes
    for i in range(n_panels, len(axes)):
        axes[i].set_visible(False)

    if suptitle:
        font_config = config.get("font", {})
        fig.suptitle(suptitle, fontsize=font_config.get("size_title", 14) + 2)

    if get_config_value(config, "figure", "tight_layout", default=True):
        fig.tight_layout()

    return fig


def save_figure(
    fig: plt.Figure,
    output_path: Union[str, Path],
    config: Optional[dict] = None,
) -> None:
    """
    Save figure with configured settings.

    Args:
        fig: Matplotlib figure
        output_path: Output file path
        config: Configuration dictionary
    """
    if config is None:
        config = load_config()

    dpi = get_config_value(config, "figure", "dpi", default=300)
    facecolor = get_config_value(config, "figure", "facecolor", default="white")

    fig.savefig(
        output_path,
        dpi=dpi,
        facecolor=facecolor,
        bbox_inches="tight",
    )
    logger.info(f"Saved figure to {output_path}")
