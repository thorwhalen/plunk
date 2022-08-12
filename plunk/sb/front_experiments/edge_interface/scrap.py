import streamlit as st
from front.elements import InputBase, OutputBase
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY, OBJ_KEY
from dataclasses import dataclass
from streamlitfront.elements import TextInput, SelectBox, FloatSliderInput
from typing import Callable
from streamlitfront.base import mk_app


fname = "/Users/sylvain/Desktop/dev/otosense/plunk/plunk/sb/front_experiments/edge_interface/data/phone_small/1_2.wav"

if "mall" not in st.session_state:
    st.session_state["mall"] = dict(
        # train_audio={},
        # tag={},
        # unused_store={"to": "illustrate"},
        sound_list={"file": fname}
    )

mall = st.session_state["mall"]
# mall = dict(
#     # train_audio={},
#     # tag={},
#     # unused_store={"to": "illustrate"},
#     tag_sound_output={}
# )


@dataclass
class TaggedAudioPlayer(OutputBase):
    def render(self):
        sound, tag = self.output
        if not isinstance(sound, str):
            sound = sound.getvalue()

        st.audio(sound)


def show_sound(fname):
    return fname


@crudify(output_store="tagged_wf")
def tag_wf(wf: WaveForm, tag: str):
    return (wf, tag)


config_ = {
    APP_KEY: {"title": "Show audio"},
    # OBJ_KEY: {"trans": crudify},
    RENDERING_KEY: {
        "display_tag_sound": {
            "execution": {
                "inputs": {
                    "result": {
                        ELEMENT_KEY: SelectBox,
                        "options": mall["sound_list"],
                    },
                },
                "output": {
                    ELEMENT_KEY: TaggedAudioPlayer,
                },
            },
        },
        Callable: {
            "execution": {
                "inputs": {
                    "save_name": {
                        ELEMENT_KEY: TextInput,
                        NAME_KEY: "Save output as",
                    },
                }
            },
        },
    },
}

app = mk_app(
    [show_sound],
    config=config_,
)
app()
# st.audio(mall["tag_sound_output"]["s3"][0])
#'execution': {'inputs': {'p': {ELEMENT_KEY: FloatSliderInput,}},}
st.write(mall)
