import pandas as pd
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, JsCode
import graphviz
import streamlit.components.v1 as components


def mermaid(code: str) -> None:
    components.html(
        f"""
        <pre class="mermaid">
            {code}
        </pre>

        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        """
    )


st.title("Streamlit DAG Maker with Aggrid")

st.write("Funcs available: [foo, bar, confuser]")

code = st.text_input("enter graph")
st.write(code)


def split_lines(code):
    return code.split(',')


"""
    graph LR
        A --> B --> C
    """
mermaid(
    f'''
graph LR 
{code}
'''
)

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
