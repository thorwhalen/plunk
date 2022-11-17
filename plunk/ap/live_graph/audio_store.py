from functools import cached_property
from itertools import chain
from operator import itemgetter

from dol import appendable
from mongodol.tracking_methods import (
    track_method_calls,
    track_calls_without_executing,
    TrackableMixin,
)


audio_slab_kv = itemgetter('timestamp', 'wf')


def should_bulk_if_bt_within_n(self, item, n=10):
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
    print(list(map(itemgetter('wf'), bulk)))
    joined_wf = list(chain(map(itemgetter('wf'), bulk)))
    return {'timestamp': ts, 'wf': joined_wf}


def bulk_append(
    should_bulk=should_bulk_if_bt_within_n, bulk_kv=join_ts_wf,
):
    class BulkAppend(TrackableMixin):
        bulk_factory = list
        _should_bulk = should_bulk  # TODO: add as method
        _bulk_kv = bulk_kv

        @cached_property
        def _bulk(self):
            return self.bulk_factory()

        def _execute_tracks(self):
            for func, args, kwargs in self._tracks:
                if kv := self._bulk_append(*args, **kwargs):
                    func(self, kv)
            if len(self._bulk) > 0:
                kv = self._bulk_kv(self._bulk)
                func(self, kv)

        def _bulk_append(self, item):
            if len(self._bulk) > 0:
                if self._should_bulk(item):
                    self._bulk.append(item)
                else:
                    print('writing', item)
                    rv = self._bulk_kv(self._bulk)
                    self._bulk.clear()
                    self._bulk.append(item)
                    return rv
            else:
                self._bulk.append(item)
            return None

    return BulkAppend


def _test_store():
    @track_method_calls(
        tracked_methods='append',
        tracking_mixin=bulk_append(),
        calls_tracker=track_calls_without_executing,
    )
    @appendable(item2kv=audio_slab_kv)
    class AudioStore(dict):
        pass

    n = 22
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
            a.append({'timestamp': i, 'wf': [i]})
            print('print#2', f'{i=}', f'{len(a._tracks)=}', a)
            assert len(a._tracks) == i + 1
            print('print#3', f'{len(a) == 0=}')
            assert len(a) == 0
        print('print#4', f'{len(a._tracks) == n=}')
        assert len(a._tracks) == n
        print('print#5', a, len(a._tracks))

    print('print#6', len(a._tracks), a)
    assert len(a._tracks) == 0


if __name__ == '__main__':
    print(audio_slab_kv({'timestamp': 1, 'wf': 2}))
    _test_store()
