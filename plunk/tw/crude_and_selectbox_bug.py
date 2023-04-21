"""
Instructions:

In one terminal window, run:
    python o/plunk/plunk/tw/crude_and_selectbox_bug_api.py
In another terminal window, run:
    python o/plunk/plunk/tw/crude_and_selectbox_bug.py
"""
from front.crude import prepare_for_crude_dispatch, Crudifier
from functools import partial

mall = {'x_store': dict()}


crudifier = partial(Crudifier, mall=mall)


def f(x):
    return f"this is {x}"


def g(y):
    return y.upper()


ff = crudifier(
    output_store='x_store',
)(f)
gg = crudifier(
    param_to_mall_map={'y': 'x_store'},
)(g)

def debug(ignore_this_just_click_select):
    return mall


funcs = [ff, gg, debug]

import i2

print(f"{ff.__name__}: {i2.Sig(ff)}")
print(f"{gg.__name__}: {i2.Sig(gg)}")




from front import APP_KEY, RENDERING_KEY, NAME_KEY, ELEMENT_KEY
from streamlitfront.elements import SelectBox

config = {
    APP_KEY: {'title': 'Data Preparation'},
    # RENDERING_KEY: {
    #     'g': {
    #         NAME_KEY: 'gg func',
    #
    #         'execution': {
    #             'inputs': {
    #                 'illustration_description': {
    #                     ELEMENT_KEY: SelectBox,
    #                 },
    #             },
    #
    #         },
    #     },
    # }
}


from extrude import mk_web_app
from streamlitfront.tools import validate_config


if __name__ == '__main__':
    validate_config(config, funcs)  # validate config against funcs
    app = mk_web_app(funcs, config=config, api_url='http://localhost:3030/openapi')
    # app = mk_web_app(funcs, config=config)
    app()
