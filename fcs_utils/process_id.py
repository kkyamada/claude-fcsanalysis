import argparse
import logging
import os
from pathlib import Path

import flowkit as fk
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

def setup_fcsprocess(
        input_dir: Path,
        color_dict: dict,
) -> np.ndarray:
    # TODO: Some colors need to be changed
    mypalette = [
        [80,168,180],
        [226,112,60],
        [141,234,181],
        [211,156,186],
        [245,204,92],
        [146,168,187],
        [104,69,200],
        [133,99,84],
        [172,208,83],
        [189,50,75],
        [250,250,250],
    ]
    mypalette = np.array(mypalette) / 255

    overwrite_sampleid(input_dir, color_dict)
    logger.info("Finished setting up.")
    return mypalette


def overwrite_sampleid(
        input_dir: Path,
        color_dict: dict,
        verbose: bool=False,
)-> None:
    """
    Function to overwrite sample id in the meta data within ".fcs" files with their filenames.
    i.e.) FILENAME.fcs with sample_id FILENAME will be overwritten as FILENAME.fcs with sample_id=FILENAME
    """
    if verbose:
        print(f"Processing .fcs files in {input_dir}")
    else:
        logger.info(f"Processing .fcs files in {input_dir}")

    for sample in os.listdir(input_dir):
        if not ".fcs" in sample:
            continue
        sample_path = os.path.join(input_dir, sample)
        s = fk.Sample(sample_path, ignore_offset_error=True)
        meta = s.get_metadata()
        meta["$FIL"] = sample
        s.metadata = meta

        # Update pnn and pns labels with precast names in color_info.csv
        # This is inteded to overwrite names that are incompatible with fcs format (such as those from ZE5)
        for i in range(len(s.channels)):
            pnn = s.pnn_labels[i]
            if pnn[-2:] in ["-A", "-W", "-H"]:
                pnn_stem, pnn_type = pnn[:-2], pnn[-2:]
            else:
                continue
            for key, val in color_dict.items():
                if pnn_stem in str(val):
                    s.pnn_labels[i] = key + pnn_type

        for i in range(len(s.channels)):
            pnn, pns = s.pnn_labels[i], s.pns_labels[i]
            if pns[-2:] in ["-A", "-W", "-H"]:
                pns_stem, pns_type = pns[:-2], pns[-2:]
            else:
                continue
            for key, val in color_dict.items():
                if pns_stem in str(val):
                    s.pns_labels[i] = key + pns_type
        # Overwrite channel info
        s.channels["pnn"] = s.pnn_labels
        s.channels["pns"] = s.pns_labels
        s.export(filename=sample_path, source="raw", include_metadata=True,)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True,
                        help="Path to the input data directory that contains fcs files")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    overwrite_sampleid(args.input_dir, args.verbose)