import logging
import os
import re
from collections import defaultdict
from pathlib import Path
# Thirdparty
import flowkit as fk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes

COLOR_BG = "#C0C0C0"
COLOR_POS = "#6495ED"
COLOR_THRESH = "#696969"
SUBPLOT_W = 6
SUBPLOT_H = 4
FONTSIZE_TICK = 11
FONTSIZE_LABEL = 13
FONTSIZE_TITLE = 15
FIG_DPI = 300

logger = logging.getLogger(__name__)

def process_data(
        session: fk.Session,
        fig_dir: Path,
        output_dir: Path,
        max_val: float,
        savefig: bool = True,
        verbose: bool = False,
        vis_mode: str = "default"
) -> None:
    """
    Process all data in the session with the defined gates.
    """
    # Create output directories if they don't exist
    if not fig_dir.exists():
        fig_dir.mkdir(parents=True)
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    gs = session.gating_strategy
    sample = session.get_sample(session.get_sample_ids()[0])

    # Get FSC-A and SSC-A channel data
    fsc_a_ch = None
    ssc_a_ch = None
    ssc_h_ch = None
    for ch in sample.pnn_labels:
        if "SSC" in ch and "-A" in ch:
                ssc_a_ch = ch
        elif "SSC" in ch and "-H" in ch:
                ssc_h_ch = ch
        elif "FSC" in ch and "-A" in ch:
                fsc_a_ch = ch
    if fsc_a_ch is None or ssc_a_ch is None or ssc_h_ch is None:
        raise ValueError("FSC-A and SSC-A channel could not be found in sample.")
    
    # Set up plot limits
    timeqc_title = "root>TimeQC"
    dict_lims = _setup_channel_lims(session, ssc_a_ch, timeqc_title, max_val, vis_mode)
    if verbose:
        print(f"Detected figure limits:\n{dict_lims}")
    
    df_save = pd.DataFrame()
    # Generate gate-wise scatter plots for each sample
    for sample_id in session.get_sample_ids():
        sample = session.get_sample(sample_id)
        gated_sample = gs.gate_sample(sample)
        gate_data = pd.DataFrame(gated_sample.report)
        num_vis = np.max(gate_data["level"])

        fig = plt.figure(
            figsize=(SUBPLOT_W * num_vis, SUBPLOT_H),
            facecolor=(0,0,0,0)
        )
        ax = fig.subplots(nrows=1, ncols=num_vis)
        # Assumes always num_vis>=2.
        last_x_channel = ssc_a_ch
        for i in range(num_vis):
            tmp_df = gate_data[gate_data["level"]==(i+1)]

            # Retrieve gate info
            sample_id, gate_path, gate_name, gate_type, quad, parent, _, _, rel_perc, _= tmp_df.values[0]
            if gate_type == "QuadrantGate":
                dimension_ids = []
                for dim in gs.get_gate(quad).dimensions:
                    dimension_ids.append(dim.dimension_ref)
            else:    
                dimension_ids = gs.get_gate(gate_name).get_dimension_ids()
            
            if len(dimension_ids) == 1:
                x_channel = dimension_ids[0]
                if vis_mode == "default" or "root" in gate_name:
                    y_channel = ssc_a_ch
                elif vis_mode == "last":
                    y_channel = last_x_channel
            else:
                x_channel, y_channel = dimension_ids
            x_idx, y_idx = sample.get_channel_index(x_channel), sample.get_channel_index(y_channel)
            last_x_channel = x_channel
            subplot_title = f"{parent}>{gate_name}"

            # Retrieve gated events
            # gated_sample.get_gate_membership() does not work with quadrant gate in flowkit==1.3.0. Waiting for being debugged.
            if gate_type == "QuadrantGate":
                gate_membership = gated_sample._raw_results[(quad, "/".join(gate_path))][gate_name]["events"]
            else:
                gate_membership = gated_sample._raw_results[(gate_name, "/".join(gate_path))]["events"]
            events = sample.get_events(source="xform", event_mask=gate_membership)
            x_events, y_events = events[:, x_idx], events[:, y_idx]

            # Retrieve those events gated out
            n_total = sample.event_count
            parent_membership = get_parent_membership(gate_path, parent, n_total, gated_sample)
            parent_only = np.logical_and(parent_membership, np.logical_not(gate_membership))
            parents = sample.get_events(source="xform", event_mask=parent_only)
            x_parents, y_parents = parents[:, x_idx], parents[:, y_idx]
            
            # Draw scatter plots and gates
            x_transform, y_transform = session.get_transform(x_channel), session.get_transform(y_channel)
            _plot_scatter_gate(
                ax=ax[i],
                x_parents=x_parents,
                y_parents=y_parents,
                x_events=x_events,
                y_events=y_events,
                parent=parent,
                gate_name=gate_name,
                rel_perc=rel_perc,
                subplot_title=subplot_title,
                timeqc_title=timeqc_title,
                x_channel=x_channel,
                y_channel=y_channel,
                x_transform=x_transform,
                y_transform=y_transform,
                dict_lims=dict_lims,
                verbose=verbose
            )
            draw_gate(
                ax[i],
                session,
                sample_id,
                gate_name,
                gate_type,
                quad,
                xlims=dict_lims[subplot_title][0,:]
            )
        
        # Save figure
        fig.suptitle(sample_id, fontsize=FONTSIZE_TITLE)
        plt.tight_layout()
        if savefig:
            figfile = str(Path(sample_id).stem) + ".png"
            fig.savefig(fig_dir / Path(figfile), dpi=FIG_DPI)

        # Collect data
        if len(df_save)==0:
            df_save = gate_data.copy()
        else:
            df_save = pd.concat([df_save, gate_data], axis=0)
    # Save data
    output_path = output_dir / Path("summary_processed.csv")
    df_save.to_csv(output_path, index=False)
    logger.info(f"Finished processing samples.")
    logger.info(f"Figures are saved to {fig_dir}.")
    logger.info(f"Output is saved to {output_path}.")
        
