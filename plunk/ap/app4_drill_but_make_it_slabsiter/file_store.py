from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Callable, Any

from boltons.iterutils import default_enter, remap
from dol import Files, wrap_kvs
from front.crude import DillFiles

from plunk.ap.persist.persist import Persist

store_rootdir = Path.cwd()


@dataclass
class ItemGetter:
    instance: Any
    key: Any

    def __call__(self):
        # print(f'ItemGetter({self.instance=}, {self.key=})={self.instance[self.key]}')
        return self.instance[self.key]


class UploadFilesStore(DillFiles):
    def item_getter(self, key) -> ItemGetter:
        """Wraps value in a callable to be retrieved later"""
        return ItemGetter(self, key)

    def getter_items(self):
        """Like dict.items() method but the values are ItemGetters"""
        for k in self:
            yield k, self.item_getter(k)


upload_files_store_rootdir = store_rootdir / 'upload_files_store'
upload_files_store_rootdir.mkdir(parents=True, exist_ok=True)
upload_files_store = UploadFilesStore(rootdir=str(upload_files_store_rootdir))


def add_to_upload_files_store(
    func: Callable = None,
    *,
    store: UploadFilesStore = upload_files_store,
    get_kv=lambda *a, _return_value=None, _function=None, **kw: (
        kw['save_name'],
        _return_value,
    ),
):
    def _decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            return_value = f(*args, **kwargs)

            try:
                k, v = get_kv(*args, _return_value=return_value, _function=f, **kwargs)
            except Exception as e:
                raise type(e)(
                    f'add_to_upload_files_store error: get_kv(*{args=}, **{kwargs=})'
                ) from e
            store[k] = v
            return return_value

        return wrapped

    return _decorator(func) if callable(func) else _decorator


wrap_kvs_to_bytes_from_persist = wrap_kvs(
    data_of_obj=lambda x: bytes(x, 'utf-8'),
    obj_of_data=lambda x: Persist.deserialize(x),
)


@wrap_kvs_to_bytes_from_persist
class PipelineStepStore(Files):
    def item_getter(self, key) -> ItemGetter:
        """Wraps value in a callable to be retrieved later"""
        return ItemGetter(instance=wrap_kvs_to_bytes_from_persist(self), key=key)

    def getter_items(self):
        """Like dict.items() method but the values are ItemGetters"""
        for k in self:
            yield k, self.item_getter(k)


def resolve_item_getter(value):
    # print(f'resolve_item_getter: {value=}')
    return value() if isinstance(value, ItemGetter) else value


def _visit(path, key, value):
    value = resolve_item_getter(value)
    return key, value


def _enter(path, key, value):
    if isinstance(value, ItemGetter):
        return None, False
    else:
        return default_enter(path, key, value)


def resolve_item_getter_args(func):
    """Function decorator to resolve any args and kwargs that are ItemGetters"""

    @wraps(func)
    def wrapped(*args, **kwargs):
        _args = remap(args, visit=_visit, enter=_enter)
        _kwargs = remap(kwargs, visit=_visit, enter=_enter)
        return func(*_args, **_kwargs)

    return wrapped


pipeline_step_store_rootdir = store_rootdir / 'pipeline_step_store'
pipeline_step_store_rootdir.mkdir(parents=True, exist_ok=True)
pipeline_step_store = PipelineStepStore(rootdir=str(pipeline_step_store_rootdir))
add_to_pipeline_step_store = add_to_upload_files_store(
    store=pipeline_step_store,
    get_kv=lambda *a, _return_value=None, _function=None, **kw: (
        kw['save_name'],
        (_function, a, kw),
    ),
)


def _test_pipeline_step_store():
    from tempfile import TemporaryDirectory
    from plunk.ap.persist.test_persist import add

    with TemporaryDirectory() as tmpdirname:
        pipeline_step_store = PipelineStepStore(rootdir=tmpdirname)
        pipeline_step_store['1+2'] = Persist.serialize_function_call(
            args=(1, 2), kwargs=None, function=add
        )
        assert pipeline_step_store['1+2'] == 3

        pipeline_step_store['2+2'] = Persist.serialize_function_call(
            args=(2, 2), kwargs=None, function=add
        )
        assert pipeline_step_store['2+2'] == 4

        item_getter_list = [v for k, v in pipeline_step_store.getter_items()]
        item_list = [v for k, v in pipeline_step_store.items()]

        @resolve_item_getter_args
        def print_and_return_list(l):
            print(l)
            return l

        resolved = print_and_return_list(item_getter_list)
        print(resolved)
        assert resolved == item_list, f'{item_list=} {resolved=}'


if __name__ == '__main__':
    _test_pipeline_step_store()
