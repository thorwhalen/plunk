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

from meshed import DAG
from sklearn.preprocessing import MinMaxScaler

DFLT_CHK_SIZE = 4
DFLT_NDIGITS = None


def chunker(wf, chk_size=DFLT_CHK_SIZE):
    """An iterable of fixed size chunks of wf"""
    yield from zip(*[iter(wf)] * chk_size)


def featurizer(chk, ndigits=DFLT_NDIGITS):
    """Compute a feature vector from a waveform chunk"""
    from statistics import stdev

    # note: surrounding single number with [...] because a vector is expected
    return [round(stdev(map(float, chk)), ndigits)]


def wfs(data_src=10):
    """Get an iterable of waveforms from the data source"""
    seed = [1, 2, 3, 5, 4, 2, 1, 4, 3]
    yield seed
    yield [x + 10 for x in seed] + [1, 2, 3, 7]
    # and finally, an outlier (the difference, is that we have high variance)
    yield [x * data_src for x in seed]


def chk_gen(chunker, wfs):
    return (chunker(wf) for wf in wfs)


def fv_gen(chunker_gen, featurizer):
    """apply _featurizer to an iterable"""
    return (featurizer(chk) for chk in chunker_gen)


# featurizer = partial(map, _featurizer)

from sklearn.preprocessing import MinMaxScaler


def learn(fv_gen, learner=MinMaxScaler()):
    """"""
    return learner.fit(list(fv_gen))


data = ["foo", "bar"]


def foo(x: str, y: str):
    return x + y


def bar(msg: str):
    return msg


data = ["foo", "bar"]
metadata = {"foo": foo, "bar": bar}


# crudifier_output = Crudifier(output_store="func_store", mall=mall)


def my_map(func, kwargs):
    f = metadata[func]
    return partial(f, **kwargs)
    # return f, kwargs


# def expand_names(names):
#     return {name: {ELEMENT_KEY: TextInput} for name in names}


def populate_list_funcs():
    value = b.selected_func()
    b.list_funcs().append(metadata[value])


if not b.selected_func():
    b.selected_func = "foo"

if not b.list_funcs():
    b.list_funcs = [my_map]

data = ["chunker", "featurizer"]
metadata = {"chunker": chunker, "featurizer": featurizer}


if __name__ == "__main__":
    app = mk_app(
        b.list_funcs(),
        config={
            APP_KEY: {"title": "Rendering map"},
            RENDERING_KEY: {
                "my_map": {
                    "execution": {
                        "inputs": {
                            "func": {
                                ELEMENT_KEY: SelectBox,
                                "options": data,
                                "value": b.selected_func,
                                "on_value_change": populate_list_funcs,
                            },
                            # "kwargs": {
                            #     ELEMENT_KEY: KwargsInput,
                            #     "func_sig": Sig(metadata[b.selected_func()]),
                            # },
                        }
                    }
                },
            },
        },
    )
    app()