def _plot_scatter_gate(
        ax: Axes,
        x_parents: np.ndarray,
        y_parents: np.ndarray,
        x_events: np.ndarray,
        y_events: np.ndarray,
        parent: str,
        gate_name: str,
        rel_perc: float,
        subplot_title: str,
        timeqc_title: str,
        x_channel: str,
        y_channel: str,
        x_transform,
        y_transform,
        dict_lims: dict,
        discarded_color: str = COLOR_BG,
        gated_color: str = COLOR_POS,
        verbose: bool = False,
) -> None:
    """Scatter plots for each gate."""
    ax.scatter(x_parents, y_parents, marker="o", s=4, linewidths=0, alpha=0.2, facecolor=discarded_color, label=f"{parent}")
    ax.scatter(x_events, y_events, marker="o", s=4, linewidths=0, alpha=0.5, facecolor=gated_color, label=f"{gate_name}: {rel_perc:.1f}%")

    fontsize_tick = 10
    fontsize_label = 13
    fontsize_title = 15
    res_log10 = 0.2
    
    # """
    if subplot_title != timeqc_title:
        # Guard against zero or negative values for log10
        x_min_val = x_transform.inverse(
            np.array(dict_lims[subplot_title][0,0]).reshape(-1,1)
        )
        x_max_val = x_transform.inverse(
            np.array(dict_lims[subplot_title][0,1]).reshape(-1,1)
        )
        x_min_val = np.nanmax([float(x_min_val.flatten()[0]), 1e2])
        x_max_val = np.nanmin([float(x_max_val.flatten()[0]), 1e9])
        x_mintick = np.ceil(np.log10(x_min_val)/res_log10)*res_log10
        x_maxtick = np.floor(np.log10(x_max_val)/res_log10)*res_log10
        
        if verbose:
            print(x_channel)
            print(x_min_val, x_max_val)
            print(x_mintick, x_maxtick)
            
        xticks = _generate_ticks(x_mintick, x_maxtick)
        
        xticks = 10**xticks

        ax.set_xticks(x_transform.apply(xticks))
        ax.set_xlim(dict_lims[subplot_title][0])
        ax.set_xticklabels([f"{np.round(v, 1)}" for v in np.log10(xticks)], fontsize=fontsize_tick)
        ax.set_xlabel(f"{x_channel} (log$_{{10}}$)", fontsize=fontsize_label)
    else:
        ax.tick_params(axis='x', labelsize=fontsize_tick)
        ax.set_xlabel(x_channel, fontsize=fontsize_label)


    # Guard against zero or negative values for log10
    y_min_val = y_transform.inverse(
        np.array(dict_lims[subplot_title][1,0]).reshape(-1,1)
    )
    y_max_val = y_transform.inverse(
        np.array(dict_lims[subplot_title][1,1]).reshape(-1,1)
    )
    y_min_val = np.nanmax([float(y_min_val.flatten()[0]), 1e2])
    y_max_val = np.nanmin([float(y_max_val.flatten()[0]), 1e9])
    y_mintick = np.ceil(np.log10(y_min_val)/res_log10)*res_log10
    y_maxtick = np.floor(np.log10(y_max_val)/res_log10)*res_log10
    
    
    if verbose:
        print(y_channel)
        print(y_min_val, y_max_val)
        print(y_mintick, y_maxtick)
        
    yticks = _generate_ticks(y_mintick, y_maxtick)
    yticks = 10**yticks
    
    ax.set_yticks(y_transform.apply(yticks))
    ax.set_ylim(dict_lims[subplot_title][1])
    ax.set_yticklabels([f"{np.round(v, 1)}" for v in np.log10(yticks)], fontsize=fontsize_tick)
    ax.set_ylabel(f"{y_channel} (log$_{{10}}$)", fontsize=fontsize_label)

    """
    ax.tick_params(axis='x', labelsize=fontsize_tick)
    ax.set_xlabel(x_channel, fontsize=fontsize_label)
    ax.tick_params(axis='y', labelsize=fontsize_tick)
    ax.set_ylabel(y_channel, fontsize=fontsize_label)
    """

    ax.set_title(subplot_title, fontsize=fontsize_title)
    ax.set_facecolor((1,1,1))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    leg = ax.legend(fontsize=fontsize_tick)
    for handle in leg.legend_handles:
        handle.set_sizes([20])
        handle.set_alpha(0.8)

