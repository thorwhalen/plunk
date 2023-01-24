from functools import wraps
from pathlib import Path
from typing import Callable, Union

from dol import Files, wrap_kvs
from front.crude import DillFiles

from plunk.ap.live_graph.audio_store import merge_and_write_upon_count


class UploadFilesStore(DillFiles):
    pass


rootdir = Path.cwd() / 'upload_files_store'
rootdir.mkdir(parents=True, exist_ok=True)
STORE = UploadFilesStore(rootdir=str(rootdir))


def upload_files_store(
    func: Callable = None,
    *,
    store: UploadFilesStore = STORE,
    get_kv=lambda *a, _return_value=None, **kw: (kw['save_name'], _return_value),
):
    def _decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            print(f'upload_files_store: {args=}, {kwargs=}')

            return_value = f(*args, **kwargs)

            try:
                k, v = get_kv(*args, _return_value=return_value, **kwargs)
            except Exception as e:
                raise type(e)(
                    f'upload_files_store error: get_kv(*{args=}, **{kwargs=})'
                ) from e
            store[k] = v
            return return_value

        return wrapped

    return _decorator(func) if callable(func) else _decorator
