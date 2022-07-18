import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development

st.set_page_config(
    page_title="Stream a dataframe",
    layout="wide",
)

# read csv from a github repo
dataset_url = "data/accel_data.csv"


@st.experimental_memo
def get_data() -> pd.DataFrame:
    return pd.read_csv(dataset_url)


df = get_data()

# dashboard title
st.title("Stream a dataframe")

# top-level filters
job_filter = st.selectbox("Select the Job", pd.unique(df["job"]))

# creating a single-element container
placeholder = st.empty()

# dataframe filter
# df = df[df["job"] == job_filter]
ddf = df.copy().iloc[:10]
# near real-time / live feed simulation
for seconds in range(200):

    ddf["ACC_X"] = df["ACC_X"].iloc[seconds * 10 : (seconds + 1) * 10]

    with placeholder.container():

        # create two columns for charts
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown("### First Chart")
            fig = px.histogram(data_frame=ddf, x="ACC_X")
            st.write(fig)

        with fig_col2:
            st.markdown("### Second Chart")
            fig2 = px.histogram(data_frame=ddf, x="ACC_X")
            st.write(fig2)

        st.markdown("### Detailed Data View")
        st.dataframe(ddf)
        time.sleep(1)
