"""
An app that loads either a wav file from local folder or records a sound
and visualizes the resulting numpy array 
"""
from typing import Mapping
from typing import Callable, Iterable
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
from front.crude import Crudifier, prepare_for_crude_dispatch
import graphviz
from streamlitfront.examples.util import Graph
from front.elements import FrontComponentBase


import streamlit as st
from functools import partial
from meshed.makers import triples_to_fnodes
from meshed import DAG

from dataclasses import dataclass
from front.elements import InputBase, ExecContainerBase, OutputBase


def _init_cache(key, init_value):
    if not b[key]():
        b[key].set(init_value)


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
class Graph(FrontComponentBase):
    use_container_width: bool = False

    def render(self):
        with st.expander(self.name, True):
            dag: DAG = self.obj
            st.graphviz_chart(
                figure_or_dot=dag.dot_digraph(),
                use_container_width=self.use_container_width,
            )


def mk_pipeline_maker_app_with_mall(
    mall: Mapping,
    *,
    steps: str = 'steps',
    edges_store: str = 'edges_store',
    dags_store: str = 'dags_store',
):
    if not b.mall():
        b.mall = mall
    mall = b.mall()

    crudifier = partial(Crudifier, mall=mall)

    # @crudifier(param_to_mall_map=dict(edge=steps), output_store=edges_store)
    # def add_edge(edge):
    #     return edge

    # b.selected_multichoice = []

    # def on_select_choice(item):

    #     b.selected_multichoice().append(item)
    @crudifier(
        output_store=dags_store,
    )
    def add_edge(edge_table) -> DAG:
        dag = DAG(triples_to_fnodes(edge_table))
        return dag

    def debug():
        st.write(mall)

    _init_cache('selected_multichoice', [])

    config = {
        APP_KEY: {'title': 'Dag Maker'},
        RENDERING_KEY: {
            DAG: {
                'graph': {
                    ELEMENT_KEY: Graph,
                    NAME_KEY: 'Flow',
                },
                #'execution': {
                #    'inputs': delegate_input(nodes_list),
                # "inputs":{'wf_filepath'}
                # },
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
                            )
                            # 'choices': list(mall[steps].values()),
                            # 'callback': on_select_choice,
                        },
                    },
                    'output': {
                        # ELEMENT_KEY: RowsToGraph,
                        ELEMENT_KEY: GraphOutput,
                        #'message': f'Edges created',
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
        # steps={'a': 'stepa', 'b': 'stepb'},
        # edges_store=dict(),
        dags_store=dict(),
    )

    crudifier = partial(prepare_for_crude_dispatch, mall=mall)

    app = mk_pipeline_maker_app_with_mall(mall)

    app()
