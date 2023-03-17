from dataclasses import dataclass
from typing import Callable

from front.elements import OutputBase
from stogui import session_table


@dataclass
class SessionTable(OutputBase):
    output: Callable = None

    def __post_init__(self):
        super().__post_init__()

    @property
    def list_session(self) -> Callable:
        return self.output

    def render(self):
        return session_table(list_session=self.list_session)
