"""
An app that loads either a wav file from local folder or records a sound
and visualizes the resulting numpy array 
"""
from typing import Mapping
from know.boxes import *
from functools import partial
from typing import Callable, Iterable
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from i2 import Pipe, Sig
from front.crude import Crudifier, prepare_for_crude_dispatch
from lined import LineParametrized
import numpy as np

from streamlitfront import mk_app, binder as b
from streamlitfront.elements import (
    SelectBox,
    SuccessNotification,
    PipelineMaker,
    KwargsInput,
)
from streamlitfront.elements import (
    AudioRecorder,
    FileUploader,
    MultiSourceInput,
)
import streamlit as st
from dataclasses import dataclass
import soundfile as sf
from io import BytesIO
from plunk.sb.front_demo.user_story1.components.components import (
    AudioArrayDisplay,
    GraphOutput,
    ArrayPlotter,
    ArrayWithIntervalsPlotter,
)
from plunk.sb.front_demo.user_story1.utils.tools import (
    DFLT_FEATURIZER,
    DFLT_CHK_SIZE,
    chunker,
    WaveForm,
    Stroll,
    clean_dict,
    scores_to_intervals,
)
from typing import List

from front.elements import SelectBoxBase


def simple_chunker(wfs, chk_size: int = DFLT_CHK_SIZE):
    return list(chunker(wfs, chk_size=chk_size))


def simple_featurizer(chks):
    fvs = np.array(list(map(DFLT_FEATURIZER, chks)))
    return fvs


# @dataclass
# class KwargsInput(KwargsInputBase):
#     def render(self):
#         exec_section = ExecSection(
#             obj=self.get_kwargs,
#             inputs=self.inputs,
#             output={ELEMENT_KEY: HiddenOutput},
#             auto_submit=True,
#             on_submit=self._return_kwargs,
#             use_expander=False,
#         )
#         exec_section()
#         return self.value()


# @dataclass
# class PipelineMaker(InputBase):
#     items: Iterable = None
#     steps: Iterable = None
#     serializer: Callable = None

#     def render(self):
#         return pipeline_maker(
#             items=self.items, steps=self.steps, serializer=self.serializer,
#         )


@dataclass
class Step:
    step_factory: Callable
    step: Callable


@dataclass
class Pipeline:
    steps: List[Step]
    pipe: Callable

    def dot_digraph(self):
        return self.pipe.dot_digraph()


@dataclass
class SelectBoxWithSubmit(SelectBoxBase):
    call_back: Callable = lambda: None

    def render(self):
        with st.form('my_form'):
            st.write('Inside the form')
            selected = st.selectbox(
                label=self.name, options=self._options, index=self._preselected_index,
            )
            # Every form must have a submit button.
            submitted = st.form_submit_button('Submit')
            if submitted:
                self.call_back(selected)


def get_steps_from_selected_pipeline(pipeline):
    return pipeline.steps


