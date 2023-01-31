from contextlib import contextmanager
from operator import itemgetter
from tempfile import TemporaryDirectory

from audiostream2py import get_input_device_index, PyAudioSourceReader
from dol import appendable
from i2 import ContextFanout
from know.base import SlabsIter
from know.util import ContextualFunc
from mongodol.tracking_methods import track_method_calls
from plunk.ap.live_graph.audio_store import (
    WavFileStore,
    merge_and_write_upon_count,
    BulkStore,
    CountMergeExecute,
    track_n_calls_of_method_then_execute,
)
from plunk.ap.live_graph.live_graph_data_buffer import audio_to_wf
from plunk.ap.snippets import if_not_none


def the_way_that_works():
    with TemporaryDirectory() as tmpdirname:
        audio_store = WavFileStore(rootdir=tmpdirname)

        @if_not_none
        def wrapped_append(item):
            return audio_store.append(item)

        wrapped_context_manager = [audio_store]

        with ContextualFunc(wrapped_append, wrapped_context_manager) as cf:
            cf({'timestamp': 0, 'wf': [1]})
            cf(None)

        print(list(audio_store))


def not_working():
    with TemporaryDirectory() as tmpdirname:
        audio_store = WavFileStore(rootdir=tmpdirname)

        with ContextualFunc(audio_store.append, audio_store) as cf:
            cf({'timestamp': 0, 'wf': [1]})
            cf(None)

        print(list(audio_store))


def not_working2():
    with TemporaryDirectory() as tmpdirname:
        audio_store = WavFileStore(rootdir=tmpdirname)

        def wrapped_append(item):
            return audio_store.append(item)

        with ContextualFunc(wrapped_append, audio_store) as cf:
            cf({'timestamp': 0, 'wf': [1]})
            cf(None)

        print(list(audio_store))


def _weak_error_message():
    def item_generator():
        for i in range(3):
            yield {'index': i}

    def print_item(item):
        print(item)

    with SlabsIter(item=item_generator(), print_item=print_item) as sit:
        for _ in sit:
            pass


def not_working3():
    def data_gen():
        for i in range(3):
            yield {'timestamp': i, 'wf': [i]}

    @merge_and_write_upon_count
    class Store(dict, BulkStore):
        pass

    store = Store()

    # @if_not_none
    # def wrapped_append(item):
    #     store.append(item)

    def print_item(item):
        print(item)

    wrapped_context_manager = [store]
    cf_store = ContextualFunc(store.append, wrapped_context_manager)
    with SlabsIter(
        item=iter(data_gen()).__next__, store_audio=cf_store, print_item=print_item,
    ) as sit:
        assert len(store) == 0

        # assert store.has_entered is True
        for _ in sit:
            assert len(store) == 0
            pass
    # assert store.has_entered is False
    assert len(store) > 0
    print(store)


def audio_it():
    input_device = 'NexiGo N930AF FHD Webcam Audio'
    rate = 44100
    width = 2
    channels = 1
    frames_per_buffer = 44100  # same as sample rate for 1 second intervals
    seconds_to_keep_in_stream_buffer = 60
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

    @if_not_none
    def store_item(timestamp, wf):
        return {'timestamp': timestamp, 'wf': wf}

    @if_not_none
    def get_timestamp(audio):
        return audio[0]

    @merge_and_write_upon_count
    class DictStore(dict, BulkStore):
        pass

    store = DictStore()
    store_audio = if_not_none(ContextualFunc(store.append, store))

    si = SlabsIter(
        audio=audio_buffer,
        timestamp=get_timestamp,
        wf=audio_to_wf,
        # audio_store_instance=lambda: store,
        item=store_item,
        _store_audio=store_audio,
    )
    with si as sit:
        assert len(store) == 0
        for i, _ in enumerate(sit):
            assert len(store) == 0
            if i > 3:
                break
    assert len(store) > 0
    print(store)


def cf_self_wrap():
    # @track_method_calls(
    #     tracked_methods='append',
    #     tracking_mixin=CountMergeExecute,
    #     calls_tracker=track_n_calls_of_method_then_execute,
    # )
    @appendable(item2kv=lambda item: (item['timestamp'], item['wf']))
    class Store(dict):
        def __enter__(self):
            print('enter')
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            print('exit')

    # with Store() as s:
    #     s.append({'timestamp': 0, 'wf': [1]})

    # print(s)

    store0 = Store()
    with ContextFanout(store0) as cfan:
        store0.append({'timestamp': 0, 'wf': [1]})
        print(store0)

    # store = Store()
    # with ContextualFunc(if_not_none(store.append), store=store) as cf:
    #     for i in range(22):
    #         cf({'timestamp': i, 'wf': [i]})
    #         cf(None)
    #
    # print(store)


def context_fanout():
    def mk_test_context(name, enter_obj=None):
        @contextmanager
        def test_context():
            print(f'entering {name} context')
            yield enter_obj
            print(f'exiting {name} context')

        return test_context()

    @appendable(item2kv=lambda item: (item['timestamp'], item['wf']))
    class TestContext:
        def __init__(self, name):
            self.name = name

        def __enter__(self):
            print(f'entering {self.name} context')
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            print(f'exiting {self.name} context')

    foo_context = mk_test_context('foo')
    with ContextFanout(foo_context) as cf:
        pass

    with ContextFanout(TestContext('bar')) as cf:
        pass


if __name__ == '__main__':
    # the_way_that_works()
    # not_working()
    # not_working2()
    # not_working3()
    # _weak_error_message()
    # audio_it()
    cf_self_wrap()
    # context_fanout()
