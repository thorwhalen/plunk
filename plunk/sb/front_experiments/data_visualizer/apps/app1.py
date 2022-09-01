import streamlit as st
from plunk.sb.front_experiments.data_visualizer.dags.wfstore_and_annots_to_dataset import (
    load_dataset,
)
from streamlitfront import mk_app, binder as b
from functools import partial
from front.crude import Crudifier, prepare_for_crude_dispatch

root_dir = "/Users/sylvain/Dropbox/_odata/sound/vacuum"
annots_path = "../data/annots_vacuum.csv"


st.title("visualizer")


# ============ BACKEND ============

if not b.mall():
    b.mall = dict(
        tagged_wf=dict(),
        dummy_store=dict(),
    )
mall = b.mall()
crudifier = partial(Crudifier, mall=mall)


@crudifier(
    param_to_mall_map=dict(x="tagged_wf"),
    output_store="dummy_store",
    auto_namer=auto_namer,
)
def get_tagged_wf(x):
    return x


# ============ END BACKEND ============
