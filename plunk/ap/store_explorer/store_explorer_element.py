from dataclasses import dataclass
from functools import reduce
from typing import Callable, Any, Mapping, Union, Hashable, List

import streamlit as st
from front.elements import OutputBase

from streamlitfront import binder as b


def get_mall(defaults: dict):
    if not b.mall():
        b.mall = defaults
    m = b.mall()
    if not all(k in m for k in defaults):
        m.update(defaults)
    return m


mall = get_mall({'__store_explorer_state': {'depth_keys': []}})


Depth = int
RenderAction = Callable[[Depth, Any], None]


@dataclass
class StoreExplorer(OutputBase):
    @property
    def depth_keys(self) -> List[Union[Hashable, int]]:
        return mall['__store_explorer_state']['depth_keys']

    @depth_keys.setter
    def depth_keys(self, value: List[Union[Hashable, int]]):
        mall['__store_explorer_state']['depth_keys'] = value

    def get_item(self, obj: Mapping, key: Union[Hashable, int]):
        return obj[key]

    def update_depth_keys(self, depth):
        self.depth_keys = [*self.depth_keys[:depth]]
        if depth > 0:
            self.depth_keys.append(st.session_state.get(f'depth_{depth - 1}'))

    def get_obj(self, store: Mapping):
        return reduce(self.get_item, self.depth_keys, store)

    def selectbox(self, depth: Depth, options: List[Union[Hashable, int]]):
        st.selectbox(
            key := f'depth_{depth}',
            options=options,
            key=key,
            on_change=self._render,
            args=[depth + 1],
        )

    def _render(self, depth: Depth):
        """Recursive render dives into the depths of a nested structure

        :param depth:
        :return:
        """
        if depth == 0:
            st.write(self.output)
        else:
            # Redraw previous selections
            self._render(depth - 1)

        self.update_depth_keys(depth)
        obj = self.get_obj(self.output)
        action_method: RenderAction = getattr(self, type(obj).__name__, self.default)
        action_method(depth, obj)

    def render(self):
        self._render(depth=0)

    def dict(self, depth: Depth, obj: Any):
        """RenderAction for dict"""
        return self.selectbox(depth, options=[None, *obj])

    def list(self, depth: Depth, obj: Any):
        """RenderAction for list"""
        self.selectbox(depth, options=[None, *(i for i in range(len(obj)))])

    def default(self, depth: Depth, obj: Any):
        """Default RenderAction"""
        st.write(f'##### Store[{"][".join(str(k) for k in self.depth_keys)}] Value')
        st.write(obj)
