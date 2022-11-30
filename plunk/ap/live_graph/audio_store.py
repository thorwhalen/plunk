from collections import defaultdict
from functools import wraps, partial, reduce
from io import BytesIO
from itertools import chain
from math import ceil
from operator import itemgetter
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import (
    Callable,
    MutableMapping,
    Protocol,
    Iterator,
    DefaultDict,
    List,
)
from wave import Wave_write

from dol import appendable, Files, wrap_kvs
from i2 import Sig
from mongodol.tracking_methods import (
    track_method_calls,
    TrackableMixin,
)
from recode import (
    encode_pcm_bytes,
    decode_wav_bytes,
)


class BulkStore(Protocol):
    """Mutable Mapping with Append Method"""

    def append(self, item):
        pass

    def __setitem__(self, __k, __v) -> None:
        pass

    def __delitem__(self, __v) -> None:
        pass

    def __getitem__(self, __k):
        pass

    def __len__(self) -> int:
        pass

    def __iter__(self) -> Iterator:
        pass


audio_slab_kv = itemgetter('timestamp', 'wf')


N_TO_BULK = 10


class CountAndExecute(TrackableMixin):
    """Make tracks factory count method calls when order of different methods is not important"""

    tracks_factory: DefaultDict[Callable, List[tuple]] = partial(defaultdict, list)

    def _execute_method_tracks(self, method: Callable):
        for args, kwargs in self._tracks[method]:
            method(self, *args, **kwargs)

    def _execute_tracks(self):
        for method in self._tracks:
            self._execute_method_tracks(method)


def merge_append_ts_wf(items: List[dict]):
    """Take a list of kwargs and return a single kwargs

    :param items: [{item: {timestamp: 0, wf: [1, 2, 3]}, ...]
    :return:
    """
    ts = items[0]['item']['timestamp']
    joined_wf = list(
        chain.from_iterable(
            map(
                partial(
                    reduce, lambda x, y: y(x), [itemgetter('item'), itemgetter('wf')],
                ),
                items,
            )
        )
    )
    return {'item': {'timestamp': ts, 'wf': joined_wf}}


class CountMergeExecute(CountAndExecute):
    """Apply a merging method to join all arguments before executing tracked method once"""

    _MERGE_KWARGS_MAP = {'append': merge_append_ts_wf}

    def _execute_method_tracks(self, method: Callable):
        if merge_kwargs_method := self._MERGE_KWARGS_MAP.get(method.__name__):
            sig = Sig(method)
            kwargs_list = [
                sig.kwargs_from_args_and_kwargs((self, *a), kw)
                for a, kw in self._tracks[method]
            ]
            merged_kwargs = merge_kwargs_method(kwargs_list)
            method(self, **merged_kwargs)
        else:
            super()._execute_method_tracks(method)


def track_n_calls_of_method_then_execute(method: Callable, n_calls=N_TO_BULK):
    @wraps(method)
    def tracked_method(self: CountAndExecute, *args, **kwargs):
        self._tracks[method].append((args, kwargs))
        if len(self._tracks[method]) >= n_calls:
            self._execute_method_tracks(method)
            del self._tracks[method]

    return tracked_method


def ts_to_filename(ts, ext='.wav'):
    return f'{ts}{ext}'


def filename_to_ts(name, ext='.wav'):
    return int(name[: -len(ext)])


def wf_to_wav(
    wf, sr: int = 44100, width_bytes: int = 2, *, n_channels: int = 1
) -> bytes:
    bio = BytesIO()
    with Wave_write(bio) as obj:
        obj.setparams((n_channels, width_bytes, sr, 0, 'NONE', 'not compressed'))
        wf_bytes = encode_pcm_bytes(wf, width=width_bytes * 8, n_channels=n_channels)
        obj.writeframes(wf_bytes)
        bio.seek(0)
    return bio.read()


def wav_to_wf(wav):
    wf, sr = decode_wav_bytes(wav)
    return wf


@track_method_calls(
    tracked_methods='append',
    tracking_mixin=CountMergeExecute,
    calls_tracker=track_n_calls_of_method_then_execute,
)
@appendable(item2kv=audio_slab_kv)
@wrap_kvs(
    key_of_id=filename_to_ts,
    id_of_key=ts_to_filename,
    obj_of_data=wav_to_wf,
    data_of_obj=wf_to_wav,
)
class WavFileStore(Files, BulkStore):
    pass


@track_method_calls(
    tracked_methods='append',
    tracking_mixin=CountMergeExecute,
    calls_tracker=track_n_calls_of_method_then_execute,
)
@appendable(item2kv=audio_slab_kv)
class DictStore(dict, BulkStore):
    pass


def _test_merge_append_ts_wf():
    a = []
    for i in range(10):
        a.append({'item': {'timestamp': i, 'wf': [i] * 2}})
    ma = merge_append_ts_wf(a)
    print(ma)
    assert 'item' in ma


def _test_dict_store():
    _test_store(DictStore())


def _test_files_store():
    with TemporaryDirectory() as tmpdirname:
        audio_store = WavFileStore(rootdir=tmpdirname)
        _test_store(audio_store)
        print(f'{len(list(Path(tmpdirname).iterdir()))=} == {len(audio_store)=}')
        assert len(list(Path(tmpdirname).iterdir())) == len(audio_store)


def _test_store(store_instance: MutableMapping, *, n=22, chk_size=2, log=print):
    """Test append, tracking, input, and output

    :param store_instance:
    :param n: number of chunks
    :param chk_size: samples per chunk
    :param log: print
    :return:
    """
    with store_instance as a:
        for i in range(n):
            a.append({'timestamp': i, 'wf': [i] * chk_size})

            _, append_track = next(iter(a._tracks.items()), (None, tuple()))

            log('print#2', f'{i=}', f'{len(append_track)=}', a)
            assert (
                len(append_track) == (i + 1) % N_TO_BULK
            ), 'Tracking should auto flush when size limit is reached'
            log('print#3', f'{len(a) == 0=}')
            assert len(a) == (i + 1) // N_TO_BULK, list(a)
            log(a._tracks)

        _, append_track = next(iter(a._tracks.items()), (None, tuple()))

        log('print#4', f'{len(append_track) == n=}')
        assert len(append_track) == n % N_TO_BULK
        log('print#5', a, len(append_track))

    _, append_track = next(iter(a._tracks.items()), (None, tuple()))

    log('print#6', len(append_track), a)
    assert len(append_track) == 0
    assert len(a) == ceil(n / N_TO_BULK), f'{len(a)=} == {ceil(n / N_TO_BULK)=}'
    for i, (k, v) in enumerate(sorted(a.items())):
        log('print#7', f'{(k, v)=}')
        assert k == i * N_TO_BULK
        if k + N_TO_BULK > n:
            assert (
                len(v) / chk_size == n - k
            ), f'{i=}, {k=}, {len(v) / chk_size=}, {n - k=}'
        else:
            assert (
                len(v) / chk_size == N_TO_BULK
            ), f'{i=}, {k=}, {len(v) / chk_size=}, {N_TO_BULK=}'
        v_iter = iter(v)
        for j in range(i * N_TO_BULK, min((i + 1) * N_TO_BULK, n)):
            for _ in range(chk_size):
                assert (
                    next(v_iter) == j
                ), f'{i=}, {j=}, {k=}, {i * N_TO_BULK=}, {min((i + 1) * N_TO_BULK, n)=}'

    print(f'Test passed with params: {store_instance=}, {n=}, {chk_size=}, {log=}')


if __name__ == '__main__':
    _test_merge_append_ts_wf()
    _test_dict_store()
    _test_files_store()
