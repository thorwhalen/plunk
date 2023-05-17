"""
User story 2: 
    - User inputs rows of triples (outputs, function, inputs)
    - User creates a DAG from the triples
    - User can view the DAG
    - User can edit the DAG by changing its functions
"""


from typing import Mapping
from typing import Callable, Iterable, Union, List
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from front.crude import Crudifier, prepare_for_crude_dispatch
from lined import LineParametrized
import pandas as pd
from streamlitfront import mk_app, binder as b
from streamlitfront.elements import (
    SelectBox,
    SuccessNotification,
    PipelineMaker,
)
from i2 import Sig
from front.crude import Crudifier, prepare_for_crude_dispatch
import graphviz
from streamlitfront.examples.util import Graph
from front.elements import FrontComponentBase
from front.types import Map
from streamlitfront.elements.js import mk_element_factory
from dataclasses import dataclass
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

import streamlit as st
from functools import partial
from meshed.makers import triples_to_fnodes
from meshed import DAG
from meshed.base import rebind_to_func


from dataclasses import dataclass
from front.elements import InputBase, ExecContainerBase, OutputBase


def _init_cache(key, init_value):
    if not b[key]():
        b[key].set(init_value)


def f(a, b: int, /):
    return a + b


def g(a_plus_b, d: float = 4):
    return a_plus_b * d


DFLT_FUNCS_DICT = {'f': f, 'g': g}


@dataclass
class EditableGrid(InputBase):
    rows: pd.DataFrame = None
    editable_column: str = None
    choices: List = None
    # on_value_change: callable = lambda x: print(x["selected_rows"])

    def render(self):
        gb = GridOptionsBuilder.from_dataframe(self.rows)
        # gb.configure_selection(selection_mode='multiple', use_checkbox=True)
        gb.configure_column(
            self.editable_column,
            editable=True,
            cellEditor='agSelectCellEditor',
            cellEditorParams={'values': self.choices},
        )
        gridOptions = gb.build()

        data = AgGrid(
            self.rows,
            gridOptions=gridOptions,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            enable_enterprise_modules=True,
        )

        # print(dir(self))
        return data['selected_rows']


@dataclass
class ExtendableTable(InputBase):
    df: pd.DataFrame = None

    def render(self):
        # self.df = pd.DataFrame(
        #     self.rows,
        #     columns=["Outputs", "Function", "Inputs"],
        # )
        edited_df = st.experimental_data_editor(
            self.df,
            use_container_width=True,
            num_rows="dynamic",
        )
        # return list(self.df.itertuples())
        triples = list(edited_df.itertuples())
        return [item[1:] for item in triples[1:]]  # cannot return to dataframe


def df_to_triples(df):
    for row in df.itertuples():
        yield row.Outputs, row.Function, row.Inputs


def triple_to_edges(triple_gen):
    for outputs, func, inputs in triple_gen:
        func = func.strip()
        for output in outputs.split(','):
            yield func, output.strip()

        for input in inputs.split(','):
            yield input.strip(), func


from dol import Pipe

row_to_edges = Pipe(df_to_triples, triple_to_edges)


def mk_graph(df, row_to_edges=row_to_edges):
    graph = graphviz.Digraph()
    for from_, to_ in row_to_edges(df):
        graph.edge(from_, to_)
    return graph


@dataclass
class RowsToGraph(OutputBase):
    def render(self):
        self.rows = self.output
        st.write(list(self.rows))


@dataclass
class DagViewer(OutputBase):
    def render(self):
        self.output.dot_digraph()
        # st.write(list(self.rows))


@dataclass
class GraphOutput(OutputBase):
    use_container_width: bool = False

    def render(self):
        # with st.expander(self.name, True): #cannot nest expanders
        dag = self.output
        st.graphviz_chart(
            figure_or_dot=dag.dot_digraph(),
            use_container_width=self.use_container_width,
        )


@dataclass
class ListSelector(InputBase):
    keys: Iterable = None

    def render(self):
        # with st.expander(self.name, True): #cannot nest expanders
        for key in self.keys:
            print(key)


