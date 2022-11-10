"""Render a stream"""
import datetime
import time
from collections import defaultdict
from dataclasses import dataclass
from functools import partial
from typing import List

from audiostream2py import PyAudioSourceReader

import streamlit as st
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, Crudifier, NAME_KEY
from front.elements import OutputBase
import matplotlib.pyplot as plt
from stream2py import StreamBuffer, BufferReader

from streamlitfront import mk_app, binder as b
from streamlitfront.elements import SelectBox

from plunk.ap.live_graph.live_graph_data_buffer import (
    mk_live_graph_data_buffer,
    GRAPH_TYPES,
)

if not b.mall():
    b.mall = dict(
        input_device=PyAudioSourceReader.list_recording_devices(),
        source=None,
        graph_types=list(GRAPH_TYPES),
    )

mall = b.mall()
crudifier = partial(Crudifier, mall=mall)


def time_string(timestamp):
    st.markdown(f'## time: {str(datetime.datetime.fromtimestamp(timestamp / 1e6))}')


def line_plot(graph_data: List[int | float], title: str, figsize=(15, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    st.markdown(f'## {title}')
    ax.plot(graph_data)
    st.pyplot(fig)
    plt.close(fig)


PLOT_TYPES = {'line': line_plot}


@dataclass
class DataGraph(OutputBase):
    output: StreamBuffer = None

    def format(self, data_reader: BufferReader):
        maxlen = data_reader._buffer._sorted_deque.maxlen
        data_list = data_reader.range(0, time.time() * 1e6, peek=True)
        plots_data_padding = [0] * (maxlen - len(data_list))
        plots_data = defaultdict(plots_data_padding.copy)
        for d in data_list:
            for k, v in d.items():
                if k in GRAPH_TYPES and v is not None:
                    plots_data[k].append(v)
        timestamp = data_list[-1]['timestamp']
        return timestamp, plots_data

    def plot(self, graph_type: str, graph_data: List[int | float]):
        plot_type = GRAPH_TYPES[graph_type]['plot']
        PLOT_TYPES[plot_type](graph_data, title=graph_type)

    def render(self):
        if self.output:
            box = st.empty()
            i = 0
            data_reader = self.output.mk_reader()
            while self.output.is_running:
                if data_reader.read(ignore_no_item_found=True) is not None:
                    timestamp, plots_data = self.format(data_reader)
                    with box.container():
                        for graph_type, graph_data in plots_data.items():
                            self.plot(graph_type, graph_data)
                        time_string(timestamp)
                    print(f'rendering...({i})')
                    i += 1
                else:
                    time.sleep(0.1)
                    # print(f'sleeping...')
            print('exit render')


def stop_stream():
    if mall['source']:
        try:
            mall['source'].stop()
            mall['source'] = None
        except Exception as e:
            print(e)


@crudifier(output_store='source')
def data_stream(
    input_device=None,
    rate=44100,
    width=2,
    channels=1,
    frames_per_buffer=44100,
    seconds_to_keep_in_stream_buffer=60,
    graph_types='volume',
):
    stop_stream()
    source = mk_live_graph_data_buffer(
        input_device,
        rate,
        width,
        channels,
        frames_per_buffer,
        seconds_to_keep_in_stream_buffer,
        graph_types,
    )
    source.start()
    return source


if __name__ == '__main__':
    app = mk_app(
        [data_stream, stop_stream],
        config={
            APP_KEY: {'title': 'My Stream App'},
            RENDERING_KEY: {
                'data_stream': {
                    NAME_KEY: 'Get Data Stream',
                    'description': {'content': 'Configure soundcard for data stream'},
                    'execution': {
                        'inputs': {
                            'input_device': {
                                ELEMENT_KEY: SelectBox,
                                'options': mall['input_device'],
                            },
                            'graph_types': {  # TODO option to select more than one graph type
                                ELEMENT_KEY: SelectBox,
                                'options': mall['graph_types'],
                            },
                        },
                        'output': {ELEMENT_KEY: DataGraph},
                    },
                },
            },
        },
    )
    app()
