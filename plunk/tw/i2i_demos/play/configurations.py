import streamlit as st
from dataclasses import dataclass
from front.elements import OutputBase

configs = None


@dataclass
class Markdown(OutputBase):
    def render(self):
        return st.markdown(
            f'<html><body><h1>{self.output}</h1></body></html>', unsafe_allow_html=True
        )


from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY


config = {
    APP_KEY: {'title': "Making children's stories"},
    RENDERING_KEY: {
        'aggregate_story_and_image': {
            NAME_KEY: 'Hit the value',
            'description': {
                'content': '''
                    No description
                ''',
            },
            'execution': {'output': {ELEMENT_KEY: Markdown,},},
        }
    },
}
