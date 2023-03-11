from dataclasses import dataclass
from functools import wraps
from typing import Iterable, Union, Tuple

import streamlit as st
import numpy as np
from matplotlib import pyplot as plt
from front.elements import OutputBase

from plunk.ap.live_graph.live_graph_streamlitfront import plot, line_plot


def only_if_output(f):
    @wraps(f)
    def wrapper(self: OutputBase, *a, **kw):
        if self.output is not None:
            return f(self, *a, **kw)

    return wrapper


def spectrum_plot(graph_data: Iterable[Union[int, float]], title: str, figsize=(15, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    st.markdown(f'## {title}')
    ax.specgram(graph_data)
    st.pyplot(fig)
    plt.close(fig)


def audio_player(wf, sr):
    st.audio(wf, sample_rate=sr)


@dataclass
class WfVisualizePlayer(OutputBase):
    output: Tuple[np.ndarray, int] = None

    @property
    def wf(self):
        return self.output[0]

    @property
    def sr(self):
        return self.output[1]

    @only_if_output
    def render(self):
        line_plot(self.wf, 'Waveform')
        spectrum_plot(self.wf, 'Spectrum')
        audio_player(self.wf, self.sr)
