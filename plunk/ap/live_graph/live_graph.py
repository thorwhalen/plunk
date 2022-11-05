"""StreamViz LiveGraph
[x] SlabsIter signal source and process chunks for graphs; initially volume and zero crossing ratio.
[ ] Add graph data to a buffer that can be queried by time or index.
[ ] Add to webservice.
[ ] Visualize graph.
"""
from time import sleep

import numpy as np
from audiostream2py import PyAudioSourceReader, get_input_device_index
from know.base import SlabsIter, IteratorExit
from know.examples.keyboard_and_audio import only_if
from recode import mk_codec

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
        **{k: v for k, v in GRAPH_TYPES.items() if k in graph_types}
    )


if __name__ == '__main__':
    print(PyAudioSourceReader.list_recording_devices())
    with audio_it(input_device='NexiGo N930AF FHD Webcam Audio') as a_it:
        i = 0
        for slab in a_it:
            if slab.get('audio') is not None:
                print(slab.get('volume'))
                i += 1
            else:
                sleep(0.1)

            if i == 10:
                break
