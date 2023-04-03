import streamlit as st
from dataclasses import dataclass

# from front.elements import OutputBase
from streamlitfront.elements import OutputBase
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY

configs = None


@dataclass
class Markdown(OutputBase):
    def render(self):
        html = '''
        f'<html><body><h1>{self.output}</h1></body></html>'
        '''
        html = '''
        <img src="https://oaidalleapiprodscus.blob.core.windows.net/private/org-AY3lr3H3xB9yPQ0HGR498f9M/user-7ZNCDYLWzP0GT48V6DCiTFWt/img-W6rSgzo5Kz3AevLsIm2mRYMf.png?st=2023-03-31T15%3A20%3A08Z&se=2023-03-31T17%3A20%3A08Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-03-30T18%3A05%3A30Z&ske=2023-03-31T18%3A05%3A30Z&sks=b&skv=2021-08-06&sig=ZF/tKVnuuiomcbeTwbXq8tLu01gFs3LfGZBsP60BP5o%3D" /> <p><p>Once there was a boy who cried wolf,<br>Whenever something bad happened to him.<br>His parents scolded him,<br>The other kids made fun of him,<br>But he didn&#x27;t care,<br>Because he knew that they&#x27;d all be there,<br>Whenever he needed them.<br><br>One day, a real wolf came along,<br>And the boy cried out for help.<br>But no one came,<br>Because they thought he was lying,<br>And the wolf ate him up.<br><br>The moral of the story is:<br>Don&#x27;t cry wolf unless you&#x27;re sure,<br>Or you&#x27;ll end up eaten like shrimp in chowder.</p></p>
        '''
        html = '''
        <img src="https://www.google.com/url?sa=i&url=https%3A%2F%2Fimages.panda.org%2F&psig=AOvVaw1i8zfwyzVh9alatKH8tlCM&ust=1680369823445000&source=images&cd=vfe&ved=0CA8QjRxqFwoTCMDL8cTXhv4CFQAAAAAdAAAAABAE">
        '''
        return st.components.v1.html(html, width=None, height=None, scrolling=False)


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
