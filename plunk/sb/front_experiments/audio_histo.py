import threading

import cv2
import streamlit as st
from matplotlib import pyplot as plt

from streamlit_webrtc import webrtc_streamer

lock = threading.Lock()
audio_container = {"audio": None}


def audio_frame_callback(frame):
    audio = frame.to_ndarray(format="bgr24")
    with lock:
        audio_container["audio"] = audio

    return frame


ctx = webrtc_streamer(key="example", audio_frame_callback=audio_frame_callback)

fig_place = st.empty()
fig, ax = plt.subplots(1, 1)

while ctx.state.playing:
    with lock:
        audio = audio_container["audio"]
    if audio is None:
        continue
    gray = cv2.cvtColor(audio, cv2.COLOR_BGR2GRAY)
    ax.cla()
    ax.hist(gray.ravel(), 256, [0, 256])
    fig_place.pyplot(fig)
