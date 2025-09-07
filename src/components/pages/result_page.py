import streamlit as st

from src.router import Page


def render_result_page():
    """
    Renders the result page of the application.
    """
    st.title("Result Page")

    # Display the counter value from session state
    # Initialize if navigating here directly without visiting main_page first
    if "counter" not in st.session_state:
        st.warning("Counter not initialized. Please visit the Main Page first.")
    else:
        counter = st.session_state.counter
        st.write(f"Counter value from session state: {counter.get_count()}")

    app_router = st.session_state.app_router
    if st.button("Back to Main"):
        app_router.go_to(Page.MAIN)
        st.rerun()
