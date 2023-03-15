from dataclasses import dataclass
from functools import wraps
from typing import Iterable, Union, Tuple, Sequence, Callable

import streamlit as st
import numpy as np
from matplotlib import pyplot as plt
from front.elements import OutputBase
from matplotlib.axes import Axes

from plunk.ap.live_graph.live_graph_streamlitfront import line_plot

WfSr = Tuple[np.ndarray, int]


def only_if_output(f):
    @wraps(f)
    def wrapper(self: OutputBase, *a, **kw):
        if self.output is not None:
            return f(self, *a, **kw)

    return wrapper


FIG_SIZE = (15, 2)


def spectrum_plot(ax: Axes, graph_data: Sequence[Union[int, float]], sr=None):
    ax.specgram(graph_data, Fs=sr)


def line_plot(ax: Axes, graph_data: Sequence[Union[int, float]], sr=None):
    time = np.arange(len(graph_data)) / sr
    ax.plot(time, graph_data)


def plot_data(
    title: str,
    graph_data: Sequence[Union[int, float]],
    sr: int,
    plot_ax: Callable[[Axes, Sequence[Union[int, float]], int], None],
    figsize=FIG_SIZE,
):
    fig, ax = plt.subplots(figsize=figsize)
    st.markdown(f'##### {title}')
    plot_ax(ax, graph_data, sr)
    ax.margins(x=0)
    st.pyplot(fig)
    plt.close(fig)




def audio_player(wf, sr):
    st.audio(wf, sample_rate=sr)


def render_channel(channel_index, wf, sr):
    box = st.empty()
    with box.container():
        st.markdown(f'## channel-{channel_index}')
        plot_data('Waveform', wf, sr, line_plot)
        plot_data('Spectrum', wf, sr, spectrum_plot)
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
