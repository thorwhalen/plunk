import streamlit as st
import pandas as pd

st.write('# Solution using a dataframe')

# initialize the empty data frame on first page load
if 'data' not in st.session_state:
    data = pd.DataFrame({'Expense': [], 'Amount': [], 'Budget': [], 'Variance': []})
    st.session_state.data = data

# show current data (will be empty to first time the page is opened, but will then show the
# incrementally built table of data with each user interactions
st.dataframe(st.session_state.data)

# this is the function the sends the information to that dataframe when called
# variance is calculated at this point
def add_dfForm():
    row = pd.DataFrame(
        {
            'Expense': [st.session_state.input_expense],
            'Amount': [st.session_state.input_amount],
            'Budget': [st.session_state.input_budget],
            'Variance': [st.session_state.input_budget - st.session_state.input_amount],
        }
    )
    st.session_state.data = pd.concat([st.session_state.data, row])


# here's the place for the user to specify information
dfForm = st.form(clear_on_submit=True, key='dfForm')
with dfForm:
    dfColumns = st.columns(4)
    with dfColumns[0]:
        st.text_input('Expense', key='input_expense')
    with dfColumns[1]:
        st.number_input('Amount', key='input_amount')
    with dfColumns[2]:
        st.number_input('Budget', key='input_budget')
    with dfColumns[3]:
        # this button calls the add_dfForm funciton to add data when clicked
        # after add_dfForm runs, the page reloads from the top, rerunning and overwriting everything
        st.form_submit_button(on_click=add_dfForm)
