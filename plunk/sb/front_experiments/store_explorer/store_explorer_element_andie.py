from dataclasses import dataclass
from functools import cached_property
from typing import (
    Any,
    Mapping,
    Union,
    Hashable,
    List,
    TypeVar,
    Protocol,
    Tuple,
    Callable,
)
import operator

import streamlit as st
from boltons.typeutils import make_sentinel
from front.elements import OutputBase, InputBase
from functools import reduce

from plunk.ap.snippets import get_mall


class _RenderInput(Protocol):
    def __call__(_self, self: "StoreExplorerInput", depth: "Depth", obj: Any) -> None:
        ...


class _RenderOutput(Protocol):
    def __call__(_self, self: "StoreExplorerOutput", obj: Any) -> None:
        ...


RenderInput = TypeVar("RenderInput", bound=_RenderInput)
RenderOutput = TypeVar("RenderOutput", bound=_RenderOutput)
Depth = TypeVar("Depth", bound=int)
DepthKey = TypeVar("DepthKey", bound=Union[Hashable, int])
NOT_SELECTED = make_sentinel("Not Selected", "Not Selected")
STORE_EXPLORER_STATE = "__STORE_EXPLORER_STATE__"
_mall = get_mall({STORE_EXPLORER_STATE: {"depth_keys": []}})


def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)


def del_by_path(root, items):
    """Delete a key-value in a nested object in root by item sequence."""
    del get_by_path(root, items[:-1])[items[-1]]


@dataclass
class StoreExplorerInput(InputBase):
    mall: Mapping = dict

    def __post_init__(self):
        super().__post_init__()
        print(f"0-{self.mall=}")
        if isinstance(self.mall, Callable):
            self.mall = self.mall()
        print(f"1-{self.mall=}")

    @cached_property
    def stores(self) -> Mapping:
        """Remove STORE_EXPLORER_STATE from selection"""
        return {k: v for k, v in self.mall.items() if k is not STORE_EXPLORER_STATE}

    @property
    def depth_keys(self) -> List[DepthKey]:
        return _mall[STORE_EXPLORER_STATE]["depth_keys"]

    @depth_keys.setter
    def depth_keys(self, value: List[DepthKey]):
        _mall[STORE_EXPLORER_STATE]["depth_keys"] = value

    @depth_keys.deleter
    def depth_keys(self):
        del _mall[STORE_EXPLORER_STATE]["depth_keys"]

    @staticmethod
    def st_key(depth) -> str:
        return f"depth {depth}"

    @staticmethod
    def get_item(obj: Mapping, key: Union[Hashable, int]) -> Any:
        if key is NOT_SELECTED:
            return NOT_SELECTED
        return obj[key]

    def selectbox(self, depth: Depth, options: List[DepthKey]):
        st.selectbox(
            key := self.st_key(depth),
            options=options,
            key=key,
            on_change=self._update_depth_keys,
            args=(depth,),
        )

    def _update_depth_keys(self, depth: Depth) -> None:
        """Update depth keys on change in streamlit component

        :param depth: number of steps into the store
        :return: None
        """
        self.depth_keys = self.depth_keys[:depth]
        if (dk := st.session_state.get(self.st_key(depth))) is not NOT_SELECTED:
            self.depth_keys.append(dk)

    def render(self):
        obj = self.stores
        depth = -1
        for depth, k in enumerate(self.depth_keys):
            action: RenderInput = getattr(self, type(obj).__name__, self.default)
            action(depth, obj)
            obj = self.get_item(obj, k)
        depth += 1
        action: RenderInput = getattr(self, type(obj).__name__, self.default)
        action(depth, obj)
        before_deletion = self.depth_keys

        def rm():
            stuff = del_by_path(self.mall, self.depth_keys)
            self.depth_keys = self.depth_keys[:-1]
            st.write(f"{stuff=}")

        st.button("delete key", on_click=rm)
        return before_deletion

    def dict(self, depth: Depth, obj: dict):
        """RenderInput for dict"""
        if len(obj) != 0:
            self.selectbox(depth, [NOT_SELECTED, *obj])

    def list(self, depth: Depth, obj: list):
        """RenderInput for list"""
        if len(obj) != 0:
            self.selectbox(depth, options=[NOT_SELECTED, *(i for i in range(len(obj)))])

    def default(self, depth: Depth, obj: Any):
        """Default RenderInput"""


@dataclass
class StoreExplorerOutput(OutputBase):
    output: Tuple[List[DepthKey], Any] = ((), {})
    write_depth_keys: Union[bool, Callable[[List[DepthKey]], None]] = True

    def __post_init__(self):
        if self.write_depth_keys is True:
            self.write_depth_keys = self.default_write_depth_keys
        elif self.write_depth_keys is False:
            self.write_depth_keys = lambda depth_keys: None

    @property
    def depth_keys(self) -> List[DepthKey]:
        return self.output[0]

    @property
    def node(self) -> Any:
        return self.output[1]

    def render(self):
        self.write_depth_keys(self.depth_keys)
        _render: RenderOutput = getattr(self, type(self.node).__name__, self.default)
        _render(self.node)
        st.button(
            label="remove key",
            on_click=lambda: st.write(f"been clicked {self.output=}"),
        )

    @staticmethod
    def default_write_depth_keys(depth_keys):
        st.write(f'#### Store[{"][".join(str(k) for k in depth_keys)}] Value')

    def dict(self, obj: dict):
        """Render for dict"""
        if STORE_EXPLORER_STATE in obj:
            obj = {k: v for k, v in obj.items() if k != STORE_EXPLORER_STATE}

        self.default(obj)

    def list(self, obj: list):
        """Render for list"""
        self.default(obj)

    def default(self, obj: Any):
        """Default RenderInput"""
        st.write(obj)
