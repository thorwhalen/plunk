"""Ideas for routing
See https://github.com/i2mint/i2/issues/40
"""

from typing import Mapping, Callable, TypeVar, KT, VT, Union
from i2 import mk_sentinel

Obj = TypeVar('Obj')
KeyFunc = Callable[[Obj], KT]
dflt_not_found_sentinel = mk_sentinel('dflt_not_found_sentinel')


def identity(x):
    return x


def key_func_mapping(
    obj: Obj,
    mapping: Mapping[KT, VT],
    key: KeyFunc = identity,
    not_found_sentinel=dflt_not_found_sentinel,
) -> VT:
    """Map an object to a value based on a key function"""
    return mapping.get(key(obj), not_found_sentinel)
