

import re
from streamlitfront import mk_app
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY

from plunk.ap.store_explorer.store_explorer_element import get_mall


_mall = dict(
    # Factory Input Stores
    sound_output=dict(),
    # Output Store
    data=dict(
        aaa=1,
        bbb='2',
        ccc=[3],
        ddd={'4': 4, '5': [{'e': 6}, {'f': 7}, ['g', 'h', 'i']]},
        jjj=[{'k': 8, 'l': 9}, 'm', 10],
    ),
)
mall = get_mall(_mall)


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


def explore_mall(
    key_filter: str,
    match_case: bool = False,
    match_whole_key: bool = False,
    use_regex: bool = False,
):
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


if __name__ == '__main__':

    app = mk_app(
        [explore_mall],
        config={
            APP_KEY: {'title': 'Store Explorer'},
            RENDERING_KEY: {
                'explore_mall': {
                    'execution': {
                        'auto_submit': True,
                    }
                }
            }
        },
    )
    app()