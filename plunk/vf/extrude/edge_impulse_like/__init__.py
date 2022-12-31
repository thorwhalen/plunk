from functools import partial
from typing import Any
from front.crude import Crudifier

mall = dict(wf=dict())
crudifier = partial(Crudifier, mall=mall, include_stores_attribute=True)


def identity(x):
    print(x)
    print(type(x))
    return x


def wrap(wrapper, f, f_name):
    _f = wrapper(f)
    _f.__name__ = f_name
    _f.__qualname__ = f_name
    return _f


upload_data = wrap(crudifier(output_store='wf'), identity, 'upload_data')
get_data = wrap(crudifier(param_to_mall_map=dict(x='wf')), identity, 'get_data')

funcs = [upload_data, get_data]
