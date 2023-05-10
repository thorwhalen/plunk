"""
An app that loads either a wav file from local folder or records a sound
and visualizes the resulting numpy array 
"""

# TODO: VF --> Review and propose refactors to eliminate some complexity

from typing import Mapping
from typing import Callable, Iterable
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from front.crude import Crudifier, prepare_for_crude_dispatch
from lined import LineParametrized

from streamlitfront import mk_app, binder as b
from streamlitfront.elements import (
    SelectBox,
    SuccessNotification,
    PipelineMaker,
)
from front.crude import Crudifier, prepare_for_crude_dispatch

import streamlit as st
from functools import partial

from dataclasses import dataclass
from front.elements import InputBase, ExecContainerBase


def _init_cache(key, init_value):
    if not b[key]():
        b[key].set(init_value)


@dataclass
class ExtendableListInput(InputBase):
    choices: list = None
    callback: Callable = None

    def render(self):

        dForm = st.form(clear_on_submit=True, key='dfForm')
        with dForm:
            dfColumns = st.columns(2)
            with dfColumns[0]:
                choice1 = st.selectbox('Select', self.choices, key='input_1_select')
            with dfColumns[1]:
                choice2 = st.selectbox('Select', self.choices, key='input_2_select')

                st.form_submit_button(
                    label='add one more edge',
                    on_click=lambda: self.callback((choice1, choice2)),
                )


def mk_pipeline_maker_app_with_mall(
    mall: Mapping,
    *,
    steps: str = 'steps',
    edges_store: str = 'edges_store',
):
    if not b.mall():
        b.mall = mall
    mall = b.mall()

    crudifier = partial(Crudifier, mall=mall)

    @crudifier(param_to_mall_map=dict(edge=steps), output_store=edges_store)
    def add_edge(edge):
        return edge

    # b.selected_multichoice = []

    def on_select_choice(item):

        b.selected_multichoice().append(item)

    def debug():
        st.write(b.selected_multichoice())
        st.write(mall)

    _init_cache('selected_multichoice', [])

    config = {
        APP_KEY: {'title': 'Dag Maker'},
        RENDERING_KEY: {
            'add_edge': {
                NAME_KEY: 'Dag Maker',
                'execution': {
                    'inputs': {
                        'edge': {
                            ELEMENT_KEY: ExtendableListInput,
                            'choices': list(mall[steps].values()),
                            'callback': on_select_choice,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': f'Edges created: {b.selected_multichoice()}',
                    },
                },
            },
        },
    }

    funcs = [add_edge, debug]
    app = mk_app(funcs, config=config)

    return app


if __name__ == '__main__':

    mall = dict(
        # Output Store
        steps={'a': 'stepa', 'b': 'stepb'},
        edges_store=dict(),
    )

    crudifier = partial(prepare_for_crude_dispatch, mall=mall)

    app = mk_pipeline_maker_app_with_mall(mall, steps='steps')

    app()
