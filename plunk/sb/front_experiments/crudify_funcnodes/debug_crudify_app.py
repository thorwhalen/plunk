from know.boxes import *
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY
from streamlitfront import mk_app, binder as b
from typing import Mapping
from i2 import Sig
from front.dag import crudify_funcs
from meshed import code_to_dag

from streamlitfront.elements import SelectBox


def foo(x, y, z="23"):
    return int(x) + int(y) * int(z)


def bar(res, other="stuff"):
    return f"{res=}, {other=}"


from i2 import include_exclude, rm_params


@code_to_dag
def dag():
    res = first_func(x, y, z)
    result = second_func(res, other)


dag = dag.ch_funcs(
    first_func=rm_params(foo, params_to_remove=("z",)),
    second_func=bar,
)


def mk_pipeline_maker_app_with_mall(
    mall: Mapping,
):

    if not b.mall():
        b.mall = mall
    mall = b.mall()

    _funcs = crudify_funcs(var_nodes="res result", dag=dag, mall=mall)

    print(dag.synopsis_string())

    def debug_check_mall():
        st.write(mall)
        return None

    step1, step2 = _funcs

    print(f"{step1.__name__ =}")
    print(f"{step2.__name__ =}")

    config = {
        APP_KEY: {"title": "Data Preparation"},
        RENDERING_KEY: {
            "step2": {
                "execution": {
                    "inputs": {
                        "bar": {
                            ELEMENT_KEY: SelectBox,
                            "options": mall["res_store"],
                        },
                    },
                },
            },
        },
    }
    funcs = [
        step1,
        step2,
        debug_check_mall,
    ]

    app = mk_app(funcs, config=config)

    return app


if __name__ == "__main__":
    import streamlit as st

    mall = dict(
        res_store=dict(),
    )

    app = mk_pipeline_maker_app_with_mall(mall)

    app()
