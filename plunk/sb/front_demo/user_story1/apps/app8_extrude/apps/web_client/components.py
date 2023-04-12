from dataclasses import dataclass, field
from typing import Tuple, List, Callable, Union

from front.elements import InputBase
from matplotlib.axes import Axes
from stogui import oto_table
from streamlitfront.elements import OutputBase
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


def pyplot_with_intervals(X, intervals=None):
    min_x = np.mean(X)
    xs = list(range(len(X)))
    ys = X
    fig, ax = plt.subplots(figsize=(7, 2))
    ax.plot(xs, ys, linewidth=1)
    if intervals:
        for i, interval in enumerate(intervals):
            start, end = interval
            plt.axvspan(start, end, facecolor='g', alpha=0.5)

            ax.annotate(f'{i}', xy=(start, min_x), ha='left', va='top')
    return fig


@dataclass
class ArrayWithIntervalsPlotter(OutputBase):
    def render(self):
        X, intervals = self.output
        fig = pyplot_with_intervals(X, intervals)
        st.pyplot(fig)


@dataclass
class ArrayPlotter(OutputBase):
    def render(self):
        X = self.output
        # st.write(f"Average score of session= {np.mean(X)}")
        fig, ax = plt.subplots(figsize=(15, 5))
        ax.plot(X)
        ax.legend()
        st.pyplot(fig)


WfSr = Tuple[np.ndarray, int]


@dataclass
class WfVisualizePlayer(OutputBase):
    output: WfSr = None
    figsize = (15, 5)

    @property
    def wf(self) -> np.ndarray:
        return self.output[0]

    @property
    def sr(self) -> int:
        return self.output[1]

    def render(self):
        if not self.output:
            return st.write('No Data')

        if np.any((self.wf > 1) | (self.wf < -1)):
            st.error(
                'Waveform signal should be bounded between [-1; 1]. '
                'If incoming signal x is encoded in int16, then apply x = x / 2**15'
            )
            return

        if self.wf.ndim > 1:
            for i, ch_wf in enumerate(self.wf):
                self.render_channel(i, ch_wf, self.sr)
        else:
            self.render_channel(0, self.wf, self.sr)

    @classmethod
    def render_channel(cls, channel_index, wf, sr):
        box = st.empty()
        with box.container():
            st.markdown(f'## channel-{channel_index}')
            cls.plot_data(wf, sr)
            cls.audio_player(wf, sr)

    @classmethod
    def spectrogram_plot(
        cls, ax: Axes, graph_data: np.ndarray, sr: int, title='Spectrogram',
    ):
        NFFT = max(
            256, 2 ** (round(np.log(len(graph_data) / 500) / np.log(2)))
        )  # to limit number of spectra
        f_res = sr / NFFT
        log10_f = np.arange(np.ceil(np.log10(f_res)), np.ceil(np.log10(sr / 2)))
        f_ticks = 10 ** log10_f

        ax.title.set_text(title)
        ax.xaxis.set_label_text('Time (sec)')
        ax.yaxis.set_label_text('Frequency (Hz)')
        ax.specgram(graph_data, Fs=sr, NFFT=NFFT)
        ax.set_yscale('log')
        ax.set_ylim(f_res, sr / 2)
        ax.set_yticks(f_ticks)

    @classmethod
    def waveform_plot(
        cls, ax: Axes, graph_data: np.ndarray, sr: int, title='Waveform',
    ):
        time = np.arange(len(graph_data)) / sr
        ax.title.set_text(title)
        ax.margins(x=0)  # remove white space from line plot
        ax.xaxis.set_label_text('Time (sec)')
        ax.yaxis.set_label_text('Magnitude')
        ax.set_yticklabels([])
        ax.plot(time, graph_data)

    @classmethod
    def plot_data(cls, wf: np.ndarray, sr: int):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=cls.figsize)
        cls.waveform_plot(ax1, wf, sr)
        cls.spectrogram_plot(ax2, wf, sr)
        fig.subplots_adjust(hspace=0.5)  # increase spacing between subplots
        st.pyplot(fig)
        plt.close(fig)

    @classmethod
    def audio_player(cls, wf: np.ndarray, sr: int):
        st.audio(wf, sample_rate=sr)


@dataclass
class OtoTable(InputBase):
    sessions: Union[List[dict], Callable[[], List[dict]]] = None
    is_multiselect: bool = False

    def render(self):
        component_value = oto_table(
            sessions=self.sessions, is_multiselect=self.is_multiselect
        )
        if self.is_multiselect is not True and isinstance(component_value, list):
            component_value = component_value[0]

        return component_value
