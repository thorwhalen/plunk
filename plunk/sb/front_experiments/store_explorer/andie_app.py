"""An app that loads wav file from local folder"""

from dataclasses import dataclass

import streamlit as st
from front.elements import OutputBase
from typing import Mapping
from functools import partial
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY

from front.crude import Crudifier

from streamlitfront import mk_app, binder as b
from streamlitfront.elements import SuccessNotification, SelectBox
from streamlitfront.elements import FileUploader

from plunk.ap.store_explorer.store_explorer_element import StoreExplorer


@dataclass
class StoreExplorer(OutputBase):
    def render(self):
        store = self.output
        print(f"{store=}")
        # Store the initial value of widgets in session state
        if "depth_keys" not in st.session_state:
            st.session_state.depth_keys = []
            st.session_state.render_count = 0

        print(f"Start {st.session_state.render_count=} {st.session_state.depth_keys=}")

        col1, col2 = st.columns(2)
        with col1:
            st.write("# Keys")
            for i in range(len(st.session_state.depth_keys) + 1):
                if i == 0:
                    d = store
                elif (
                    len(st.session_state.depth_keys) == i
                    and (dk := st.session_state.depth_keys[i - 1]) is not None
                ):
                    d = d[dk]
                else:
                    break

                if isinstance(d, dict):
                    options = [None, *d]
                    k = st.selectbox(key := f"depth_{i}", options=options, key=key)
                    st.session_state.depth_keys = [*st.session_state.depth_keys[:i], k]
                if isinstance(d, list):
                    options = [None, *(j for j in range(len(d)))]
                    k = st.selectbox(key := f"depth_{i}", options=options, key=key)
                    st.session_state.depth_keys = [*st.session_state.depth_keys[:i], k]
            if k is not None:
                print(f"{k=}")
                st.write("Value")
                st.write(d)

        with col2:
            st.write("# Store")
            st.write(store)

        print(f"{st.session_state.depth_keys=}")
        print(f"Finish {st.session_state.render_count=}")
        st.session_state.render_count += 1


def mk_pipeline_maker_app_with_mall(
    mall: Mapping,
):
    if not b.mall():
        b.mall = mall
    mall = b.mall()

    crudifier = partial(Crudifier, mall=mall)

    @crudifier(output_store="sound_output")
    def upload_sound(train_audio: list, tag: str):
        return train_audio, tag

    def explore_mall(key):
        return mall[key]

    config = {
        APP_KEY: {"title": "Data Preparation"},
        RENDERING_KEY: {
            "upload_sound": {
                # NAME_KEY: "Data Loader",
                "execution": {
                    "inputs": {
                        "train_audio": {
                            ELEMENT_KEY: FileUploader,
                            "type": "wav",
                            "accept_multiple_files": True,
                        },
                    },
                    "output": {
                        ELEMENT_KEY: SuccessNotification,
                        "message": "Wav files loaded successfully.",
                    },
                },
            },
            "explore_mall": {
                "execution": {
                    "inputs": {"key": {ELEMENT_KEY: SelectBox, "options": list(mall)}},
                    "output": {ELEMENT_KEY: StoreExplorer},
                }
            },
        },
    }

    funcs = [
        explore_mall,
        upload_sound,
    ]
    app = mk_app(funcs, config=config)

    return app


mall = dict(
    # Factory Input Stores
    sound_output=dict(),
    # Output Store
    data=dict(
        a=1,
        b="2",
        c=[3],
        d={"4": 4, "5": [{"e": 6}, {"f": 7}, ["g", "h", "i"]]},
        j=[{"k": 8, "l": 9}, "m", 10],
    ),
)


if __name__ == "__main__":

    app = mk_pipeline_maker_app_with_mall(mall)

    app()
