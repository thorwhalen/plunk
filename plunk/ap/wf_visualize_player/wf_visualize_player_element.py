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


FIG_SIZE = (15, 5)


def spectrogram_plot(
    ax: Axes, graph_data: Sequence[Union[int, float]], sr=None, title='Spectrogram'
):
    ax.title.set_text(title)
    ax.xaxis.set_label_text('Time (sec)')
    ax.yaxis.set_label_text('Frequency (Hz)')
    ax.set_yscale('log')
    ax.specgram(graph_data, Fs=sr)
    ax.set_ylim(100, sr / 2)
    ax.set_yticklabels(['0', '100', '1k', '10k'])


def waveform_plot(
    ax: Axes, graph_data: Sequence[float], sr, title='Waveform',
):
    time = np.arange(len(graph_data)) / sr
    ax.title.set_text(title)
    ax.margins(x=0)  # remove white space from line plot
    ax.xaxis.set_label_text('Time (sec)')
    ax.yaxis.set_label_text('Magnitude')
    ax.set_yticklabels([])
    ax.plot(time, graph_data)


def plot_data(
    wf: Sequence[Union[int, float]], sr: int, figsize=FIG_SIZE,
):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    waveform_plot(ax1, wf, sr)
    spectrogram_plot(ax2, wf, sr)
    fig.subplots_adjust(hspace=0.5)  # increase spacing between subplots
    st.pyplot(fig)
    plt.close(fig)


def audio_player(wf, sr):
    st.audio(wf, sample_rate=sr)


def render_channel(channel_index, wf, sr, figsize=FIG_SIZE):
    box = st.empty()
    with box.container():
        st.markdown(f'## channel-{channel_index}')
        plot_data(wf, sr, figsize)
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
        if np.any((self.wf > 1) | (self.wf < -1)):
            st.error(
                'Waveform signal should be bounded between [-1; 1]. '
                'If incoming signal x is encoded in int16, then apply x = x / 2**15'
            )
            return

        if self.wf.ndim > 1:
            for i, ch_wf in enumerate(self.wf):
                render_channel(i, ch_wf, self.sr)
        else:
            render_channel(0, self.wf, self.sr)
