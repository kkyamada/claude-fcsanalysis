import os
from pathlib import Path
# thirdparty
import pandas as pd
# local
from fcs_utils.fluor50 import extract_day_rep

def retrieve_results(
        output_path: Path | str,
        target_gate: str,
        summary_file: str="summary_processed.csv",
        sample_mapper: dict = {},
) -> pd.DataFrame:
    
    output_path = Path(output_path)
    df = pd.DataFrame()
    for rep in os.listdir(output_path):
        rep = output_path / Path(rep)
        if rep.is_dir():
            data_path = rep / Path(summary_file)
            # tmp_df is an aggregated output of fk.gated_sample report.
            tmp_df = pd.read_csv(data_path)
            tmp_df = tmp_df[tmp_df["gate_name"]==target_gate]

        day, rep = extract_day_rep(str(data_path))
        tmp_df["day"], tmp_df["rep"] = [day,]*len(tmp_df), [rep,]*len(tmp_df)
        if len(df)==0:
            df = tmp_df.copy()
        else:
            df = pd.concat([df, tmp_df], axis=0).reset_index(drop=True)

    df["id"] = df["sample_id"].str.strip(".fcs")
    if not len(sample_mapper)==0:
        df["sample_name"] = df["id"].apply(lambda x: sample_mapper[x])
    return df