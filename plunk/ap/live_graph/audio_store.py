from dol import appendable
from mongodol.tracking_methods import track_method_calls


def audio_slab_kv(data: dict):
    return data.get('timestamp'), data.get('wf')


@track_method_calls(tracked_methods='append')
@appendable(item2kv=audio_slab_kv)
class AudioStore(dict):
    pass


def _test_store():
    """
    0
    print#0 "assert False" did not stop run
    0
    print#1 "Test Exception" did not stop run
    print#2 i=0 len(a._tracks)=1 {0: [0]}
    print#3 len(a) == 0=False
    print#2 i=1 len(a._tracks)=2 {0: [0], 1: [1]}
    print#3 len(a) == 0=False
    print#2 i=2 len(a._tracks)=3 {0: [0], 1: [1], 2: [2]}
    print#3 len(a) == 0=False
    print#4 len(a._tracks) == n=True
    print#5 {0: [0], 1: [1], 2: [2]} 3
    print#6 0 {0: [0], 1: [1], 2: [2]}

    :return:
    """
    n = 3
    with AudioStore() as a:
        for i in range(n):
            a.append({'timestamp': 1, 'wf': 1})
            print(i)
            assert False, 'testing assert'

    print('print#0', '"assert False" did not stop run')

    with AudioStore() as a:
        for i in range(n):
            a.append({'timestamp': 1, 'wf': 1})
            print(i)
            raise Exception('Test Exception')

    print('print#1', '"Test Exception" did not stop run')

    with AudioStore() as a:
        for i in range(n):
            a.append({'timestamp': i, 'wf': [i]})
            print('print#2', f'{i=}', f'{len(a._tracks)=}', a)
            assert len(a._tracks) == i + 1
            print('print#3', f'{len(a) == 0=}')
            # assert len(a) == 0
        print('print#4', f'{len(a._tracks) == n=}')
        assert len(a._tracks) == n
        print('print#5', a, len(a._tracks))

    print('print#6', len(a._tracks), a)
    assert len(a._tracks) == 0
    assert len(a) == n


if __name__ == '__main__':
    _test_store()
