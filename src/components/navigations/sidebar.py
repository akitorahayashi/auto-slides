import streamlit as st

from src.router import AppRouter, Page


def render_sidebar():
    """
    Renders the sidebar for navigation.
    """
    app_router: AppRouter = st.session_state.app_router

    pages = {
        "Main": Page.MAIN,
        "Sub": Page.SUB,
    }

    # Do nothing if the current page is not included in the sidebar navigation
    if app_router.current_page not in pages.values():
        return

    current_page_label = next(
        (label for label, page in pages.items() if page == app_router.current_page),
        "Main",
    )

    selection = st.sidebar.radio(
        "Navigation",
        options=list(pages.keys()),
        key="sidebar_navigation",
        index=list(pages.keys()).index(current_page_label),
        label_visibility="collapsed",
    )

    if pages[selection] != app_router.current_page:
        app_router.go_to(pages[selection])
        st.rerun()
