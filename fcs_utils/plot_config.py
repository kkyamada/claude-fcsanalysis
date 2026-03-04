"""
Plot configuration module for FCS analysis visualization.

Provides a layered configuration system:
1. Built-in defaults
2. Preset styles (publication, exploratory, presentation)
3. User config file (plot_config.yaml)
4. Runtime overrides
"""

import logging
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)

# Built-in default configuration
DEFAULT_CONFIG = {
    "style": "publication",
    "figure": {
        "dpi": 300,
        "figsize_single": [4, 3],
        "figsize_multi": [8, 6],
        "max_cols": 4,
        "facecolor": "white",
        "tight_layout": True,
    },
    "font": {
        "family": "sans-serif",
        "size_title": 14,
        "size_label": 12,
        "size_tick": 10,
        "size_legend": 9,
    },
    "colors": {
        "palette": "Set2",
        "control_color": "#808080",
        "control_patterns": ["Control", "Mock", "Ctrl", "ctrl", "mock", "control"],
        "highlight_color": "#4a7fe8",
        "background": "#F5F5F5",
    },
    "bar": {
        "width": 0.7,
        "edgecolor": "black",
        "linewidth": 1.0,
        "error_capsize": 5,
        "error_linewidth": 1.0,
        "show_title": False,
        "show_points": True,
        "point_size": 15,
        "point_alpha": 1.0,
        "point_facecolor": "white",
        "point_edgecolor": "#333333",
        "point_linewidth": 1.0,
        "control_first": True,
    },
    "scatter": {
        "point_size": 20,
        "alpha": 0.7,
        "edgecolor": "none",
    },
    "line": {
        "linewidth": 2.0,
        "marker": "o",
        "markersize": 8,
        "error_style": "bars",  # "bars" for whiskers, "band" for shaded area
        "error_capsize": 8,
        "error_linewidth": 2.0,
        "error_alpha": 0.2,
        "show_title": False,
    },
    "heatmap": {
        "cmap": "RdYlBu_r",
        "annot": True,
        "fmt": ".1f",
        "linewidths": 0.5,
    },
    "legend": {
        "loc": "best",
        "frameon": True,
        "framealpha": 0.9,
    },
    "grid": {
        "show": False,
        "alpha": 0.3,
        "linestyle": "--",
    },
    "axes": {
        "spines_top": False,
        "spines_right": False,
        "y_percent": True,  # Show y-axis as percentage
        "y_lim_auto": True,
        "y_lim": [0, 100],
    },
}

# Preset configurations that override defaults
PRESETS = {
    "publication": {
        "figure": {"dpi": 300, "figsize_single": [4, 3]},
        "font": {"size_title": 14, "size_label": 12, "size_tick": 10},
        "bar": {"show_points": True},
        "grid": {"show": False},
    },
    "exploratory": {
        "figure": {"dpi": 100, "figsize_single": [6, 4]},
        "font": {"size_title": 12, "size_label": 10, "size_tick": 9},
        "bar": {"show_points": True},
        "grid": {"show": True},
    },
    "presentation": {
        "figure": {"dpi": 150, "figsize_single": [8, 5]},
        "font": {"size_title": 18, "size_label": 14, "size_tick": 12, "size_legend": 11},
        "bar": {"show_points": False, "width": 0.6},
        "line": {"linewidth": 3.0, "markersize": 10},
        "grid": {"show": False},
    },
}


def deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries. Override values take precedence.

    Args:
        base: Base dictionary
        override: Dictionary with override values

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(
    config_path: Optional[Path] = None,
    preset: Optional[str] = None,
    **overrides
) -> dict:
    """
    Load plot configuration with layered overrides.

    Priority (highest to lowest):
    1. Runtime overrides (kwargs)
    2. User config file (plot_config.yaml)
    3. Preset style
    4. Built-in defaults

    Args:
        config_path: Path to user config YAML file
        preset: Preset name ("publication", "exploratory", "presentation")
        **overrides: Runtime parameter overrides

    Returns:
        Merged configuration dictionary
    """
    # Start with defaults
    config = DEFAULT_CONFIG.copy()
    config = deep_merge(config, {})  # Deep copy

    # Apply preset if specified
    if preset is None:
        preset = config.get("style", "publication")

    if preset in PRESETS:
        config = deep_merge(config, PRESETS[preset])
        config["style"] = preset
    else:
        logger.warning(f"Unknown preset '{preset}', using defaults")

    # Load user config file if exists
    if config_path is not None and config_path.exists():
        try:
            with open(config_path, "r") as f:
                user_config = yaml.safe_load(f) or {}
            config = deep_merge(config, user_config)
            logger.info(f"Loaded user config from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load config file {config_path}: {e}")

    # Apply runtime overrides
    if overrides:
        # Handle nested overrides like figure__dpi=300
        nested_overrides = {}
        for key, value in overrides.items():
            if "__" in key:
                parts = key.split("__")
                current = nested_overrides
                for part in parts[:-1]:
                    current = current.setdefault(part, {})
                current[parts[-1]] = value
            else:
                nested_overrides[key] = value
        config = deep_merge(config, nested_overrides)

    return config


def auto_layout(n_items: int, max_cols: int = 4) -> tuple[int, int]:
    """
    Automatically determine grid layout based on number of items.

    Args:
        n_items: Number of items to display
        max_cols: Maximum number of columns

    Returns:
        Tuple of (n_rows, n_cols)
    """
    if n_items <= 0:
        return (1, 1)
    if n_items <= max_cols:
        return (1, n_items)

    n_cols = min(n_items, max_cols)
    n_rows = (n_items + n_cols - 1) // n_cols
    return (n_rows, n_cols)


def auto_figsize(
    n_rows: int,
    n_cols: int,
    base_width: float = 4,
    base_height: float = 3
) -> tuple[float, float]:
    """
    Calculate figure size based on grid dimensions.

    Args:
        n_rows: Number of rows
        n_cols: Number of columns
        base_width: Width per subplot
        base_height: Height per subplot

    Returns:
        Tuple of (width, height)
    """
    return (n_cols * base_width, n_rows * base_height)


def get_config_value(config: dict, *keys, default: Any = None) -> Any:
    """
    Safely get a nested config value.

    Args:
        config: Configuration dictionary
        *keys: Key path (e.g., "figure", "dpi")
        default: Default value if not found

    Returns:
        Config value or default
    """
    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def ensure_config_exists(config_path: Path) -> dict:
    """
    Ensure a config file exists at the given path.
    If not, generate a default config file.

    Args:
        config_path: Path to the config file

    Returns:
        Loaded configuration dictionary
    """
    if not config_path.exists():
        logger.info(f"Generating default config at {config_path}")
        with open(config_path, "w") as f:
            f.write(generate_default_config_yaml())

    return load_config(config_path=config_path)


def generate_default_config_yaml() -> str:
    """
    Generate a default config YAML string for user reference.

    Returns:
        YAML string with commented defaults
    """
    template = """# FCS Plot Configuration
# Default settings for all plot types (bar, line, scatter, heatmap)

style: "publication"

# Color settings
colors:
  palette: "Set2"
  control_color: "#808080"    # Gray for control/mock samples
  control_patterns:
    - "Control"
    - "Mock"
    - "Ctrl"
    - "ctrl"
    - "mock"
    - "control"
  highlight_color: "#4A7FE8"  # Blue for non-control samples

# Bar plot settings
bar:
  width: 0.7
  edgecolor: "black"
  linewidth: 1.0
  error_capsize: 8
  error_linewidth: 2.0
  show_title: false
  show_points: true
  point_size: 18
  point_alpha: 1.0
  point_facecolor: "white"
  point_edgecolor: "#333333"
  point_linewidth: 1.0
  control_first: true         # Control samples on left

# Line plot settings
line:
  linewidth: 2.0
  marker: "o"
  markersize: 8
  error_style: "bars"         # "bars" for whiskers, "band" for shaded area
  error_capsize: 8
  error_linewidth: 2.0
  show_title: false

# Figure settings
figure:
  dpi: 300
  figsize_single: [6, 4]
  figsize_multi: [8, 6]
  max_cols: 4

# Font settings
font:
  size_title: 14
  size_label: 12
  size_tick: 10
  size_legend: 10

# Axis settings
axes:
  spines_top: false
  spines_right: false
  y_percent: true
"""
    return template
