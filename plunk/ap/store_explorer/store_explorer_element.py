from dataclasses import dataclass

import streamlit as st
from front.elements import OutputBase


@dataclass
class StoreExplorer(OutputBase):
    def render(self):
        print(self.output)
        st.write(self.output)
