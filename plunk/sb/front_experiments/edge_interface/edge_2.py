from front.spec_maker import APP_KEY, RENDERING_KEY, ELEMENT_KEY
from front.elements import FLOAT_INPUT_SLIDER_COMPONENT
from elements import SimpleList, SimpleText
from streamlitfront.base import mk_app
from meshed import code_to_dag, DAG
from front.elements import (
    FILE_UPLOADER_COMPONENT,
    AUDIO_RECORDER_COMPONENT,
    MULTI_SOURCE_INPUT_CONTAINER,
    FrontComponentBase,
)
from typing import Iterable
from front.spec_maker import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from streamlitfront.examples.graph_component import Graph


WaveForm = Iterable[int]


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
                        ELEMENT_KEY: FILE_UPLOADER_COMPONENT,
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
