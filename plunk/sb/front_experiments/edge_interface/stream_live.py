import time
import pandas as pd
import plotly.express as px
import streamlit as st
import pyaudio
import numpy as np

st.set_page_config(
    page_title="Stream a dataframe",
    layout="wide",
)


maxValue = 2 ** 16
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=44100,
    input=True,
    output=True,
    frames_per_buffer=1024,
    output_device_index=3,
)


# df = get_data(dataset_path)
# min_data = df["ACC_Y"].min()
# max_data = df["ACC_Y"].max()

# dashboard title
st.title("Stream a dataframe")


# creating a single-element container
placeholder = st.empty()

# live data
while True:
    data = np.fromstring(stream.read(1024, exception_on_overflow=False), dtype=np.int16)
    dataL = data[0::2]
    peakL = np.abs(np.max(dataL) - np.min(dataL)) / maxValue

    # print("left", round(peakL, 2))
    # # vals = df["ACC_Y"].iloc[seconds : seconds + 30].values
    d = {"sound": dataL}
    with placeholder.container():
        fig = px.line(
            data_frame=pd.DataFrame(d),
            x=range(512),
            y="sound",
            # range_y=[min_data, max_data],
        )
        st.write(fig)

        # time.sleep(0.1)
