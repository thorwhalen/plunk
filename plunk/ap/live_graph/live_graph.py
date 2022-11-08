"""StreamViz LiveGraph
[x] SlabsIter signal source and process chunks for graphs; initially volume and zero crossing ratio.
[ ] Add graph data to a buffer that can be queried by time or index.
[ ] Add to webservice.
[ ] Visualize graph.
"""
from time import sleep, time
from typing import Any, Callable

import numpy as np
from audiostream2py import PyAudioSourceReader, get_input_device_index
from know.base import SlabsIter, IteratorExit
from know.examples.keyboard_and_audio import only_if
from recode import mk_codec
from stream2py import SourceReader
from stream2py.utility.typing_hints import ComparableType

codec = mk_codec('h')


def if_not_none(func):
    def _is_none_dict(d):
        return not all(v is None for k, v in d.items())

    return only_if(_is_none_dict)(func)


@if_not_none
def volume(wf):
    return np.std(wf)


@if_not_none
def zero_crossing_ratio(wf):
    return sum(np.diff(np.array(wf) > 0).astype(int)) / (len(wf) - 1)


GRAPH_TYPES = {
    'volume': volume,
    'zero_crossing_ratio': zero_crossing_ratio,
}


@if_not_none
def audio_to_wf(audio):
    _, wf_bytes, *_ = audio
    wf = codec.decode(wf_bytes)
    return wf


def audio_it(
    input_device=None,
    rate=44100,
    width=2,
    channels=1,
    frames_per_buffer=44100,  # same as sample rate for 1 second intervals
    seconds_to_keep_in_stream_buffer=60,
    graph_types=('volume', 'zero_crossing_ratio'),
):
    input_device_index = get_input_device_index(input_device=input_device)
    maxlen = PyAudioSourceReader.audio_buffer_size_seconds_to_maxlen(
        buffer_size_seconds=seconds_to_keep_in_stream_buffer,
        rate=rate,
        frames_per_buffer=frames_per_buffer,
    )

    audio_buffer = PyAudioSourceReader(
        rate=rate,
        width=width,
        channels=channels,
        unsigned=True,
        input_device_index=input_device_index,
        frames_per_buffer=frames_per_buffer,
    ).stream_buffer(maxlen)

    def stop_if_audio_not_running(audio_reader_instance):
        if audio_reader_instance is not None and not audio_reader_instance.is_running:
            raise IteratorExit("audio isn't running anymore!")

    return SlabsIter(
        audio=audio_buffer,
        wf=audio_to_wf,
        audio_reader_instance=lambda: audio_buffer,
        _audio_stop=stop_if_audio_not_running,
        **{k: v for k, v in GRAPH_TYPES.items() if k in graph_types},
    )


class SlabsSourceReader(SourceReader):
    def __init__(self, slabs_it: SlabsIter, key: Callable, skip: Callable = None):
        self.slabs_it = slabs_it
        self.key_func = key
        self.skip_func = skip

    def open(self) -> None:
        self.slabs_it.open()

    def close(self) -> None:
        self.slabs_it.close()

    def key(self, data: Any) -> ComparableType:
        return self.key_func(data)

    def read(self) -> dict:
        if self.skip_func(data := next(self.slabs_it)):
            return None
        return data


if __name__ == '__main__':
    print(PyAudioSourceReader.list_recording_devices())

    def get_timestamp(data):
        return data.get('audio')[0]

    def skip_data(data) -> bool:
        return data.get('audio') is None

    start = time() * 1e6
    with SlabsSourceReader(
        slabs_it=audio_it(input_device='NexiGo N930AF FHD Webcam Audio'),
        key=get_timestamp,
        skip=skip_data,
    ).stream_buffer(100) as slab_buffer:
        i = 0

        slab_reader = slab_buffer.mk_reader()
        while slab_buffer.is_running:
            if (slab := slab_reader.next(ignore_no_item_found=True)) is not None:
                print(slab.get('audio')[0], slab.get('volume'))
                i += 1
            else:
                sleep(0.1)

            if i == 10:
                break

        stop = time() * 1e6
        print(f'{len(slab_reader.range(start, stop))}')
