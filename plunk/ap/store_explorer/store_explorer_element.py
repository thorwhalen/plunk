from dataclasses import dataclass
from functools import reduce, cached_property, wraps
from typing import Callable, Any, Mapping, Union, Hashable, List, TypeVar, Protocol

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


__store_explorer_state__ = '__store_explorer_state__'
mall = get_mall({__store_explorer_state__: {'depth_keys': []}})
NOT_SELECTED = make_sentinel(name='Not Selected', var_name='Not Selected')


Depth = TypeVar('Depth', bound=int)


class _RenderAction(Protocol):
    def __call__(
        _self, self: 'StoreExplorer', depth: Depth, obj: Any, is_changed_depth: bool
    ) -> None:
        ...


RenderAction = TypeVar('RenderAction', bound=_RenderAction)


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
    def stores(self):
        """Remove __store_explorer_state__ from selection"""
        return {
            k: v for k, v in self.output.items() if k is not __store_explorer_state__
        }

    @property
    def depth_keys(self) -> List[Union[Hashable, int]]:
        return mall[__store_explorer_state__]['depth_keys']

    @depth_keys.setter
    def depth_keys(self, value: List[Union[Hashable, int]]):
        mall[__store_explorer_state__]['depth_keys'] = value

    def get_item(self, obj: Mapping, key: Union[Hashable, int]):
        return obj[key]

    def get_obj(self, store: Mapping):
        return reduce(self.get_item, self.depth_keys, store)

    def selectbox(self, depth: Depth, options: List[Union[Hashable, int]]):
        st.selectbox(
            key := f'depth_{depth}',
            options=options,
            key=key,
            on_change=self._render,
            args=(depth + 1, True),
        )

    def _render(self, depth: Depth, is_changed_depth=False):
        """Recursive render dives into the depths of a nested structure

        :param depth: number of steps into the store
        :param is_changed_depth: is the depth changed by user action
        :return:
        """
        self.depth_keys = self.depth_keys[:depth]
        if depth > 0:
            self._render(depth - 1)
            self.depth_keys.append(st.session_state.get(f'depth_{depth - 1}'))

        obj = self.get_obj(self.stores)
        action_method: RenderAction = getattr(self, type(obj).__name__, self.default)
        action_method(depth, obj, is_changed_depth)

    def render(self):
        self._render(depth=0, is_changed_depth=True)

    @write_obj_after
    def dict(self, depth: Depth, obj: dict, is_changed_depth: bool):
        """RenderAction for dict"""
        self.selectbox(depth, options=[NOT_SELECTED, *obj])

    @write_obj_after
    def list(self, depth: Depth, obj: list, is_changed_depth: bool):
        """RenderAction for list"""
        self.selectbox(depth, options=[NOT_SELECTED, *(i for i in range(len(obj)))])

    def default(self, depth: Depth, obj: Any, is_changed_depth: bool):
        """Default RenderAction"""
        st.write(f'##### Store[{"][".join(str(k) for k in self.depth_keys)}] Value')
        st.write(obj)
