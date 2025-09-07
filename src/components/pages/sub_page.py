import streamlit as st


def render_sub_page():
    """
    Renders the sub page of the application.
    """
    # Clear previous content when navigating between pages
    st.empty()

    st.title("Sub Page")
    st.write("This is the sub page.")
