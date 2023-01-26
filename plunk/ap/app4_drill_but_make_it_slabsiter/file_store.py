from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Callable, Any

from front.crude import DillFiles


@dataclass
class ItemGetter:
    instance: Any
    key: Any

    def __call__(self):
        return self.instance[self.key]


class UploadFilesStore(DillFiles):
    def item_getter(self, key) -> ItemGetter:
        """Wraps value in a callable to be retrieved later"""
        return ItemGetter(self, key)

    def getter_items(self):
        """Like dict.items() method but the values are ItemGetters"""
        for k in self:
            yield k, self.item_getter(k)

    @classmethod
    def resolve_item_getter(cls, value):
        return value() if isinstance(value, ItemGetter) else value

    @classmethod
    def resolve_item_getter_args(cls, func):
        """Function decorator to resolve any args and kwargs that are ItemGetters"""

        @wraps(func)
        def wrapped(*args, **kwargs):
            _kwargs = {k: cls.resolve_item_getter(v) for k, v in kwargs.items()}
            _args = (cls.resolve_item_getter(v) for v in args)
            return func(*_args, **_kwargs)

        return wrapped


upload_files_store_rootdir = Path.cwd() / 'upload_files_store'
upload_files_store_rootdir.mkdir(parents=True, exist_ok=True)
STORE = UploadFilesStore(rootdir=str(upload_files_store_rootdir))


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
