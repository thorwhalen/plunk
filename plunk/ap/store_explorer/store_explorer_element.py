from dataclasses import dataclass

import streamlit as st
from front.elements import OutputBase


@dataclass
class StoreExplorer(OutputBase):
    def render(self):
        store = self.output
        print(f'{store=}')
        # Store the initial value of widgets in session state
        if 'depth_keys' not in st.session_state:
            st.session_state.depth_keys = []
            st.session_state.render_count = 0

        print(f'Start {st.session_state.render_count=} {st.session_state.depth_keys=}')

        col1, col2 = st.columns(2)
        with col1:
            st.write('# Keys')
            for i in range(len(st.session_state.depth_keys) + 1):
                if i == 0:
                    d = store
                elif (
                    len(st.session_state.depth_keys) == i
                    and (dk := st.session_state.depth_keys[i - 1]) is not None
                ):
                    d = d[dk]
                else:
                    break

                if isinstance(d, dict):
                    options = [None, *d]
                    k = st.selectbox(key := f'depth_{i}', options=options, key=key)
                    st.session_state.depth_keys = [*st.session_state.depth_keys[:i], k]
                if isinstance(d, list):
                    options = [None, *(j for j in range(len(d)))]
                    k = st.selectbox(key := f'depth_{i}', options=options, key=key)
                    st.session_state.depth_keys = [*st.session_state.depth_keys[:i], k]
            if k is not None:
                print(f'{k=}')
                st.write('Value')
                st.write(d)

        with col2:
            st.write('# Store')
            st.write(store)

        print(f'{st.session_state.depth_keys=}')
        print(f'Finish {st.session_state.render_count=}')
        st.session_state.render_count += 1
