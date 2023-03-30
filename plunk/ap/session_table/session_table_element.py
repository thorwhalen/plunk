from dataclasses import dataclass
from typing import List

from front.elements import InputBase
from stogui import oto_table


@dataclass
class OtoTable(InputBase):
    sessions: List[dict] = None
    is_multiselect: bool = None

    def render(self):
        component_value = oto_table(
            sessions=self.sessions, is_multiselect=self.is_multiselect
        )
        return component_value
