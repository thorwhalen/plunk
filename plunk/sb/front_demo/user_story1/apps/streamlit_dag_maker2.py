import pandas as pd
import streamlit as st
import graphviz

st.title("Streamlit DAG Maker")

st.write("Funcs available: [foo, bar, confuser]")

df = pd.DataFrame(
    [['foo', 'bar'], ['foo', 'confuser']],
    columns=["Source", "Target"],
)

edited_df = st.experimental_data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
)

st.write("Graph so far:")


def mk_graph(df):
    graph = graphviz.Digraph()
    for row in df.itertuples():
        graph.edge(row.Source, row.Target)
    return graph


st.graphviz_chart(mk_graph(edited_df))
