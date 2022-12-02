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
    def data_gen():
        for i in range(3):
            yield {'timestamp': i, 'wf': [i]}

    for d in data_gen():
        print(d)

    with TemporaryDirectory() as tmpdirname:
        audio_store = WavFileStore(rootdir=tmpdirname)

        @if_not_none
        def wrapped_append(item):
            return audio_store.append(item)

        wrapped_context_manager = [audio_store]
        cf_store_audio = ContextualFunc(wrapped_append, wrapped_context_manager)
        with SlabsIter(item=data_gen(), store_audio=cf_store_audio) as sit:
            for s in sit:
                print(s)


if __name__ == '__main__':
    the_way_that_works()
    not_working()
    not_working2()
    not_working3()
