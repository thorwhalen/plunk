"""
An app that loads either a wav file from local folder or records a sound
and visualizes the resulting numpy array 
"""
from typing import Mapping
from know.boxes import *
from functools import partial
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from front.crude import Crudifier

from streamlitfront import mk_app, binder as b
from streamlitfront.elements import (
    SuccessNotification,
    PipelineMaker,
)

import streamlit as st
from dataclasses import dataclass

from typing import List


@dataclass
class Pipeline:
    steps: List[str]


def get_steps_from_selected_pipeline(pipeline):
    return pipeline.steps


def mk_pipeline_maker_app_with_mall(
    mall: Mapping, *, pipelines: str = 'pipelines', pipelines_store=None,
):
    if not b.mall():
        b.mall = mall
    mall = b.mall()

    crudifier = partial(Crudifier, mall=mall)

    pipelines_store = pipelines_store or pipelines

    @crudifier(
        param_to_mall_map=dict(pipeline=pipelines_store), output_store=pipelines_store,
    )
    def modify_pipeline(pipeline, steps):
        pipe = Pipeline(steps=steps)
        return pipe

    def view_state():
        st.write(mall)

    def on_select_pipeline(pipeline):
        b.steps_of_selected_pipeline.set(mall['pipelines'][pipeline].steps)
        st.write(f'{pipeline=} selected')

    config = {
        APP_KEY: {'title': 'Data Preparation'},
        RENDERING_KEY: {
            'modify_pipeline': {
                NAME_KEY: 'Pipeline Modify',
                'execution': {
                    'inputs': {
                        'pipeline': {
                            'value': b.selected_pipeline,
                            'on_value_change': on_select_pipeline,
                        },
                        'steps': {
                            ELEMENT_KEY: PipelineMaker,
                            'items': ['a', 'b'],
                            'steps': b.steps_of_selected_pipeline(),
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The pipeline has been modified successfully.',
                    },
                },
            },
        },
    }

    funcs = [
        modify_pipeline,
        view_state,
    ]
    app = mk_app(funcs, config=config)

    return app


mall = dict(
    pipelines={
        'pipe1': Pipeline(steps=['a', 'b']),
        'pipe2': Pipeline(steps=['b', 'a']),
    },
)


if __name__ == '__main__':

    app = mk_pipeline_maker_app_with_mall(mall, pipelines='pipelines')

    app()
