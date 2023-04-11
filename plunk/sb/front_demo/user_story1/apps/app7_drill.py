from typing import List, Dict, Union, TypedDict, Callable, Mapping, Iterable

from front import APP_KEY, RENDERING_KEY, NAME_KEY, ELEMENT_KEY
from front.elements import InputBase, OutputBase
from plunk.ap.wf_visualize_player.wf_visualize_player_element import WfVisualizePlayer
from streamlitfront import mk_app
from streamlitfront.elements import SelectBox
from lined import LineParametrized

from i2 import FuncFactory, Sig
from streamlitfront.elements import (
    SelectBox,
    SuccessNotification,
    PipelineMaker,
)
from functools import partial
import pandas as pd
from dataclasses import dataclass
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import streamlit as st
from streamlitfront import binder as b
from front.crude import Crudifier
from olab.types import (
    Step,
    Pipeline,
    WaveForm,
)
from olab.util import clean_dict
from olab.base import (
    scores_to_intervals,
    simple_featurizer,
    learn_outlier_model,
    apply_fitted_model,
    simple_chunker,
)
from plunk.sb.front_demo.user_story1.components.components import (
    AudioArrayDisplay,
    ArrayWithIntervalsPlotter,
    GraphOutput,
    ArrayPlotter,
)


@dataclass
class Grid(InputBase):
    sessions: pd.DataFrame = None
    # on_value_change: callable = lambda x: print(x["selected_rows"])

    def render(self):
        gb = GridOptionsBuilder.from_dataframe(self.sessions)
        gb.configure_selection(selection_mode='multiple', use_checkbox=True)
        gridOptions = gb.build()

        data = AgGrid(
            self.sessions,
            gridOptions=gridOptions,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            enable_enterprise_modules=True,
        )

        # print(dir(self))
        return data['selected_rows']


@dataclass
class MockGrid(InputBase):
    sessions: pd.DataFrame = None

    def render(self):
        st.write(self.sessions)


def retrieve_data(sref):
    import soundfile as sf
    import os

    home_directory = os.path.expanduser('~')
    path = os.path.join(home_directory + '/Dropbox/OtoSense/VacuumEdgeImpulse/', sref)

    arr = sf.read(path, dtype='int16')[0]
    return path, arr


@dataclass
class WavSelectionViewer(OutputBase):
    def render(self):
        sref = self.output[0]['sref']
        path, arr = retrieve_data(sref)
        tab1, tab2 = st.tabs(['Audio Player', 'Waveform'])
        with tab1:
            st.audio(path)
        with tab2:
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(15, 5))
            ax.plot(arr)
            ax.legend()
            st.pyplot(fig)


DFLT_FPATH = '../data/mock_data.csv'


def mk_dataset() -> pd.DataFrame:
    df = pd.read_csv(DFLT_FPATH)
    return df


MOCK_SESSIONS = mk_dataset()


def identity(x=None):
    st.write(b.selected_row())
    return x


def select_sessions(sessions):
    return sessions


def pre_configure_dpp(model_type, chk_size, featurizer):
    return model_type


