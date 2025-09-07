import os

import streamlit as st
from dotenv import load_dotenv

from src.components.pages import (
    render_download_page,
    render_gallery_page,
    render_result_page,
)
from src.protocols.marp_protocol import MarpProtocol
from src.router import AppRouter, Page

load_dotenv()

st.set_page_config(
    page_title="Auto Slides",
    page_icon="📑",
    # "centered"/"wide"
    layout="wide",
    # "auto"/"expanded"/"collapsed"
    initial_sidebar_state="collapsed",
)


def main():
    """
    The main function that runs the Streamlit application.
    """
    initialize_session()

    app_router = st.session_state.app_router

    # Page routing
    current_page = app_router.current_page
    if current_page == Page.GALLERY:
        render_gallery_page()
    elif current_page == Page.DOWNLOAD:
        render_download_page()
    elif current_page == Page.RESULT:
        render_result_page()
    else:
        st.error(f"Unknown page: {current_page} (type: {type(current_page)})")
        st.write(f"Available pages: {list(Page)}")
        st.stop()


def initialize_session():
    """Initializes the session state."""
    if "app_router" not in st.session_state:
        st.session_state.app_router = AppRouter()

    if "marp_service" not in st.session_state:
        slides_path = "src/templates/sample/content.md"
        output_dir = "output"
        is_debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes", "on")

        if is_debug:
            from dev.mocks.mock_marp_service import MockMarpService

            marp_service: MarpProtocol = MockMarpService(slides_path, output_dir)
        else:
            from src.services.marp_service import MarpService

            marp_service: MarpProtocol = MarpService(slides_path, output_dir)

        st.session_state.marp_service = marp_service


if __name__ == "__main__":
    main()
