import streamlit as st
import io
import numpy as np
import soundfile as sf


from front.spec_maker import APP_KEY, RENDERING_KEY, ELEMENT_KEY
from streamlitfront.base import mk_app
from meshed import code_to_dag, DAG
from front.elements import (
    FileUploaderBase,
)
from streamlitfront.elements import implement_input_component
from typing import Iterable
from streamlitfront.examples.graph_component import Graph


WaveForm = Iterable[int]

WavUploader = implement_input_component(
    FileUploaderBase,
    component_factory=st.file_uploader,
    input_value_callback=lambda input, self: wav_complex_display(input),
)


def discretize(arr, num_windows=200):
    step = len(arr) // num_windows
    dis = [np.mean(arr[i * step : i * (step + 1)]) for i in range(num_windows)]
    return np.array(dis)


def wav_complex_display(uploaded_file):
    bytes = bytes_from_uploaded(uploaded_file)
    st.audio(bytes)
    arr = arr_from_bytes(bytes)
    arr_d = discretize(arr)
    st.write(f"length = {len(arr)}")
    st.bar_chart(arr_d)


def arr_from_bytes(bytes, dtype="int16"):
    arr = sf.read(bytes, dtype=dtype)[0]

    return arr


def bytes_from_uploaded(uploaded_file):
    uploaded_file.seek(0)
    result = io.BytesIO(uploaded_file.read())

    return result


@code_to_dag
def display_wf(wf: WaveForm):
    result = display_wf(wf)


config_ = {
    APP_KEY: {"title": "Simple Load and Display"},
    RENDERING_KEY: {
        DAG: {
            "execution": {
                "inputs": {
                    "wf": {
                        # ELEMENT_KEY: FILE_UPLOADER_COMPONENT,
                        ELEMENT_KEY: WavUploader,
                        "type": "wav",
                    },
                }
            },
            "graph": {
                ELEMENT_KEY: Graph,
                NAME_KEY: "Flow",
            },
        }
    },
}

app = mk_app([display_wf], config=config_)
app()
