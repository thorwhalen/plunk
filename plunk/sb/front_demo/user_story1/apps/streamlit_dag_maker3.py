import pandas as pd
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import graphviz

#@dataclass
# class Grid(InputBase):
#     sessions: pd.DataFrame = None
#     # on_value_change: callable = lambda x: print(x["selected_rows"])

#     def render(self):
#         gb = GridOptionsBuilder.from_dataframe(self.sessions)
#         gb.configure_selection(selection_mode='multiple', use_checkbox=True)
#         gridOptions = gb.build()

#         data = AgGrid(
#             self.sessions,
#             gridOptions=gridOptions,
#             update_mode=GridUpdateMode.SELECTION_CHANGED,
#             enable_enterprise_modules=True,
#         )

#         # print(dir(self))
#         return data['selected_rows']


st.title("Streamlit DAG Maker with Aggrid")

st.write("Funcs available: [foo, bar, confuser]")

df = pd.DataFrame(
    [['foo', 'bar'], ['foo', 'confuser']],
    columns=["Source", "Target"],
)

dropdownlst = ('foo', 'bar', 'confuser')

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column(“Your Col Name”, editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdownlst })

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
