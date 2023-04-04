from st_aggrid import AgGrid
import pandas as pd
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import streamlit as st

# get some data
df = pd.read_csv(
    'https://raw.githubusercontent.com/fivethirtyeight/data/master/airline-safety/airline-safety.csv'
)
# configure the grid to have selectable rows
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection(selection_mode='multiple', use_checkbox=True)
gridOptions = gb.build()


data = AgGrid(
    df,
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    enable_enterprise_modules=True,
)

# write the selected rows
st.write(data['selected_rows'])