def draw_gate(
        ax: Axes,
        session: fk.Session,
        sample_id: str,
        gate_name: str,
        gate_type: str,
        quad: str,
        xlims: list[float],
) -> None:
    """Draw gate boundaries on the axes."""
    if gate_type == "QuadrantGate":
        gate = session.get_gate(quad)
    else:
        if gate_name == "TimeQC":
            gate = session.get_gate(gate_name, sample_id=sample_id)
        else:
            gate = session.get_gate(gate_name)
    line_color = COLOR_THRESH
    line_width = 1.5
    line_style = "--"
    line_alpha = 0.9

    # Thresh values and vertices are all in the transformed values in the corresponding channel.
    # So, you can directly use these coordinates on ax.
    if isinstance(gate, fk.gates.RectangleGate):
        dimension = gate.dimensions[0]
        min_thresh, max_thresh = dimension.min, dimension.max
        if min_thresh is not None and len(xlims)>0:
            if min_thresh < xlims[0]:
                min_thresh = xlims[0]
            ax.axvline(x=min_thresh, color=line_color, linewidth=line_width, linestyle=line_style, alpha=line_alpha)
        if max_thresh is not None and len(xlims)>0:
            if max_thresh > xlims[1]:
                max_thresh = xlims[1]
            ax.axvline(x=max_thresh, color=line_color, linewidth=line_width, linestyle=line_style, alpha=line_alpha)

    elif isinstance(gate, fk.gates.PolygonGate):
        vertices = np.array(gate.vertices)
        # Close the polygon by appending the first vertex
        vertices_closed = np.vstack([vertices, vertices[0]])
        ax.plot(vertices_closed[:, 0], vertices_closed[:, 1],
                color=line_color, linewidth=line_width, linestyle=line_style, alpha=line_alpha)

    elif isinstance(gate, fk.gates.QuadrantGate):
        # Quadrant gates should have multiple thresholds
        dimension_ids = []
        gs = session.gating_strategy
        for dim in gs.get_gate(quad).dimensions:
            dimension_ids.append(dim.dimension_ref)
        x_channel = dimension_ids[0] if len(dimension_ids) > 0 else None
        y_channel = dimension_ids[1] if len(dimension_ids) > 1 else None
        for dimension in gate.dimensions:
            dim_ref = dimension.dimension_ref
            vals = dimension.values
            for val in vals:
                if dim_ref == x_channel:
                    ax.axvline(x=val, color=line_color, linewidth=line_width, linestyle=line_style, alpha=line_alpha)
                elif dim_ref == y_channel:
                    ax.axhline(y=val, color=line_color, linewidth=line_width, linestyle=line_style, alpha=line_alpha)
    else:
        raise NotImplementedError(f"draw_gate function is not implemented for {type(gate)}.")

