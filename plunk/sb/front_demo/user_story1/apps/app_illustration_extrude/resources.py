from front.crude import prepare_for_crude_dispatch
from mall import mall
from functools import partial

crudifier = partial(
    prepare_for_crude_dispatch, mall=mall, include_stores_attribute=True
)


@crudifier(output_store='x_store', output_trans=lambda: None)
def f(x):
    return f"this is {x}"


@crudifier(
    param_to_mall_map={'y': 'x_store'},
)
def g(y):
    return y.upper()


def debug(ignore_this_just_click_select):
    return mall


funcs = [f, g, debug]