def get_annotations_from_sessions(session_df):
    return set.union(*session_df['annotations'].apply(set))


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

    steps_store = steps_store or steps
    data_store = data_store or data
    pipelines_store = pipelines_store or pipelines

    crudifier = partial(Crudifier, mall=mall)

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

    @crudifier(output_store=pipelines_store,)
    def mk_pipeline(steps: Iterable[Callable]):
        named_funcs = [(get_step_name(step), step) for step in steps]
        pipeline = Pipeline(steps=steps, pipe=LineParametrized(*named_funcs))
        return pipeline

    @crudifier(
        param_to_mall_map=dict(pipeline=pipelines_store), output_store=pipelines_store,
    )
    def modify_pipeline(pipeline, steps):
        named_funcs = [(get_step_name(step), step) for step in steps]
        pipe = LineParametrized(*named_funcs)
        return Pipeline(steps=named_funcs, pipe=pipe)

    learn_outlier_model_crudified = crudifier(
        param_to_mall_map=dict(
            tagged_data='sound_output', preprocess_pipeline='pipelines'
        ),
        output_store='learned_models',
    )(learn_outlier_model)

    apply_fitted_model_crudified = crudifier(
        param_to_mall_map=dict(
            tagged_data='sound_output',
            preprocess_pipeline='pipelines',
            fitted_model='learned_models',
        ),
        output_store='models_scores',
    )(apply_fitted_model)

    @crudifier(param_to_mall_map=dict(pipeline=pipelines_store),)
    def visualize_pipeline(pipeline: Pipeline):

        return pipeline

    @crudifier(param_to_mall_map=dict(scores='models_scores'),)
    def visualize_scores(scores, threshold=80, num_segs=3):

        intervals = scores_to_intervals(scores, threshold, num_segs)

        return scores, intervals

    @crudifier(output_store='sound_output')
    def upload_sound(train_audio: List[WaveForm], tag: str):
        return train_audio, tag

    def get_step_name(step):
        return [k for k, v in mall[steps].items() if v.step == step][0]

    def get_selected_step_factory_sig():
        selected_step_factory = mall['step_factories'].get(
            b.selected_step_factory.get()
        )
        if selected_step_factory:
            return Sig(selected_step_factory)

    def get_step_to_modify_factory_sig():
        selected_step_factory = (
            mall['steps'].get(b.selected_step_to_modify.get()).step_factory
        )
        if selected_step_factory:
            return Sig(selected_step_factory)

    def on_select_pipeline(pipeline):
        b.steps_of_selected_pipeline.set(mall['pipelines'][pipeline].steps)

    config = {
        APP_KEY: {'title': 'Data Preparation'},
        RENDERING_KEY: {
            'select_sessions': {
                NAME_KEY: 'Original dataset',
                'description': {
                    'content': '''
                            Review carefully the dataset that will be used to train and test the model, then press NEXT.
                            If the dataset does not look right, close the DPP Builder, return to the Session List, 
                            and preselect the relevant sessions before reopening the DPP Builder.
                            '''
                },
                'execution': {
                    'inputs': {
                        'sessions': {
                            ELEMENT_KEY: Grid,
                            'sessions': MOCK_SESSIONS,
                            # "value": b.selected_row,
                        },
                    },
                    'output': {ELEMENT_KEY: WavSelectionViewer},
                    # "auto_submit": True,
                },
            },
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
                            ELEMENT_KEY: SelectBox,
                            'value': b.selected_pipeline,
                            'on_value_change': on_select_pipeline,
                        },
                        steps: {
                            ELEMENT_KEY: PipelineMaker,
                            'items': [v.step for v in mall[steps].values()],
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
            'visualize_scores': {
                NAME_KEY: 'Scores Visualization',
                'execution': {'output': {ELEMENT_KEY: ArrayWithIntervalsPlotter,},},
            },
            'simple_model': {
                NAME_KEY: 'Learn model',
                'execution': {'output': {ELEMENT_KEY: ArrayPlotter,},},
            },
            'apply_fitted_model': {
                NAME_KEY: 'Apply model',
                'execution': {'output': {ELEMENT_KEY: ArrayPlotter,},},
            },
        },
    }

    funcs = [
        select_sessions,
        # upload_sound,
        mk_step,
        modify_step,
        mk_pipeline,
        modify_pipeline,
        learn_outlier_model_crudified,
        apply_fitted_model_crudified,
        visualize_pipeline,
        visualize_scores,
    ]
    app = mk_app(funcs, config=config)

    return app


# Mall
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


if __name__ == '__main__':

    app = mk_pipeline_maker_app_with_mall(
        mall, step_factories='step_factories', steps='steps', pipelines='pipelines'
    )

    app()
