from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from collections.abc import Callable

from streamlitfront import mk_app, binder as b
from streamlitfront.elements import SelectBox
from typing import Any
from streamlitfront.elements import MultiSourceInput
import streamlit as st
from front.elements import InputBase
from i2 import Sig
from dataclasses import dataclass
from streamlitfront.elements import TextInput, SelectBox
from functools import partial
from front.crude import Crudifier


# # ============ MALL ===============
# if not b.mall():
#     b.mall = dict(func_store={})

# mall = b.mall()


def foo(x: str, y: int):
    return str(x) * int(y)


def bar(msg: str):
    return msg


data = ["foo", "bar"]
metadata = {"foo": foo, "bar": bar}


# @Crudifier(output_store="func_store", mall=mall)
def my_map(func, kwargs):
    # return partial(func, **kwargs)
    return kwargs


def expand_names(names):
    return {name: {ELEMENT_KEY: TextInput} for name in names}


def populate_kwargs():
    value = b.selected_func()
    list_names = list(Sig(metadata[value]).names)
    b.names_for_kwargs.set(expand_names(list_names))
    st.write(b.names_for_kwargs())


if __name__ == "__main__":
    app = mk_app(
        [my_map],
        config={
            APP_KEY: {"title": "Rendering map"},
            RENDERING_KEY: {
                "my_map": {
                    "execution": {
                        "inputs": {
                            "func": {
                                ELEMENT_KEY: SelectBox,
                                "options": data,
                                "value": b.selected_func,
                                "on_value_change": populate_kwargs,
                            },
                            "kwargs": {
                                ELEMENT_KEY: MultiSourceInput,
                                # "a": {ELEMENT_KEY: TextInput},
                                **b.names_for_kwargs(),
                            },
                        }
                    }
                },
            },
        },
    )
    app()
