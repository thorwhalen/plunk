# TODO : refactor tabled to include the changes below
# the class below is a copy from tabled
# the json access is not very convenient the way it is

"""
A  (key-value) data-object-layer to get (pandas) tables from a variety of sources with ease.
"""
from functools import partial
from io import BytesIO
import os
import pickle

import pandas as pd
from dol import wrap_kvs
from lined import Pipe
from tabled import (
    DfLocalFileReader,
    dflt_ext_mapping,
)


DFLT_EXT_SPECS = {}


def set_of_concatenated_col_names(store):
    col_names = []
    for key in store:
        col_name = "-".join(list(store[key].columns))
        col_names.append(col_name)

    return set(col_names)


def df_from_json(data, ext_specs={"orient": "index"}, **kwargs):
    """Get a dataframe from a (data, ext) pair"""

    kwargs = dict(ext_specs, **kwargs)
    return pd.read_json(data, **kwargs).T  # modified from tabled


dflt_ext_mapping["json"] = df_from_json

DFLT_METADATA_COLS = [
    "dataType",
    "deviceId",
    "motorId",
    "tempe",
    "tempm",
    "tenantId",
    "timestamp",
    "ts",
    "tsr",
    "vbat",
]
DFLT_DATA_COLS = ["flux", "vibx", "vibz"]


def filter_store_by_outer_keys(store, outer_keys=DFLT_METADATA_COLS):
    nstore = wrap_kvs(store, obj_of_data=lambda data: data[outer_keys])
    return nstore


metadata_store = partial(filter_store_by_outer_keys, outer_keys=DFLT_METADATA_COLS)


def process_dict(d):
    return {k: v[0] for k, v in d.items()}


def data_store(store):
    filt = lambda data: data[DFLT_DATA_COLS]
    dict_transform = lambda data: process_dict(data.to_dict())
    to_df = pd.DataFrame
    pipe = Pipe(filt, dict_transform, to_df)
    nstore = wrap_kvs(store, obj_of_data=pipe)

    return nstore


if __name__ == "__main__":
    import os.path

    # Path
    path = "~/Dropbox/_odata/sound/induction_motor_data/"
    full_path = os.path.expanduser(path)

    dflt_ext_mapping["json"] = df_from_json

    # store
    store = DfLocalFileReader(full_path)

    # try one key
    key = list(store.keys())[0]
    print(store[key])
