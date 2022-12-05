from tempfile import TemporaryDirectory

from know.base import SlabsIter
from know.util import ContextualFunc
from plunk.ap.live_graph.audio_store import WavFileStore
from plunk.ap.live_graph.live_graph_data_buffer import if_not_none


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


def not_working3():
    _enter = False

    def data_gen():
        for i in range(3):
            yield {'timestamp': i, 'wf': [i]}

    class Store(dict):
        def __enter__(self):
            self._enter = True

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._enter = False

        def append(self, item):
            if self._enter is True:
                self[item['timestamp']] = item['wf']

    store = Store()

    @if_not_none
    def wrapped_append(item):
        store.append(item)

    def print_item(item):
        print(item)

    wrapped_context_manager = [store]
    cf_store = ContextualFunc(wrapped_append, wrapped_context_manager)
    with SlabsIter(
        item=iter(data_gen()).__next__, store_audio=cf_store, print_item=print_item,
    ) as sit:
        for _ in sit:
            pass


def _weak_error_message():
    def item_generator():
        for i in range(3):
            yield {'index': i}

    def print_item(item):
        print(item)

    with SlabsIter(item=item_generator(), print_item=print_item) as sit:
        for _ in sit:
            pass


if __name__ == '__main__':
    # the_way_that_works()
    # not_working()
    # not_working2()
    # not_working3()
    _weak_error_message()
