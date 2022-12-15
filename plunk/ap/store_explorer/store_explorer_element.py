from dataclasses import dataclass
from functools import reduce, cached_property, wraps
from typing import Any, Mapping, Union, Hashable, List, TypeVar, Protocol

import streamlit as st
from boltons.typeutils import make_sentinel
from front.elements import OutputBase

from streamlitfront import binder as b


def get_mall(defaults: dict):
    if not b.mall():
        b.mall = defaults
    m = b.mall()
    if not all(k in m for k in defaults):
        m.update(defaults)
    return m


class _RenderAction(Protocol):
    def __call__(
        _self, self: 'StoreExplorer', depth: 'Depth', obj: Any, is_changed_depth: bool
    ) -> None:
        ...


RenderAction = TypeVar('RenderAction', bound=_RenderAction)
Depth = TypeVar('Depth', bound=int)
NOT_SELECTED = make_sentinel('Not Selected', 'Not Selected')
STORE_EXPLORER_STATE = '__STORE_EXPLORER_STATE__'
mall = get_mall({STORE_EXPLORER_STATE: {'depth_keys': []}})


def write_obj_after(method: RenderAction) -> RenderAction:
    @wraps(method)
    def _wrapper(self: 'StoreExplorer', depth: Depth, obj: Any, is_changed_depth: bool):
        method(self, depth, obj, is_changed_depth)
        if is_changed_depth:
            self.default(depth, obj, is_changed_depth)

    return _wrapper


@dataclass
class StoreExplorer(OutputBase):
    output: Mapping = None

    @cached_property
    def stores(self) -> Mapping:
        """Remove STORE_EXPLORER_STATE from selection"""
        return {k: v for k, v in self.output.items() if k is not STORE_EXPLORER_STATE}

    @property
    def depth_keys(self) -> List[Union[Hashable, int]]:
        return mall[STORE_EXPLORER_STATE]['depth_keys']

    @depth_keys.setter
    def depth_keys(self, value: List[Union[Hashable, int]]):
        mall[STORE_EXPLORER_STATE]['depth_keys'] = value

    @staticmethod
    def st_key(depth):
        return f'depth {depth}'

    @staticmethod
    def get_item(obj: Mapping, key: Union[Hashable, int]) -> Any:
        if key is NOT_SELECTED:
            return NOT_SELECTED
        return obj[key]

    def get_depth_obj(self) -> Any:
        """Get object by following selected depth keys"""
        return reduce(self.get_item, self.depth_keys, self.stores)

    def selectbox(self, depth: Depth, options: List[Union[Hashable, int]]):
        st.selectbox(
            key := self.st_key(depth),
            options=options,
            key=key,
            on_change=self._render,
            args=(depth + 1, True),
        )

    def _render(self, depth: Depth, is_changed_depth=False) -> None:
        """Recursive render dives into the depths of a nested structure

        :param depth: number of steps into the store
        :param is_changed_depth: is the depth changed by user action
        :return: None
        """
        self.depth_keys = self.depth_keys[:depth]
        if depth > 0:
            dk = st.session_state.get(self.st_key(depth - 1))
            self._render(depth - 1, is_changed_depth=dk is NOT_SELECTED)
            self.depth_keys.append(dk)

        if (obj := self.get_depth_obj()) is not NOT_SELECTED:
            action: RenderAction = getattr(self, type(obj).__name__, self.default)
            action(depth, obj, is_changed_depth)

    def render(self):
        self._render(depth=0, is_changed_depth=True)

    @write_obj_after
    def dict(self, depth: Depth, obj: dict, is_changed_depth: bool):
        """RenderAction for dict"""
        if len(obj) != 0:
            self.selectbox(depth, [NOT_SELECTED, *obj])

    @write_obj_after
    def list(self, depth: Depth, obj: list, is_changed_depth: bool):
        """RenderAction for list"""
        if len(obj) != 0:
            self.selectbox(depth, options=[NOT_SELECTED, *(i for i in range(len(obj)))])

    def default(self, depth: Depth, obj: Any, is_changed_depth: bool):
        """Default RenderAction"""
        st.write(f'##### Store[{"][".join(str(k) for k in self.depth_keys)}] Value')
        st.write(obj)
