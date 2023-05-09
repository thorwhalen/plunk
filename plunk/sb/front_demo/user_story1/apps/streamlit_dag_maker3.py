import pandas as pd
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, JsCode
import graphviz

# @dataclass
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

# df = pd.DataFrame(
#     [['foo', 'bar'], ['foo', 'confuser']],
#     columns=["Source", "Target"],
# )

# dropdownlst = ('foo', 'bar', 'confuser')

# gb = GridOptionsBuilder.from_dataframe(df)
# gb.configure_column(
#     'Source',
#     editable=True,
#     cellEditor='agSelectCellEditor',
#     cellEditorParams={'values': dropdownlst},
# )
# gridOptions = gb.build()

# data = AgGrid(
#     df,
#     gridOptions=gridOptions,
#     update_mode=GridUpdateMode.SELECTION_CHANGED,
#     enable_enterprise_modules=True,
# )

# st.write(data['selected_rows'])
def get_data():
    return pd.DataFrame(
        [['foo', 'bar'], ['foo', 'confuser']],
        columns=["Source", "Target"],
    )


def generate_agrid(df):
    gb = GridOptionsBuilder.from_dataframe(df)

    addRow = JsCode(
        """
function addRow(params) {
  let result = [
    {
      name: Add Row,
      action: () => {
        params.api.applyTransaction({add: [{}]});
        
      },
      //cssClasses: ['redFont', 'bold']
    },
    //'separator',
    //'copy',
  ];
  return result
}
"""
    )
    # gridApi.applyTransaction({add: [{}]})
    grid_op = {
        "addRow": addRow,
    }
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb.configure_grid_options(**grid_op)
    gridoptions = gb.build()

    grid_response = AgGrid(
        df,
        height=200,
        gridOptions=gridoptions,
        update_mode=GridUpdateMode.MANUAL,
        allow_unsafe_jscode=True,
    )
    selected = grid_response['selected_rows']

    # Show the selected row.
    if selected:
        st.write('selected')
        st.dataframe(selected)

    return grid_response


def add_row(grid_table):
    st.write('add row')
    df = pd.DataFrame(grid_table['data'])

    new_row = [['', 100]]
    df_empty = pd.DataFrame(new_row, columns=df.columns)
    df = pd.concat([df, df_empty], axis=0, ignore_index=True)
    st.write(df)
    st.session_state['df'] = df
    # Save new df to sample.csv.
    # df.to_csv('sample.csv', index=False)


if __name__ == '__main__':
    st.session_state['df'] = pd.DataFrame(get_data())

    # df = get_data()
    grid_response = generate_agrid(st.session_state['df'])

    st.button("Add row", on_click=add_row, args=[grid_response])

# st.write("Graph so far:")


# def mk_graph(df):
#     graph = graphviz.Digraph()
#     for row in df.itertuples():
#         graph.edge(row.Source, row.Target)
#     return graph


# st.graphviz_chart(mk_graph(df))
