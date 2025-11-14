import streamlit as st
from dataclasses import dataclass
from front.elements import OutputBase

configs = None


class HtmlOutput(OutputBase):
    def render(self):
        st.markdown(self.output, unsafe_allow_html=True)


from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from plunk.tw.i2i_demos.play.resources import funcs


config = {
    APP_KEY: {'title': "Making children's stories"},
    RENDERING_KEY: {
        '_make_children_story': {
            # NAME_KEY: 'Hit the value',
            # 'description': {
            #     'content': '''
            #         No description
            #     ''',
            # },
            'execution': {'output': {ELEMENT_KEY: HtmlOutput,},},
        },
        'aggregate_story_and_image': {
            # NAME_KEY: 'Hit the value',
            # 'description': {
            #     'content': '''
            #         No description
            #     ''',
            # },
            'execution': {'output': {ELEMENT_KEY: HtmlOutput,},},
        },
    },
}
