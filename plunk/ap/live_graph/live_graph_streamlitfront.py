"""Render a stream"""
import time
from dataclasses import dataclass
from functools import partial

from audiostream2py import PyAudioSourceReader

import streamlit as st
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, Crudifier, NAME_KEY
from front.elements import OutputBase
import matplotlib.pyplot as plt
from stream2py import StreamBuffer

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


@dataclass
class DataGraph(OutputBase):
    output: StreamBuffer = None

    def render(self):
        if self.output:
            maxlen = self.output._maxlen
            box = st.empty()
            i = 0
            data_reader = self.output.mk_reader()
            while self.output.is_running:
                if data_reader.read(ignore_no_item_found=True) is not None:
                    data_list = data_reader.range(0, time.time() * 1e6, peek=True)
                    # print(f'{len(data_list)=}')

                    graph_data = [0] * (maxlen - len(data_list))
                    graph_data.extend(
                        [
                            next(v for k, v in d.items() if k != 'timestamp')
                            for d in data_list
                        ]
                    )
                    with box.container():
                        fig, ax = plt.subplots(figsize=(15, 5))
                        st.markdown(f'## Graph')
                        ax.plot(graph_data, label='Graph')
                        st.pyplot(fig)
                        plt.close(fig)
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
                            'graph_types': {
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