def _generate_ticks(
        tick_min: float,
        tick_max: float,
        num_min: int=3,
        num_max: int=5,
):
    """
    Generate clean figure ticks in the range (tick_min, tick_max), where the number of ticks is in the range (num_min, num_max).
    Prioritizes "nice" tick values (integers, then 0.5 increments, then 0.2 increments).
    """
    tick_range = tick_max - tick_min

    # Handle edge case: invalid or zero range
    if tick_range <= 0:
        return np.array([tick_min])

    # Nice step sizes in order of preference (integers first, then finer divisions)
    nice_steps = [2.0, 1.0, 0.5, 0.2, 0.1]

    for step in nice_steps:
        # Start at the first nice value >= tick_min
        first_tick = np.ceil(tick_min / step) * step
        # End at the last nice value <= tick_max
        last_tick = np.floor(tick_max / step) * step

        if first_tick + step > last_tick:
            continue

        ticks = np.arange(first_tick, last_tick + step * 0.5, step)
        # Round to avoid floating point artifacts
        ticks = np.round(ticks / step) * step

        if num_min <= len(ticks) <= num_max:
            return ticks

    # Fallback: return evenly spaced ticks with num_min points
    return np.linspace(tick_min, tick_max, num_min)

def _setup_channel_lims(
        session: fk.Session,
        ssc_a_ch: str,
        timeqc_title: str,
        max_val: float,
        vis_mode: str,
) -> defaultdict:
    gs = session.gating_strategy

    # Get number of axes
    sample = session.get_sample(session.get_sample_ids()[0])
    gated_sample = gs.gate_sample(sample)
    gate_data = pd.DataFrame(gated_sample.report)
    num_vis = np.max(gate_data["level"])

    # Plot all events from all samples
    # key: subplot_title
    # value: np.array([[xlim_min, xlim_max], [ylim_min, ylim_max]])
    dict_lims = defaultdict(lambda: np.array([[max_val, 0.0], [max_val, 0.0]]))
    for sample_id in session.get_sample_ids():
        sample = session.get_sample(sample_id)
        gated_sample = gs.gate_sample(sample)
        gate_data = pd.DataFrame(gated_sample.report)
        num_vis = np.max(gate_data["level"])

        last_x_channel = ssc_a_ch
        for i in range(num_vis):
            tmp_df = gate_data[gate_data["level"]==(i+1)]
            
            # Retrieve gate info
            sample_id, gate_path, gate_name, gate_type, quad, parent, _, _, rel_perc, _= tmp_df.values[0]
            if gate_type == "QuadrantGate":
                dimension_ids = []
                for dim in gs.get_gate(quad).dimensions:
                    dimension_ids.append(dim.dimension_ref)
            else:    
                dimension_ids = gs.get_gate(gate_name).get_dimension_ids()
            if len(dimension_ids) == 1:
                x_channel = dimension_ids[0]
                if vis_mode == "default" or "root" in gate_name:
                    y_channel = ssc_a_ch
                elif vis_mode == "last":
                    y_channel = last_x_channel
            else:
                x_channel, y_channel = dimension_ids
            x_idx, y_idx = sample.get_channel_index(x_channel), sample.get_channel_index(y_channel)
            last_x_channel = x_channel

            n_total = sample.event_count
            parent_membership = get_parent_membership(gate_path, parent, n_total, gated_sample)
            parents = sample.get_events(source="xform", event_mask=parent_membership)
            x_parents, y_parents = parents[:, x_idx], parents[:, y_idx]

            # update min max values with 99% quantile
            subplot_title = f"{parent}>{gate_name}"
            if len(x_parents)>0:
                xmin = np.min([dict_lims[subplot_title][0,0], np.nanmin(x_parents)])
                xmax = np.max([dict_lims[subplot_title][0,1], np.nanmax(x_parents)])
            else:
                xmin, xmax = dict_lims[subplot_title][0]
            if len(y_parents)>0:
                ymin = np.min([dict_lims[subplot_title][1,0], np.nanmin(y_parents)])
                ymax = np.max([dict_lims[subplot_title][1,1], np.nanmax(y_parents)])
            else:
                ymin, ymax = dict_lims[subplot_title][1]
            dict_lims[subplot_title] = np.array([[xmin, xmax],[ymin, ymax]])

    return dict_lims

