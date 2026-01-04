import argparse
import math
import os
import re
from typing import Literal, Dict, List, Tuple, Union
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon as SPolygon
import seaborn as sns
from scipy.stats import mode
import fcsparser

mypalette = [[80,168,180],
                    [226,112,60],
                    [141,234,181],
                    [211,156,186],
                    [245,204,92],
                    [146,168,187],
                    [104,69,200],
                    [133,99,84],
                    [172,208,83],
                    [189,50,75],
                    [250,250,250]
                    ]
mypalette = np.array(mypalette) / 255

def extract_inner_points(
        polygon: SPolygon,
        df: pd.DataFrame,
        data: pd.DataFrame,
        column_a: str,
        column_b: str,
        )-> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Function to extract inner points of a plot within a polygon.
    column_a and column_b are selected from a column of df to define x and y axes of the plot.
    returns:
    - df_extracted that includes all extracted inner points.
    - df_vis that includes outer points that were not extracted.
    """
    indices = []
    for i, row in df.iterrows():
        point = Point(row[column_a], row[column_b])
        if polygon.contains(point):
            indices.append(i)
    df_extracted = df.loc[indices]
    df_vis = df_extracted.merge(data, how="outer", indicator=True)
    df_vis = df_vis[df_vis["_merge"] == "right_only"]
    df_vis = df_vis.drop(columns=["_merge"])
    return df_extracted, df_vis

def apply_compensation(
        data: pd.DataFrame,
        df_comp: pd.DataFrame,
) -> pd.DataFrame:
    """
    Function to apply fluorescence compensation on the data using df_comp.
    """
    for channel_orig in df_comp["Channel"]:
        for channel_sub in df_comp["Channel"]:
            val = df_comp[df_comp["Channel"]==channel_orig][channel_sub].values[0]
            if val>0:
                col_name = f"{channel_orig}-A"
                col_name2 = f"{channel_sub}-A"
                data[col_name] = data[col_name] - data[col_name2]*val/100
    return data

def annotate_fig(
        data: pd.DataFrame,
        info_dict: Dict,
        polygon_coord: List[np.ndarray],
        ax: Axes,
        perc_extracted: float,
        text_position: str,
        relative_margin: float = 0.03,
) -> None:
    # Assuming rectangle region
    if info_dict["x_lims"] is not None:
        x_range = info_dict["x_lims"]
        x_offset = x_range[0]
        x_range = x_range[1] - x_range[0]
    else:
        x_range = [np.min(data[info_dict["x_column"]]), np.max(data[info_dict["x_column"]])]
        x_offset = x_range[0]
        x_range = x_range[1] - x_range[0]
    if np.min(np.array(polygon_coord)[:,0]) > x_offset:
        x_offset = np.min(np.array(polygon_coord)[:,0])
    
    if info_dict["x_scale"] == "log" or info_dict["x_scale"] == "symlog":
        x_coord = x_offset + 10**(np.log10(x_range) * relative_margin)
    else:
        x_coord = x_offset + x_range * relative_margin
    
    if info_dict["y_lims"] is not None:
        y_lims = info_dict["y_lims"]
        y_range = y_lims[1] - y_lims[0]
    else:
        y_lims = [np.min(data[info_dict["y_column"]]), np.max(data[info_dict["y_column"]])]
        y_range = y_lims[1] - y_lims[0]
    
    if info_dict["y_scale"] == "log" or info_dict["y_scale"] == "symlog":
        if "bottom" in text_position:
            y_coord = 10**(np.log10(np.min(np.array(polygon_coord)[:,1])) + np.log10(y_range) * relative_margin)
            if y_coord <= y_lims[0]:
                y_coord = 10**(np.log10(y_lims[0]) + np.log10(y_range) * relative_margin)
        else:
            y_coord = 10**(np.log10(np.max(np.array(polygon_coord)[:,1])) + np.log10(y_range) * relative_margin)
            if y_coord >= y_lims[1]:
                y_coord = 10**(np.log10(y_lims[1]) - np.log10(y_range) * relative_margin)
    else:
        if "bottom" in text_position:
            y_coord = np.min(np.array(polygon_coord)[:,1]) + y_range * relative_margin
            if y_coord <= y_lims[0]:
                y_coord = y_lims[0] + y_range * relative_margin
        else:
            y_coord = np.max(np.array(polygon_coord)[:,1]) + y_range * relative_margin
            if y_coord >= y_lims[1]:
                y_coord = y_lims[1] - y_range * relative_margin

    if text_position == "left":
        ax.text(x=x_coord, y=y_coord, s=f"%{info_dict['fig_annot']}: {perc_extracted:.2f}",
            fontdict={"fontsize": 12,
                        "weight": "bold",
                        "backgroundcolor": [1.0,1.0,1.0,0.7],
                        "fontname":"sans-serif"})
    else:
        x_coord = x_offset + x_range
        ax.text(x=x_coord, y=y_coord, s=f"%{info_dict['fig_annot']}: {perc_extracted:.2f}", ha="right",
            fontdict={"fontsize": 12,
                        "weight": "bold",
                        "backgroundcolor": [1.0,1.0,1.0,0.7],
                        "fontname": "sans-serif"})
    return ax

def determine_threshold(
        specimens: List[Union[str, Path]],
        thresh_column: str,
        threshold_perc: float,
        threshold_direction: str,
        threshold_info_num: int,
        polygon_coordinates: np.ndarray,
        info_list: List[Dict],
        mock_keyword: str = "Mock",
        text_position: str = "left",
        df_comp: pd.DataFrame = pd.DataFrame([]),
        verbose: bool = False,
        ) -> float:
    """
    Docstring for determine_threshold
    """
    print("Defining the thresholds using Mock samples.")
    print(f"Assuming the mock sample filename includes {mock_keyword}")

    thresh_values = []
    for tmp_path in specimens:
        if mock_keyword in tmp_path:
            print(f"Found {mock_keyword} in {tmp_path}")
            figtitle = tmp_path.split("/")[-1]
            figtitle = figtitle.split(" ")[-1].split(".")[0]
            
            fig = plt.figure(figsize=(6*len(info_list),4),
                            facecolor=(0,0,0))
            ax = fig.subplots(nrows=1, ncols=len(info_list))
            meta, data = fcsparser.parse(tmp_path, meta_data_only=False, reformat_meta=True)
            print(f"Available channels : {meta['_channel_names_']}")

            # Applying Compensation
            if len(df_comp)>0:
                data = apply_compensation(data, df_comp)
            
            # Visualize Plots
            for j, [polygon_coord, info_dict] in enumerate(zip(polygon_coordinates, info_list)):
                if j==0:
                    # First plot (x=FSC-A vs y=SSC-A)
                    sns.scatterplot(data=data,
                                    x=info_dict["x_column"],
                                    y=info_dict["y_column"],
                                    ax=ax[j],
                                    color=info_dict["scatter_color"],
                                    s=2,
                                    )
                else:
                    # Plotting outer points
                    sns.scatterplot(data=df_vis,
                                    x=info_dict["x_column"],
                                    y=info_dict["y_column"],
                                    ax=ax[j],
                                    color=mypalette[7],
                                    alpha=0.3,
                                    s=2,
                                    )
                    # Plotting inner points
                    sns.scatterplot(data=data_extracted,
                                    x=info_dict["x_column"],
                                    y=info_dict["y_column"],
                                    ax=ax[j],
                                    color=info_dict["scatter_color"],
                                    s=2,
                                    )
                polygon = SPolygon(polygon_coord)
                polygon_patch = Polygon(polygon_coord, fill=None, edgecolor="r")
                ax[j].set_facecolor((1,1,1))
                ax[j].spines["right"].set_visible(False)
                ax[j].spines["top"].set_visible(False)
                if not info_dict["x_lims"] is None:
                    ax[j].set_xlim(info_dict["x_lims"])
                if not info_dict["y_lims"] is None:
                    ax[j].set_ylim(info_dict["y_lims"])
                if not info_dict["x_scale"] is None:
                    ax[j].set_xscale(info_dict["x_scale"])
                if not info_dict["y_scale"] is None:
                    ax[j].set_yscale(info_dict["y_scale"])
                ax[j].add_patch(polygon_patch)
                
                if j==0:
                    data_extracted, df_vis = extract_inner_points(polygon,
                                                                  data,
                                                                  data,
                                                                  info_dict["x_column"],
                                                                  info_dict["y_column"],
                                                                  )
                else:
                    num_points = len(data_extracted)
                    if j==threshold_info_num:
                        if threshold_direction=="lower":
                            data_tmp = data_extracted.sort_values(by=thresh_column, ascending=True).reset_index(drop=True)
                        else:
                            data_tmp = data_extracted.sort_values(by=thresh_column, ascending=False).reset_index(drop=True)
                        thresh_num = int(num_points*threshold_perc/100)
                        print(f"Column: {thresh_column}")
                        print(f"thresh_num: {thresh_num}")
                        thresh_value = data_tmp[thresh_column].iloc[thresh_num]
                        print(f"thresh_value: {thresh_value:3e}")
                        thresh_values.append(thresh_value)
                    data_extracted, df_vis = extract_inner_points(polygon, data_extracted, data, info_dict["x_column"], info_dict["y_column"])
                    perc_extracted = len(data_extracted)/num_points*100

                    if not info_dict["fig_annot"] is None:
                        ax[j] = annotate_fig(
                                data,
                                info_dict,
                                polygon_coord,
                                ax[j],
                                perc_extracted,
                                text_position,
                                relative_margin = 0.03,
                        )
    if threshold_direction=="lower":
        return np.min(thresh_values)
    elif threshold_direction=="higher":
        return np.max(thresh_values)

def process_data(
        specimens: List[pd.DataFrame],
        polygon_coordinates: List[np.ndarray],
        info_list: List[Dict],
        save_fig: bool=False,
        save_data: bool=False,
        fig_dir: str="./figures",
        text_position: str="left",
        df_comp: pd.DataFrame=pd.DataFrame([]),
        ):
    """
    Docstring for process_data
    """
    dict_df = {}
    saved_info = pd.DataFrame([])
    if not os.path.exists(fig_dir):
      os.makedirs(fig_dir)

    for tmp_path in specimens:
        print(f"Processing {tmp_path}")
        figtitle = tmp_path.split("/")[-1]
        figtitle = ".".join(figtitle.split(" ")[-1].split(".")[:-1])
        try:
            rep = re.search(r"rep[0-9]", tmp_path).group()
        except:
            rep = ""
        try:
            day = re.search(r"[dD]ay[0-9]", tmp_path).group()
        except:
            day = ""
        tmp_info = {"sample":figtitle,
                    "rep":rep,
                    "day":day,
                    }
        
        fig = plt.figure(figsize=(6*len(info_list),4),
                        facecolor=(0,0,0,))
        ax = fig.subplots(nrows=1, ncols=len(info_list))
        meta, data = fcsparser.parse(tmp_path, meta_data_only=False, reformat_meta=True)
        # Applying Compensation
        if len(df_comp)>0:
            data = apply_compensation(data, df_comp)

        for j, [polygon_coord, info_dict] in enumerate(zip(polygon_coordinates, info_list)):
            if j==0:
                sns.scatterplot(data=data,
                                x=info_dict["x_column"],
                                y=info_dict["y_column"],
                                ax=ax[j],
                                color=info_dict["scatter_color"],
                                s=2,
                                )
            else:
                sns.scatterplot(data=data_extracted,
                                x=info_dict["x_column"],
                                y=info_dict["y_column"],
                                ax=ax[j],
                                color=info_dict["scatter_color"],
                                s=3,
                                )
            polygon = SPolygon(polygon_coord)
            polygon_patch = Polygon(polygon_coord, fill=None, edgecolor="r")
            ax[j].set_facecolor((1,1,1))
            ax[j].spines["right"].set_visible(False)
            ax[j].spines["top"].set_visible(False)
            if not info_dict["x_lims"] is None:
                ax[j].set_xlim(info_dict["x_lims"])
            if not info_dict["y_lims"] is None:
                ax[j].set_ylim(info_dict["y_lims"])
            if not info_dict["x_scale"] is None:
                ax[j].set_xscale(info_dict["x_scale"])
            if not info_dict["y_scale"] is None:
                ax[j].set_yscale(info_dict["y_scale"])
            ax[j].add_patch(polygon_patch)
            if j==0:
                tmp_info["num_total"] = len(data)
                data_extracted, _ = extract_inner_points(polygon,
                                                         data,
                                                         data,
                                                         info_dict["x_column"],
                                                         info_dict["y_column"],
                                                         )
                tmp_info[f"num_extracted_polygon{j+1}"] = len(data_extracted)
                perc_extracted = len(data_extracted)/len(data)*100
                tmp_info[f"perc_extracted_polygon{j+1}"] = perc_extracted
            else:
                num_points = len(data_extracted)
                data_extracted, _ = extract_inner_points(polygon,
                                                         data_extracted,
                                                         data,
                                                         info_dict["x_column"],
                                                         info_dict["y_column"],
                                                         )
                if j==1:
                    dict_df[figtitle] = data_extracted
                perc_extracted = len(data_extracted)/num_points*100

                if not info_dict["fig_annot"] is None:
                    tmp_info[f"num_{info_dict['fig_annot']}"] = len(data_extracted)
                    tmp_info[f"perc_{info_dict['fig_annot']}"] = perc_extracted
                    # Assuming rectangle region
                    ax[j] = annotate_fig(data,
                                 info_dict,
                                 polygon_coord,
                                 ax[j],
                                 perc_extracted,
                                 text_position,
                                 )
                else:
                    tmp_info[f"num_extracted_polygon{j+1}"] = len(data_extracted)
                    tmp_info[f"perc_extracted_polygon{j+1}"] = perc_extracted

        fig.suptitle(f"{figtitle}", fontsize=16)
        if save_fig:
            fig.savefig(f"{fig_dir}/{figtitle}.png", dpi=300)
        
        if len(saved_info)==0:
            saved_info = pd.DataFrame([tmp_info])
        else:
            new_df = pd.DataFrame([tmp_info])
            saved_info = pd.concat([saved_info, new_df], axis=0)
        plt.close()
    
    if save_data:
        return [dict_df, saved_info]
    else:
        return [{}, saved_info]

def main(args):
    # Detecting input data
    print(f"Processing data in {args.input_dir}")
    dir_name = args.input_dir.split("/")[-1]
    list_files = os.listdir(args.input_dir)
    specimens = []
    for i in list_files:
        tmp_path = os.path.join(args.input_dir, i)
        if i.endswith(".fcs"):
            specimens.append(tmp_path)
        elif i.endswith(".csv"):
            compfile = tmp_path
            df_comp = pd.read_csv(compfile)
    specimens.sort()
    if not os.path.exists(os.path.join(args.output_dir, "./figures", dir_name)):
        os.makedirs(os.path.join(args.output_dir, "./figures", dir_name))

    thresh_value_mCherry = 0
    polygon_coordinates = [
        # FSC-A vs SSC-A
        np.array([[1083730.86784495,  166543.7484262 ],
        [1338798.81935135,  221870.1246444 ],
        [1856580.45062592,  358742.70482059],
        [2939777.28904265, 1180121.91738143],
        [2139702.87258903, 1195049.04624178],
        [1060249.21795605,  533811.07113043],
        [ 832428.16461548,  243671.62870918],
        [ 852157.88183109,  157901.67865493]]),
        # FSC-A vs FSC-H
        np.array([[ 810649.06994437,  543163.9465631 ],
        [ 964488.47261082,  516258.3261507 ],
        [1994101.26931907,  760001.536019  ],
        [2354548.91916692,  908892.96663505],
        [2294988.87230394, 1198082.86921558],
        [1518091.00982468, 1108583.28440283],
        [ 967257.88363558,  784790.40735147],
        [ 758818.98898419,  590499.23877722]]),
        # B525-A vs Y610-A
        # mCherryOFF box:
        np.array([[1.0*1e1,thresh_value_mCherry], [1.0*1e7, thresh_value_mCherry], [1.0*1e7,1.0*1e1], [1.0*1e1, 1.0*1e1]]),
        # np.array([[1.0*1e1,1], [1.0*1e7, 1], [1.0*1e7,1.0*1e7], [1.0*1e1, 1.0*1e7]]),
        # B525-A vs Y610-A
        # GFPOFF box:
        # np.array([[1.0*1e1,1.0*1e1], [thresh_value_GFP, 1.0*1e1], [thresh_value_GFP,1.0*1e7], [1.0*1e1, 1.0*1e7]]),
    ]
    info_list = [{"x_column":"FSC-A", "y_column":"SSC-A",
                  "x_lims":[1e5, 5.0*1e6], "y_lims":[1e5, 3.0*1e6], "x_scale":"log", "y_scale":"log",
                  "scatter_color":mypalette[5], "fig_annot": None},
            {"x_column":"FSC-A", "y_column":"FSC-H",
                  "x_lims":[3.0*1e5, 5.0*1e6], "y_lims":[3.0*1e5, 3.0*1e6], "x_scale":"log", "y_scale":"log",
                  "scatter_color":mypalette[5], "fig_annot": None},
            {"x_column":"B525-A", "y_column":"Y610-A",
                  "x_lims":[1e2, 1e6], "y_lims":[1e1, 1e6], "x_scale":"log", "y_scale":"log",
                  "scatter_color":mypalette[3], "fig_annot": "mCherryOFF",
                  "x_label": "GFP", "y_label":"mCherry",},]
    threshold_perc = 2.5
    threshold_info_num = 2
    threshold_direction = "lower"
    thresh_column = "Y610-A"
    mock_keyword="Mock"

    thresh_value_mCherry = determine_threshold(specimens, 
                                               thresh_column, 
                                               threshold_perc,
                                               threshold_direction, 
                                               threshold_info_num, 
                                               polygon_coordinates, 
                                               info_list,
                                               mock_keyword,
                                               text_position="right",
                                               )
    polygon_coordinates[2] = np.array([[1.0*1e1, thresh_value_mCherry],
                                       [1.0*1e7, thresh_value_mCherry],
                                       [1.0*1e7, 1.0*1e1],
                                       [1.0*1e1, 1.0*1e1]])

    dict_df, saved_df = process_data(specimens,
                                 polygon_coordinates,
                                 info_list,
                                 save_fig=True,
                                 save_data=True,
                                 fig_dir=os.path.join(args.output_dir, "./figures", dir_name),
                                 text_position="right",)
    plt.clf()
    saved_df = saved_df.reset_index(drop=True)
    saved_df.to_csv(os.path.join(args.output_dir, f"curated_{dir_name}.csv"), index=False)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True,
                        help="Path to input data directory")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="Path to output directory")
    args = parser.parse_args()
    main(args)