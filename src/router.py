from enum import Enum, auto

import streamlit as st


class Page(Enum):
    """
    Enumeration for the different pages in the application.
    """

    MAIN = auto()
    RESULT = auto()
    SUB = auto()


class AppRouter:
    """
    Manages the application's routing and navigation state.
    """

    def __init__(self):
        """
        Initializes the router.
        Sets the default page in the session state if it's not already set.
        """
        if "page" not in st.session_state:
            st.session_state.page = Page.MAIN

    @property
    def current_page(self) -> Page:
        """
        Gets the current page from the session state.

        Returns:
            Page: The current page enum.
        """
        return st.session_state.page

    def go_to(self, page: Page):
        """
        Navigates to the specified page.

        Args:
            page (Page): The page to navigate to.
        """
        st.session_state.page = page
