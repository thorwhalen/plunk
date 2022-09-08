import streamlit.components.v1 as components  # Import Streamlit

# Import the wrapper function from your package
from streamlit_folder_browser import st_folder_browser
import streamlit as st


st.title('Testing Streamlit custom components')
v = st_folder_browser()
st.write(v)
