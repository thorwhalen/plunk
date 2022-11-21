import shutil
from abc import ABC, abstractmethod
from functools import cached_property
from itertools import chain
from math import ceil
from operator import itemgetter
from pathlib import Path
from typing import MutableSequence, Callable

from dol import appendable, Files, wrap_kvs
from mongodol.tracking_methods import (
    track_method_calls,
    track_calls_without_executing,
    TrackableMixin,
)
from recode import (
    encode_pcm_bytes,
    decode_pcm_bytes,
    encode_wav_header_bytes,
    decode_wav_bytes,
)


class AbstractBulkAppend(TrackableMixin, ABC):
    bulk_factory: Callable[[], MutableSequence] = list

    @cached_property
    def _bulk(self) -> MutableSequence:
        """Sequence of items.

        :return:
        """
        return self.bulk_factory()

    def _execute_tracks(self):
        for func, args, kwargs in self._tracks:
            if kv := self._bulk_append(*args, **kwargs):
                func(self, kv)
        if len(self._bulk) > 0:
            kv = self._bulk_kv(self._bulk)
            func(self, kv)

    def _bulk_append(self, item):
        """Append item to bulk and return None, or combine bulk and return the resulting item.

        :param item:
        :return:
        """
        if len(self._bulk) > 0:
            if self._should_bulk(item):
                self._bulk.append(item)
            else:
                rv = self._bulk_kv(self._bulk)
                self._bulk.clear()
                self._bulk.append(item)
                return rv
        else:
            self._bulk.append(item)
        return None

    @abstractmethod
    def _should_bulk(self, item) -> bool:
        """Check if next item triggers the condition to bulk all the items into a single item

        :param item:
        :return:
        """
        pass

    @abstractmethod
    def _bulk_kv(self, bulk):
        """Takes the sequence of items and combines into a single item

        :param bulk:
        :return:
        """
        pass


audio_slab_kv = itemgetter('timestamp', 'wf')


N_TO_BULK = 10


def should_bulk_if_bt_within_n(self, item, n=N_TO_BULK):
    print(self, item, n)
    print(self._bulk[0])
    bulk_ts, _ = audio_slab_kv(self._bulk[0])
    item_ts, _ = audio_slab_kv(item)
    return item_ts - bulk_ts < n


def join_ts_wf(self, bulk):
    """Merge bulk and return key and joined value

    :param bulk:
    :return:
    """
    print(self, bulk)
    ts = bulk[0]['timestamp']
    joined_wf = list(chain.from_iterable(map(itemgetter('wf'), bulk)))
    return {'timestamp': ts, 'wf': joined_wf}


def bulk_append(
    should_bulk=should_bulk_if_bt_within_n,
    bulk_kv=join_ts_wf,
    bulk_factory_callable=AbstractBulkAppend.bulk_factory,
):
    class BulkAppend(AbstractBulkAppend):
        bulk_factory = bulk_factory_callable

        def _should_bulk(self, item) -> bool:
            return should_bulk(self, item)

        def _bulk_kv(self, bulk):
            return bulk_kv(self, bulk)

    return BulkAppend


def _test_dict_store():
    @track_method_calls(
        tracked_methods='append',
        tracking_mixin=bulk_append(),
        calls_tracker=track_calls_without_executing,
    )
    @appendable(item2kv=audio_slab_kv)
    class AudioStore(dict):
        pass

    n = 22
    repeat = 2
    # with AudioStore() as a:
    #     for i in range(n):
    #         a.append({'timestamp': 1, 'wf': 1})
    #         print(i)
    #         assert False, 'testing assert'
    # print('print#0', '"assert False" did not stop run')
    #
    # with AudioStore() as a:
    #     for i in range(n):
    #         a.append({'timestamp': 1, 'wf': 1})
    #         print(i)
    #         raise Exception('Test Exception')
    # print('print#1', '"Test Exception" did not stop run')

    with AudioStore() as a:
        for i in range(n):
            a.append({'timestamp': i, 'wf': [i] * repeat})
            print('print#2', f'{i=}', f'{len(a._tracks)=}', a)
            assert len(a._tracks) == i + 1
            print('print#3', f'{len(a) == 0=}')
            assert len(a) == 0
        print('print#4', f'{len(a._tracks) == n=}')
        assert len(a._tracks) == n
        print('print#5', a, len(a._tracks))

    print('print#6', len(a._tracks), a)
    assert len(a._tracks) == 0
    assert len(a) == ceil(n / N_TO_BULK), f'{len(a)=} == {ceil(n / N_TO_BULK)=}'
    for i, (k, v) in enumerate(sorted(a.items())):
        assert k == i * N_TO_BULK
        if k + N_TO_BULK > n:
            assert len(v) / repeat == n - k, f'{i=}, {k=}, {len(v) / repeat=}, {n - k=}'
        else:
            assert (
                len(v) / repeat == N_TO_BULK
            ), f'{i=}, {k=}, {len(v) / repeat=}, {N_TO_BULK=}'
        v_iter = iter(v)
        for j in range(i * N_TO_BULK, min((i + 1) * N_TO_BULK, n)):
            for _ in range(repeat):
                assert (
                    next(v_iter) == j
                ), f'{i=}, {j=}, {k=}, {i * N_TO_BULK=}, {min((i + 1) * N_TO_BULK, n)=}'


