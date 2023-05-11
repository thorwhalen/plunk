from typing import List, Dict, Union, TypedDict, Callable, Mapping, Iterable

from dataclasses import dataclass
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode


@dataclass
class Grid(InputBase):
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


# And then configure the column like below:
# gb.configure_column(“Your Col Name”, editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdownlst })
