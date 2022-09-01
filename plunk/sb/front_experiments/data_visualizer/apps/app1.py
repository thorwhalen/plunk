import streamlit as st
from plunk.sb.front_experiments.data_visualizer.dags.wfstore_and_annots_to_dataset import (
    load_dataset,
)


root_dir = "/Users/sylvain/Dropbox/_odata/sound/vacuum"
annots_path = "../data/annots_vacuum.csv"


st.title("visualizer")