def _test_files_store():
    # WARNING: rootdir will be deleted at the start of test
    rootdir = Path('/tmp/plunk_audio_store_test/')
    if rootdir.is_dir():
        shutil.rmtree(rootdir)
    rootdir.mkdir()

    def ts_to_filename(ts, ext='.wav'):
        return f'{ts}{ext}'

    def filename_to_ts(name, ext='.wav'):
        return int(name[: -len(ext)])

    def wf_to_wav(wf, *, sr=44100, width_bytes=2, n_channels=1):
        header = encode_wav_header_bytes(
            sr, width_bytes, n_channels=n_channels, nframes=len(wf)
        )
        pcm = encode_pcm_bytes(wf, width_bytes * 8, n_channels)
        return header + pcm

    def wav_to_wf(wav):
        print(f'{wav=}')
        wf, sr = decode_wav_bytes(wav)
        return wf

    @track_method_calls(
        tracked_methods='append',
        tracking_mixin=bulk_append(bulk_kv=join_ts_wf),
        calls_tracker=track_calls_without_executing,
    )
    @appendable(item2kv=audio_slab_kv)
    @wrap_kvs(
        key_of_id=filename_to_ts,
        id_of_key=ts_to_filename,
        obj_of_data=wav_to_wf,
        data_of_obj=wf_to_wav,
    )
    class AudioStore(Files):
        def _id_of_key(self, k):
            return super()._id_of_key(str(k))

        # def _key_of_id(self, _id):
        #     return int(super()._key_of_id(_id))

    n = 22
    repeat = 2

    with AudioStore(rootdir='/tmp/plunk_audio_store_test/') as a:
        for i in range(n):
            a.append({'timestamp': i, 'wf': [i] * repeat})
            print('print#2', f'{i=}', f'{len(a._tracks)=}', a)
            assert len(a._tracks) == i + 1
            print('print#3', f'{len(a) == 0=}')
            assert len(a) == 0, list(a)
        print('print#4', f'{len(a._tracks) == n=}')
        assert len(a._tracks) == n
        print('print#5', a, len(a._tracks))

    print('print#6', len(a._tracks), a)
    assert len(a._tracks) == 0
    assert len(a) == ceil(n / N_TO_BULK), f'{len(a)=} == {ceil(n / N_TO_BULK)=}'
    for i, (_k, _v) in enumerate(sorted(a.items())):
        k = int(_k)
        v = decode_pcm_bytes(_v)
        assert k == i * N_TO_BULK
        if k + N_TO_BULK > n:
            assert len(v) / repeat == n - k, f'{i=}, {k=}, {len(v) / repeat=}, {n - k=}'
        else:
            assert (
                len(v) / repeat == N_TO_BULK
            ), f'{i=}, {k=}, {len(v) / repeat=}, {N_TO_BULK=}'
        v_iter = iter(v)
        for j in range(i * N_TO_BULK, min((i + 1) * N_TO_BULK, n)):
            for _ in range(repeat):
                assert (
                    next(v_iter) == j
                ), f'{i=}, {j=}, {k=}, {i * N_TO_BULK=}, {min((i + 1) * N_TO_BULK, n)=}'


if __name__ == '__main__':
    _test_dict_store()
    _test_files_store()
