"""
User story 1: 
    - User inputs rows of triples (outputs, function, inputs)
    - User creates a DAG from the triples
    - User can view the DAG
"""


from typing import List, Dict, Union, TypedDict, Callable, Mapping, Iterable

from front import APP_KEY, RENDERING_KEY, NAME_KEY, ELEMENT_KEY
from front.elements import InputBase, OutputBase
from plunk.ap.wf_visualize_player.wf_visualize_player_element import WfVisualizePlayer
from streamlitfront import mk_app
from streamlitfront.elements import SelectBox, SelectBoxBase
from lined import LineParametrized
from streamlitfront.examples.util import Graph

from i2 import FuncFactory, Sig
from streamlitfront.elements import (
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
    ArrayWithIntervalsPlotter,
    GraphOutput,
    ArrayPlotter,
)
from meshed import FuncNode, DAG


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


def retrieve_data(sref):
    import soundfile as sf
    import os

    home_directory = os.path.expanduser('~')
    path = os.path.join(home_directory + '/Dropbox/OtoSense/VacuumEdgeImpulse/', sref)

    arr = sf.read(path, dtype='int16')[0]
    return path, arr


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
    # *,
    step_factories: str = 'step_factories',
    steps: str = 'steps',
    funcnodes_store: str = 'funcnodes_store',
    dags_store: str = 'dags_store',
):

    if not b.mall():
        b.mall = mall
    mall = b.mall()

    crudifier = partial(Crudifier, mall=mall)

    def debug_view():
        st.write(mall)

    @crudifier(
        param_to_mall_map=dict(func_factory=step_factories),
        output_store=funcnodes_store,
    )
    def mk_funcnode(func_factory: Callable, out: str, kwargs: dict):
        kwargs = clean_dict(kwargs)  # TODO improve that logic
        step = partial(func_factory, **kwargs)()
        result = FuncNode(func=step, out=out)
        return result

    @crudifier(
        output_store=dags_store,
    )
    def mk_dag(steps: Iterable[Callable]):
        return DAG(*steps)

    def get_step_name(step):
        return [k for k, v in mall[funcnodes_store].items() if v == step][0]

    def get_selected_func_factory_sig():
        selected_step_factory = mall['step_factories'].get(
            b.selected_func_factory.get()
        )
        if selected_step_factory:
            return Sig(selected_step_factory)

    config = {
        APP_KEY: {'title': 'Data Preparation'},
        RENDERING_KEY: {
            Callable: {
                'execution': {
                    'inputs': {
                        'save_name': {
                            NAME_KEY: 'Save as',
                        },
                    },
                },
            },
            DAG: {
                'graph': {
                    ELEMENT_KEY: Graph,
                    NAME_KEY: 'Flow',
                },
            },
            'mk_funcnode': {
                NAME_KEY: 'Funcnode Maker',
                'execution': {
                    'inputs': {
                        'func_factory': {
                            'value': b.selected_func_factory,
                        },
                        'kwargs': {'func_sig': get_selected_func_factory_sig},
                        'save_name': {
                            NAME_KEY: 'Save as',
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The step has been created successfully.',
                    },
                },
            },
            'mk_dag': {
                NAME_KEY: 'Dag Maker',
                'execution': {
                    'inputs': {
                        steps: {
                            ELEMENT_KEY: PipelineMaker,
                            'items': mall[funcnodes_store].values(),
                            'serializer': get_step_name,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The pipeline has been created successfully.',
                    },
                },
            },
        },
    }

    funcs = [
        mk_funcnode,
        mk_dag,
        debug_view,
    ]
    app = mk_app(funcs, config=config)

    return app


# Mall
mall = dict(
    # Factory Input Stores
    step_factories=dict(
        # ML
        chunker=FuncFactory(simple_chunker),
        featurizer=FuncFactory(simple_featurizer),
    ),
    # sessions_store={'my_saved_session': MOCK_SESSIONS},
    # Output Store
    funcnodes_store=dict(),
    steps=dict(),
    # mapped_annots=dict(),
    # annotation_dict_store=dict(),
    dags_store=dict(),
    # exec_outputs=dict(),
    # learned_models=dict(),
    # models_scores=dict(),
)


if __name__ == '__main__':

    app = mk_pipeline_maker_app_with_mall(
        mall,
        funcnodes_store='funcnodes_store',
        step_factories='step_factories',
        steps='steps',
        dags_store='dags_store',
    )

    app()
