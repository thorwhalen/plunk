"""An app that loads wav file from local folder"""
import re
from functools import partial, reduce, wraps
from typing import Iterable

from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY

from front.crude import Crudifier

from streamlitfront import mk_app, binder as b
from streamlitfront.elements import SuccessNotification, SelectBox
from streamlitfront.elements import FileUploader

from plunk.ap.store_explorer.store_explorer_element import (
    StoreExplorerOutput,
    StoreExplorerInput,
)
from plunk.ap.snippets import get_mall


def tuple_wrap(f):
    @wraps(f)
    def _wrap(*a, **kw):
        return (), f(*a, **kw)

    return _wrap


def mk_pipeline_maker_app_with_mall(mall: dict):
    mall = get_mall(mall)

    def on_select_mall_name():
        print(f'{b.selected_mall_name()=}')
        b.selected_mall.set(mall[b.selected_mall_name()])

    if not b.mall_names():
        b.mall_names = lambda: list(mall)
        b.selected_mall_name.set(next(iter(b.mall_names()())))
        on_select_mall_name()
    crudifier = partial(Crudifier, mall=mall)

    @crudifier(output_store='sound_output')
    def upload_sound(train_audio: list, tag: str):
        return train_audio, tag

    def explore_mall(mall_name, depth_keys: Iterable = ()):
        return depth_keys, reduce(lambda o, k: o[k], depth_keys, mall[mall_name])

    @tuple_wrap
    def search_mall(
        key_filter: str,
        match_case: bool = False,
        match_whole_key: bool = False,
        use_regex: bool = False,
    ):
        """By vf"""

        def filter_dict_in_depth(d, predicate):
            def build_filtered_dict():
                for k, v in d.items():
                    if predicate(k):
                        yield k, v
                    elif isinstance(v, dict):
                        _v = filter_dict_in_depth(v, predicate)
                        if _v:
                            yield k, _v

            return {k: v for k, v in build_filtered_dict()}

        if not key_filter:
            return mall
        if not match_case:
            key_filter = key_filter.lower()
        if use_regex:

            def include_key(key):
                if not match_case:
                    key = key.lower()
                regex = f'^{key_filter}$' if match_whole_key else key_filter
                if re.search(regex, str(key)):
                    return True
                return False

        else:

            def include_key(key):
                if not match_case:
                    key = key.lower()
                if match_whole_key:
                    return key_filter == key
                return key_filter in str(key)

        return filter_dict_in_depth(mall, include_key)

    config = {
        APP_KEY: {'title': 'Data Preparation'},
        RENDERING_KEY: {
            'upload_sound': {
                # NAME_KEY: "Data Loader",
                'execution': {
                    'inputs': {
                        'train_audio': {
                            ELEMENT_KEY: FileUploader,
                            'type': 'wav',
                            'accept_multiple_files': True,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'Wav files loaded successfully.',
                    },
                },
            },
            'explore_mall': {
                'execution': {
                    'inputs': {
                        'mall_name': {
                            ELEMENT_KEY: SelectBox,
                            'options': b.mall_names(),
                            'value': b.selected_mall_name,
                            'on_value_change': on_select_mall_name,
                        },
                        'depth_keys': {
                            ELEMENT_KEY: StoreExplorerInput,
                            'mall': b.selected_mall,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: StoreExplorerOutput,
                        'write_depth_keys': True,
                    },
                    'auto_submit': True,
                },
            },
            'search_mall': {
                'execution': {
                    'output': {
                        ELEMENT_KEY: StoreExplorerOutput,
                        'write_depth_keys': False,
                    },
                    'auto_submit': True,
                },
            },
        },
    }

    funcs = [
        explore_mall,
        search_mall,
        upload_sound,
    ]
    app = mk_app(funcs, config=config)

    return app


_mall = dict(
    # Factory Input Stores
    sound_output=dict(),
    # Output Store
    data=dict(
        a=1,
        b='2',
        c=[3],
        d={'4': 4, '5': [{'e': 6}, {'f': 7}, ['g', 'h', 'i']]},
        j=[{'k': 8, 'l': 9}, 'm', 10],
    ),
)


if __name__ == '__main__':

    app = mk_pipeline_maker_app_with_mall(_mall)

    app()
