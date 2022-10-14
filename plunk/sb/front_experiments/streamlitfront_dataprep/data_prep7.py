from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from collections.abc import Callable

from streamlitfront import mk_app, binder as b
from streamlitfront.elements import SelectBox
from typing import Any
from streamlitfront.elements import MultiSourceInput
import streamlit as st
from front.elements import InputBase
from i2 import Sig
from dataclasses import dataclass
from streamlitfront.elements import TextInput, SelectBox, ExecSection, TextOutput
from functools import partial
from front.crude import Crudifier
from streamlitfront.data_binding import BoundData
from i2.deco import FuncFactory
from plunk.sb.front_experiments.streamlitfront_dataprep.data_prep2 import (
    # DFLT_WF_PATH,
    # DFLT_ANNOT_PATH,
    data_from_wav_folder,
    data_from_csv,
    store_to_key_fvs,
    key_fvs_to_tag_fvs,
    mk_Xy,
)
from odat.mdat.vacuum import DFLT_CHUNKER, DFLT_FEATURIZER


# # ============ MALL ===============
if not b.mall():
    b.mall = dict(func_store={})

mall = b.mall()


def foo(x: str, y: str):
    return x + y


def bar(msg: str):
    return msg


# def factory(func):
#     result = FuncFactory(func)
#     return result


DFLT_CHUNKER_MAKER = lambda: DFLT_CHUNKER
DFLT_FEATURIZER_MAKER = lambda: DFLT_FEATURIZER
DFLT_WF_PATH = "/Users/sylvain/Dropbox/Otosense/VacuumEdgeImpulse/"
DFLT_ANNOT_PATH = "/Users/sylvain/Dropbox/sipyb/Testing/data/annots_vacuum.csv"
metadata = {
    "FixedSizeChunker": {"func": DFLT_CHUNKER, "out": "chks"},
    # 'FixedSizeChunker100': {'out': 'chks'},
    # 'ThresholdChunker': {'out': 'chks'},
    "FixedSizeChunkerMaker": {"func": DFLT_CHUNKER_MAKER, "out": "chunker"},
    "FeaturizerMaker": {"func": DFLT_FEATURIZER_MAKER, "out": "featurizer"},
    # 'key_fvs_to_tag_fvs': {'func': key_fvs_to_tag_fvs},
    # 'Featurizer': {'func': DFLT_FEATURIZER, 'out': 'fvs'},
    "store_to_key_fvs": {"func": store_to_key_fvs, "out": "key_fvs"},
    "key_fvs_to_tag_fvs": {"func": key_fvs_to_tag_fvs, "out": "tag_fv_iterator"},
    "WfStoreMaker": {
        "func": data_from_wav_folder,
        "out": "wf_store",
        "bind": {"filepath": "wf_filepath"},
    },
    "AnnotsStoreMaker": {"func": data_from_csv, "out": "annots_df"},
    "mk_Xy": {"func": mk_Xy},
}
data = list(metadata.keys())


crudifier_output = Crudifier(output_store="func_store", mall=mall)


def my_map(func_name):
    f = metadata[func_name]["func"]
    return f


def expand_names(names):
    return {name: {ELEMENT_KEY: TextInput} for name in names}


def populate_pages():
    value = b.selected_name()
    func = metadata[value]["func"]
    func = crudifier_output(func)
    b.list_funcs().append(func)


if not b.selected_func():
    b.selected_func = "foo"

if not b.list_funcs():
    b.list_funcs = [my_map]


def get_kwargs(**kwargs):
    return kwargs


if __name__ == "__main__":
    app = mk_app(
        b.list_funcs(),
        # [my_map, FuncFactory(foo)],
        config={
            APP_KEY: {"title": "Rendering map"},
            RENDERING_KEY: {
                "my_map": {
                    "execution": {
                        "inputs": {
                            "func_name": {
                                ELEMENT_KEY: SelectBox,
                                "options": data,
                                "value": b.selected_name,
                                "on_value_change": populate_pages,
                            },
                        }
                    }
                },
            },
        },
    )
    app()
