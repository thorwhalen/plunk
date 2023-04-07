"""Demo utils
(Which should really be a stage for tools that we SHOULD have in our libraries.)
"""

from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY

import streamlit as st
from dataclasses import dataclass
from front.elements import OutputBase

from dol.paths import path_edit

configs = None


class HtmlOutputWrap(OutputBase):
    def render(self):
        st.markdown(
            f'<html> <body> <img src="{self.output}" /> </body> </html>',
            unsafe_allow_html=True,
        )


class HtmlOutput(OutputBase):
    def render(self):
        st.markdown(self.output, unsafe_allow_html=True)


from i2 import mk_sentinel


NoChanges = mk_sentinel('NoChanges')


def forgiving_path_get(d: dict, path: list, default=None):
    """Get a value from a nested dictionary, without raising exceptions"""
    for key in path:
        if key in d:
            d = d[key]
        else:
            return default
    return d


# def add_output_trans(configs: dict, **trans_for_key):
#     def _gen():

from copy import deepcopy
from dol import path_set
