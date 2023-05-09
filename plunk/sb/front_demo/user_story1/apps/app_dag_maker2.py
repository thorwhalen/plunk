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
import streamlit as st
from functools import partial

from dataclasses import dataclass
from front.elements import InputBase, ExecContainerBase, OutputBase


def _init_cache(key, init_value):
    if not b[key]():
        b[key].set(init_value)


@dataclass
class ExtendableTable(InputBase):
    rows = []

    def render(self):
        self.df = pd.DataFrame(
            self.rows,
            columns=["Outputs", "Function", "Inputs"],
        )
        edited_df = st.experimental_data_editor(
            self.df,
            use_container_width=True,
            num_rows="dynamic",
        )
        return edited_df.itertuples()  # cannot return to dataframe


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
        self.df = pd.DataFrame(
            self.rows,
            columns=["Outputs", "Function", "Inputs"],
        )
        graph = mk_graph(self.df)
        st.graphviz_chart(graph)


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

    # @crudifier(param_to_mall_map=dict(edge=steps), output_store=edges_store)
    # def add_edge(edge):
    #     return edge

    # b.selected_multichoice = []

    # def on_select_choice(item):

    #     b.selected_multichoice().append(item)

    def add_edge(edge_table=['this', 'func', 'that']):
        return edge_table

    def debug():
        st.write(mall)

    _init_cache('selected_multichoice', [])

    config = {
        APP_KEY: {'title': 'Dag Maker'},
        RENDERING_KEY: {
            'add_edge': {
                NAME_KEY: 'Dag Maker',
                'execution': {
                    'inputs': {
                        'edge_table': {
                            ELEMENT_KEY: ExtendableTable,
                            # 'value': pd.DataFrame(
                            #     [
                            #         ['this', 'func', 'that'],
                            #     ],
                            #     columns=["Outputs", "Function", "Inputs"],
                            # )
                            # 'choices': list(mall[steps].values()),
                            # 'callback': on_select_choice,
                        },
                    },
                    'output': {
                        ELEMENT_KEY: RowsToGraph,
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
        steps={'a': 'stepa', 'b': 'stepb'},
        edges_store=dict(),
    )

    crudifier = partial(prepare_for_crude_dispatch, mall=mall)

    app = mk_pipeline_maker_app_with_mall(mall, steps='steps')

    app()