@dataclass
class ListSelect(InputBase):
    options: Iterable = None
    keys: Iterable = None

    def __post_init__(self):
        super().__post_init__()

    def render(self):
        result = dict()
        if self.keys:
            for key in self.keys:
                # value = st_multiselect(options=self.options, key=key)
                value = st.selectbox(
                    options=self.options, label=key
                )  # TODO: make it multiselect
                result[key] = DFLT_FUNCS_DICT[value]
        return result


@dataclass
class Graph(FrontComponentBase):
    use_container_width: bool = False

    def render(self):
        with st.expander(self.name, True):
            dag: DAG = self.obj
            st.graphviz_chart(
                figure_or_dot=dag.dot_digraph(),
                use_container_width=self.use_container_width,
            )


def compare_signatures_by_inserting_defaults(func1, func2):
    from i2.signatures import Sig, _fill_defaults_and_annotations

    sig1 = Sig(func1)
    sig2 = Sig(func2)
    sig_1_from_2 = _fill_defaults_and_annotations(sig1, sig2)
    sig_2_from_1 = _fill_defaults_and_annotations(sig2, sig1)

    return sig_1_from_2 == sig_2_from_1
    # return True


def compare_signatures_by_lengths(func1, func2):
    from i2.signatures import Sig

    sig1 = Sig(func1)
    sig2 = Sig(func2)

    return len(sig1) == len(sig2)


from meshed.dag import ch_func_node_func

ch_func_node_func2 = partial(
    ch_func_node_func, func_comparator=compare_signatures_by_lengths
)


def mk_pipeline_maker_app_with_mall(
    mall: Mapping,
    *,
    # steps: str = 'steps',
    # edges_store: str = 'edges_store',
    dags_store: str = 'dags_store',
):
    if not b.mall():
        b.mall = mall
    mall = b.mall()

    crudifier = partial(Crudifier, mall=mall)

    @crudifier(
        output_store=dags_store,
    )
    def add_edge(edge_table) -> DAG:
        dag = DAG(triples_to_fnodes(edge_table))
        return dag

    @crudifier(
        param_to_mall_map=dict(dag=dags_store),
        output_store=dags_store,
    )
    def chooser(dag, inputs):
        new_dag = dag.ch_funcs(rebind_to_func, **inputs)
        st.write([node.func for node in new_dag.func_nodes])
        return new_dag

    def debug():
        st.write(mall)

    _init_cache('selected_multichoice', [])

    def on_select_dag(dag_name):
        dag = mall['dags_store'][dag_name]
        st.write(dag)
        funcs_names = [node.name for node in dag.func_nodes]
        st.write(funcs)

        b.names_for_dag.set(funcs_names)

    config = {
        APP_KEY: {'title': 'Dag Maker'},
        RENDERING_KEY: {
            DAG: {
                'graph': {
                    ELEMENT_KEY: Graph,
                    NAME_KEY: 'Flow',
                },
            },
            'add_edge': {
                NAME_KEY: 'Dag Maker',
                'execution': {
                    'inputs': {
                        'edge_table': {
                            ELEMENT_KEY: ExtendableTable,
                            'df': pd.DataFrame(
                                [
                                    ['output', 'func', 'inputs'],
                                ],
                                columns=["Outputs", "Function", "Inputs"],
                            ),
                        },
                    },
                    'output': {
                        ELEMENT_KEY: GraphOutput,
                    },
                },
            },
            'chooser': {
                NAME_KEY: 'chooser',
                'execution': {
                    'inputs': {
                        'dag': {
                            ELEMENT_KEY: SelectBox,
                            'value': b.selected_dag,
                            'on_value_change': on_select_dag,
                        },
                        'inputs': {
                            ELEMENT_KEY: ListSelect,
                            'options': list(DFLT_FUNCS_DICT.keys()),
                            'keys': b.names_for_dag(),
                        },
                    },
                    'output': {
                        ELEMENT_KEY: SuccessNotification,
                        'message': 'The step has been created successfully.',
                    },
                },
            },
        },
    }

    funcs = [add_edge, chooser, debug]
    app = mk_app(funcs, config=config)

    return app


if __name__ == '__main__':

    mall = dict(
        # Output Store
        dags_store=dict(),
    )

    crudifier = partial(prepare_for_crude_dispatch, mall=mall)

    app = mk_pipeline_maker_app_with_mall(mall)

    app()
