from dataclasses import dataclass
from functools import wraps
from typing import Iterable, Union, Tuple

import streamlit as st
import numpy as np
from matplotlib import pyplot as plt
from front.elements import OutputBase

from plunk.ap.live_graph.live_graph_streamlitfront import plot, line_plot

WfSr = Tuple[np.ndarray, int]


def only_if_output(f):
    @wraps(f)
    def wrapper(self: OutputBase, *a, **kw):
        if self.output is not None:
            return f(self, *a, **kw)

    return wrapper


FIG_SIZE = (15, 2)


def line_plot(graph_data: Iterable[Union[int, float]], title: str, figsize=FIG_SIZE):
    fig, ax = plt.subplots(figsize=figsize)
    st.markdown(f'### {title}')
    ax.plot(graph_data)
    st.pyplot(fig)
    plt.close(fig)


def spectrum_plot(
    graph_data: Iterable[Union[int, float]], title: str, figsize=FIG_SIZE
):
    fig, ax = plt.subplots(figsize=figsize)
    st.markdown(f'### {title}')
    ax.specgram(graph_data)
    st.pyplot(fig)
    plt.close(fig)


def audio_player(wf, sr):
    st.audio(wf, sample_rate=sr)


def render_channel(channel_index, wf, sr):
    box = st.empty()
    with box.container():
        st.markdown(f'## channel-{channel_index}')
        line_plot(wf, 'Waveform')
        spectrum_plot(wf, 'Spectrum')
        audio_player(wf, sr)


@dataclass
class WfVisualizePlayer(OutputBase):
    output: WfSr = None

    @property
    def wf(self) -> np.ndarray:
        return self.output[0]

    @property
    def sr(self) -> int:
        return self.output[1]

    @only_if_output
    def render(self):
        if self.wf.ndim > 1:
            for i, ch_wf in enumerate(self.wf):
                render_channel(i, ch_wf, self.sr)
        else:
            render_channel(0, self.wf, self.sr)
