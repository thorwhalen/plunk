from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY, OBJ_KEY
from streamlitfront.elements import SelectBox
from streamlitfront import mk_app
import streamlit as st
from front.crude import Crudifier
from front.crude import Crudifier


DFLT_INPUT = "my text"


def do_something(wf_src=DFLT_INPUT):
    return wf_src


if "mall" not in st.session_state:
    st.session_state["mall"] = dict(
        wfsource={"wfsrc": DFLT_INPUT},
    )

mall = st.session_state["mall"]


@Crudifier(mall=mall, param_to_mall_map={"wf_src": "wfsource"})
def example(wf_src):
    result = do_something(wf_src)  # better tuple wfs_train, wfs_test


config_ = {
    APP_KEY: {"title": "Crudified learner"},
    RENDERING_KEY: {
        "classify": {
            "execution": {
                "inputs": {
                    "wf_src": {
                        ELEMENT_KEY: SelectBox,
                        "options": mall["wfsource"],
                    },
                },
            }
        },
    },
}

app = mk_app(
    [example],
    config=config_,
)
app()
