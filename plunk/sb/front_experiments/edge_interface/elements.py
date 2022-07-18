import streamlit as st
from meshed import DAG
from front.types import FrontElementName
from front.elements import FrontComponentBase
from typing import List

WaveForm = List[int]


class SimpleList(FrontComponentBase):
    def __init__(
        self,
        arr: WaveForm,
        name: FrontElementName = None,
        use_container_width: bool = False,
    ):
        super().__init__(arr=arr, name=name)
        self.use_container_width = use_container_width

    def render(self):
        with st.expander(self.name, True):
            arr: WaveForm = self.arr
            st.write(arr.len)


class SimpleText(FrontComponentBase):
    def __init__(
        self,
        word: str,
        name: FrontElementName = None,
        use_container_width: bool = False,
    ):
        super().__init__(word=word, name=name)
        self.use_container_width = use_container_width

    def render(self):
        with st.expander(self.name, True):
            word: str = self.word
            st.write(f"length = {word.len}")