def get_parent_membership(
          gate_path: tuple[str],
          parent: str,
          n_total: int,
          gated_sample, # fk._models.gating_strategy.GatingResults
) -> np.ndarray:
    """Retrieve the boolean membership array for a given parent gate"""
    parent_path = list(gate_path)
    parent_path.remove(parent)
    if parent == "root":
        parent_membership = np.array([True,]*n_total)
    else:
        # gated_sample.get_gate_membership() does not work with quadrant gate in flowkit==1.3.0. Waiting for being debugged.
        parent_membership = gated_sample._raw_results[(parent, "/".join(parent_path))]["events"]
    return parent_membership

def draw_fig_verbose(
        session: fk.Session,
        scores: tuple[float],
        fig_path: Path,
        sample_idx: int,
) -> None:
    gs = session.gating_strategy
    sample = session.get_sample(session.get_sample_ids()[sample_idx])
    timeqc_title = "root>TimeQC"

    # Get FSC-A and SSC-A channel data
    fsc_a_ch = None
    ssc_a_ch = None
    ssc_h_ch = None
    for ch in sample.pnn_labels:
        if "SSC" in ch and "-A" in ch:
                ssc_a_ch = ch
        elif "SSC" in ch and "-H" in ch:
                ssc_h_ch = ch
        elif "FSC" in ch and "-A" in ch:
                fsc_a_ch = ch
    if fsc_a_ch is None or ssc_a_ch is None or ssc_h_ch is None:
        raise ValueError("FSC-A and SSC-A channel could not be found in sample.")
    
    gated_sample = gs.gate_sample(sample)
    gate_data = pd.DataFrame(gated_sample.report)
    num_vis = np.max(gate_data["level"])

    fig = plt.figure(
        figsize=(SUBPLOT_W * num_vis, SUBPLOT_H),
        facecolor=(0,0,0,0)
    )
    ax = fig.subplots(nrows=1, ncols=num_vis)
    # Assumes always num_vis>=2.
    for i in range(num_vis):
        tmp_df = gate_data[gate_data["level"]==(i+1)]

        # Retrieve gate info
        sample_id, gate_path, gate_name, gate_type, quad, parent, _, _, rel_perc, _= tmp_df.values[0]
        dimension_ids = gs.get_gate(gate_name).get_dimension_ids()
        if len(dimension_ids) == 1:
            x_channel = dimension_ids[0]
            y_channel = ssc_a_ch
        else:
            x_channel, y_channel = dimension_ids
        x_idx, y_idx = sample.get_channel_index(x_channel), sample.get_channel_index(y_channel)
        subplot_title = f"{parent}>{gate_name}"

        # Retrieve gated events
        # gated_sample.get_gate_membership() does not work with quadrant gate in flowkit==1.3.0. Waiting for being debugged.
        gate_membership = gated_sample._raw_results[(gate_name, "/".join(gate_path))]["events"]
        events = sample.get_events(source="xform", event_mask=gate_membership)
        x_events, y_events = events[:, x_idx], events[:, y_idx]

        # Retrieve those events gated out
        n_total = sample.event_count
        parent_membership = get_parent_membership(gate_path, parent, n_total, gated_sample)
        parent_only = np.logical_and(parent_membership, np.logical_not(gate_membership))
        parents = sample.get_events(source="xform", event_mask=parent_only)
        x_parents, y_parents = parents[:, x_idx], parents[:, y_idx]

        ax[i].scatter(x_parents, y_parents, marker="o", s=4, linewidths=0, alpha=0.2, facecolor=COLOR_BG, label=f"{parent}")
        ax[i].scatter(x_events, y_events, marker="o", s=4, linewidths=0, alpha=0.5, facecolor=COLOR_POS, label=f"{gate_name}: {rel_perc:.1f}%")
        ax[i].set_title(f"{subplot_title}")
        # ax[i].set_title(f"{subplot_title}\ndens_score:{scores[1]:.2f}, center_score:{scores[2]:.2f}")
        draw_gate(ax[i], session,sample_id, gate_name, gate_type, quad, xlims=[])
        
        # Save figure
        fig.suptitle(sample_id, )
        plt.tight_layout()
        fig.savefig(fig_path, dpi=100)
        plt.close(fig)
