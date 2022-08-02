import streamlit as st

st.title("Display")
st.write(st.session_state["shared"])
st.session_state["shared"] = "page display visited"
