from typing import Iterable
from meshed import code_to_dag, DAG
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY, OBJ_KEY

from front.crude import prepare_for_crude_dispatch
from streamlitfront.elements import TextInput

from streamlitfront.base import mk_app
from streamlitfront.examples.util import Graph
from streamlitfront.elements import (
    AudioRecorder,
    FileUploader,
    MultiSourceInputContainer,
)
import streamlit as st

param_to_mall_map = dict(train_audio="train_audio", tag="tag_store")

mall = dict(
    train_audio={},
    tag_store={},
    # unused_store={"to": "illustrate"},
)


def crudify(funcs):
    for func in funcs:
        yield prepare_for_crude_dispatch(
            func, param_to_mall_map=param_to_mall_map, mall=mall
        )


WaveForm = Iterable[int]


@code_to_dag
def tag_sound(train_audio: WaveForm, tag):
    # mall["tag_store"] = tag
    result = tag_sound(train_audio, tag)


config_ = {
    APP_KEY: {"title": "Simple Real Audio ML"},
    # OBJ_KEY: {"trans": crudify},
    RENDERING_KEY: {
        DAG: {
            # "description": {"content": "A very simple learn model example."},
            "execution": {
                "inputs": {
                    "train_audio": {
                        ELEMENT_KEY: MultiSourceInputContainer,
                        "From a file": {
                            ELEMENT_KEY: FileUploader,
                            "type": "wav",
                        },
                        "From the microphone": {ELEMENT_KEY: AudioRecorder},
                    },
                    "tag_store": {
                        ELEMENT_KEY: TextInput,
                    },
                },
            },
            "graph": {
                ELEMENT_KEY: Graph,
                NAME_KEY: "Flow",
            },
        }
    },
}

app = mk_app([tag_sound], config=config_)
app()
st.write(mall)
