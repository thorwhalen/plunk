# taken from https://github.com/aidanjungo/StreamlitDirectoryPicker/blob/main/directorypicker.py
import streamlit as st
from pathlib import Path


def st_directory_picker(initial_path=Path()):

    st.markdown('#### Directory picker')

    if 'path' not in st.session_state:
        st.session_state.path = initial_path.absolute()

    st.text_input('Selected directory:', st.session_state.path)

    _, col1, col2, col3, _ = st.columns([3, 1, 3, 1, 3])

    with col1:
        st.markdown('#')
        if st.button('⬅️') and 'path' in st.session_state:
            st.session_state.path = st.session_state.path.parent
            st.experimental_rerun()

    with col2:
        subdirectroies = [
            f.stem
            for f in st.session_state.path.iterdir()
            if f.is_dir()
            and (not f.stem.startswith('.') and not f.stem.startswith('__'))
        ]
        if subdirectroies:
            st.session_state.new_dir = st.selectbox(
                'Subdirectories', sorted(subdirectroies)
            )
        else:
            st.markdown('#')
            st.markdown(
                "<font color='#FF0000'>No subdir</font>", unsafe_allow_html=True
            )

    with col3:
        if subdirectroies:
            st.markdown('#')
            if st.button('➡️') and 'path' in st.session_state:
                st.session_state.path = Path(
                    st.session_state.path, st.session_state.new_dir
                )
                st.experimental_rerun()

    return st.session_state.path
