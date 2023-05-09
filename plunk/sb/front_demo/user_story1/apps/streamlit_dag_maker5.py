import pandas as pd
import streamlit as st
import graphviz


# TODO: How do we make this in front (beyond the "put it in render")?

st.title("Streamlit DAG Maker")

st.write("Funcs available: [foo, bar, confuser]")

df = pd.DataFrame(
    [['this', 'func', 'that'], ['The, quick', 'brown', 'fox, jumps']],
    columns=["Outputs", "Function", "Inputs"],
)

edited_df = st.experimental_data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
)

st.write("Graph so far:")


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


st.graphviz_chart(mk_graph(edited_df))