def mk_pipeline_maker_app_with_mall(
    mall: Mapping,
    *,
    step_factories: str = 'step_factories',
    steps: str = 'steps',
    steps_store=None,
    pipelines: str = 'pipelines',
    pipelines_store=None,
    data: str = 'data',
    data_store=None,
    learned_models=None,
    models_scores=None,
):
    if not b.mall():
        b.mall = mall
    mall = b.mall()
    if not b.selected_step_factory():
        b.selected_step_factory = 'chunker'  # TODO make this dynamic

    crudifier = partial(Crudifier, mall=mall)

    steps_store = steps_store or steps
    data_store = data_store or data
    pipelines_store = pipelines_store or pipelines

    @crudifier(
        param_to_mall_map=dict(step_factory=step_factories), output_store=steps_store
    )
    def mk_step(step_factory: Callable, kwargs: dict):
        kwargs = clean_dict(kwargs)  # TODO improve that logic
        step = partial(step_factory, **kwargs)()
        result = Step(step=step, step_factory=step_factory)
        return result

    @crudifier(
        param_to_mall_map=dict(step_to_modify=steps_store), output_store=steps_store
    )
    def modify_step(step_to_modify: Step, kwargs: dict):

        kwargs = clean_dict(kwargs)  # TODO improve that logic
        step_factory = step_to_modify.step_factory
        step = partial(step_factory, **kwargs)()
        return Step(step=step, step_factory=step_factory)

    #
    @crudifier(output_store=pipelines_store,)
    def mk_pipeline(steps: Iterable[Callable]):
        named_funcs = [(get_step_name(step), step) for step in steps]
        pipeline = Pipeline(steps=steps, pipe=LineParametrized(*named_funcs))
        return pipeline

    @crudifier(
        param_to_mall_map=dict(pipeline=pipelines_store), output_store=pipelines_store,
    )
    def modify_pipeline(pipeline, steps):
        st.write(f'current pipeline={pipeline}')
        named_funcs = [(get_step_name(step), step) for step in steps]
        pipe = LineParametrized(*named_funcs)
        return Pipeline(steps=named_funcs, pipe=pipe)

    @crudifier(param_to_mall_map=dict(pipeline=pipelines_store),)
    def visualize_pipeline(pipeline: Pipeline):

        return pipeline

    def get_step_name(step):
        return [k for k, v in mall[steps].items() if v.step == step][0]

    def get_selected_step_factory_sig():
        selected_step_factory = mall['step_factories'].get(
            b.selected_step_factory.get()
        )
        if selected_step_factory:
            return Sig(selected_step_factory)

    # get_step_to_modify_factory_sig #TODO: refactor this
    def get_step_to_modify_factory_sig():
        selected_step_factory = (
            mall['steps'].get(b.selected_step_to_modify.get()).step_factory
        )
        if selected_step_factory:
            return Sig(selected_step_factory)

    def view_state():
        st.write(mall)

    def dummy(input: List[int]):
        return input

    def on_select_pipeline(pipeline):
        b.steps_of_selected_pipeline.set(mall['pipelines'][pipeline].steps)
        st.write(f'{pipeline=} selected')

    config = {
        APP_KEY: {'title': 'Data Preparation'},
        RENDERING_KEY: {
            'mk_step': {
                NAME_KEY: 'Pipeline Step Maker',
                'execution': {
                    'inputs': {
                        'step_factory': {'value': b.selected_step_factory,},
                        'kwargs': {'func_sig': get_selected_step_factory_sig},
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The step has been created successfully.',
                    },
                },
            },
            'modify_step': {
                NAME_KEY: 'Modify Step',
                'execution': {
                    'inputs': {
                        'step_to_modify': {'value': b.selected_step_to_modify,},
                        'kwargs': {'func_sig': get_step_to_modify_factory_sig},
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The step has been created successfully.',
                    },
                },
            },
            'mk_pipeline': {
                NAME_KEY: 'Pipeline Maker',
                'execution': {
                    'inputs': {
                        steps: {
                            ELEMENT_KEY: PipelineMaker,
                            'items': [v.step for v in mall[steps].values()],
                            'serializer': get_step_name,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The pipeline has been created successfully.',
                    },
                },
            },
            'modify_pipeline': {
                NAME_KEY: 'Pipeline Modify',
                'execution': {
                    'inputs': {
                        'pipeline': {
                            ELEMENT_KEY: SelectBoxWithSubmit,
                            'call_back': on_select_pipeline,
                            'value': b.selected_pipeline,
                            'on_value_change': on_select_pipeline,
                            # "auto_submit": True,
                        },
                        steps: {
                            ELEMENT_KEY: PipelineMaker,
                            'items': [v.step for v in mall[steps].values()],
                            # "steps": [
                            #     # get_step_name(step)
                            #     step
                            #     # for step in mall["pipelines"][b.selected_pipeline()]
                            #     for step in [v.step for v in mall[steps].values()]
                            # ],
                            # "steps": mall["pipelines"][b.selected_pipeline.get()].steps,
                            # or [],
                            'steps': b.steps_of_selected_pipeline(),
                            'serializer': get_step_name,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The pipeline has been modified successfully.',
                    },
                },
            },
            'visualize_pipeline': {
                NAME_KEY: 'Pipeline Visualization',
                'execution': {
                    'inputs': {'pipeline': {'value': b.selected_pipeline,},},
                    'output': {
                        ELEMENT_KEY: GraphOutput,
                        NAME_KEY: 'Flow',
                        'use_container_width': True,
                    },
                },
            },
        },
    }

    funcs = [
        mk_step,
        modify_step,
        mk_pipeline,
        visualize_pipeline,
        modify_pipeline,
        view_state,
        dummy,
    ]
    app = mk_app(funcs, config=config)

    return app


mall = dict(
    # Factory Input Stores
    sound_output=dict(),
    step_factories=dict(
        # ML
        chunker=FuncFactory(simple_chunker),
        featurizer=FuncFactory(simple_featurizer),
    ),
    # Output Store
    data=dict(),
    steps=dict(),
    pipelines=dict(),
    exec_outputs=dict(),
    learned_models=dict(),
    models_scores=dict(),
)

# crudifier = partial(prepare_for_crude_dispatch, mall=mall)

# step_factories = dict(
#     # ML
#     chunker=FuncFactory(simple_chunker),
#     featurizer=FuncFactory(simple_featurizer),
# )

# mall['step_factories'] = step_factories


if __name__ == '__main__':

    app = mk_pipeline_maker_app_with_mall(
        mall, step_factories='step_factories', steps='steps', pipelines='pipelines'
    )

    app()
