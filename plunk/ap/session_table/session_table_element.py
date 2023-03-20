from dataclasses import dataclass, field
from typing import Callable, TypedDict, List

import streamlit as st
from front import BoundData
from front.elements import InputBase, OutputBase
from stogui import oto_table


class SessionQuery(TypedDict):
    filter: dict
    sort: dict
    pagination: dict


@dataclass
class OtoTableQuery(InputBase):
    def render(self):
        query = oto_table(sessions=[])
        st.write(f'OtoTableQuery: {query}')
        return query


@dataclass
class OtoTable(OutputBase):
    output: List[dict] = field(default_factory=list)

    @property
    def session(self):
        return self.output

    def render(self):
        return oto_table(sessions=self.output)


@dataclass
class OtoTableAll(InputBase):
    list_session: Callable = None
    query: BoundData = None

    def render(self):
        query = self.query() or {}  # is BoundData
        st.write(f'OtoTableAll: {query=}')

        sessions = self.list_session(query)
        next_query = oto_table(sessions=sessions, query=query)
        nxt_str = f'OtoTableAll: {next_query=}'
        st.write(nxt_str)
        print(nxt_str)
        if next_query is not None and query != next_query:
            self.query.set(next_query)
        return next_query


@dataclass
class Pass(OutputBase):
    def render(self):
        pass
