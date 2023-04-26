"""
Instructions:

In one terminal window, run:
    python o/plunk/plunk/tw/crude_and_selectbox_bug_api.py
In another terminal window, run:
    python o/plunk/plunk/tw/crude_and_selectbox_bug.py
"""
from front.crude import prepare_for_crude_dispatch, Crudifier
from functools import partial
from front.crude import DillFiles
from streamlitfront import binder as b


# mall = {'x_store': DillFiles}

if not b.mall():
    b.mall = {'x_store': dict()}
mall = b.mall()


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




if __name__ == '__main__':

    from streamlitfront.tools import validate_config

    validate_config(config, funcs)  # validate config against funcs

    # # For mk_web_app version, need to:
    # # In one terminal window, run:
    # #     python o/plunk/plunk/tw/crude_and_selectbox_bug_api.py
    # # In another terminal window, run:
    # #     python o/plunk/plunk/tw/crude_and_selectbox_bug.py
    # from extrude import mk_web_app
    # app = mk_web_app(funcs, config=config, api_url='http://localhost:3030/openapi')

    from streamlitfront import mk_app
    app = mk_app(funcs, config=config)

    app()
