import os

import streamlit as st
from dotenv import load_dotenv

from src.protocols.marp_protocol import MarpProtocol

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

    # st.navigationでページのリストを定義
    pg = st.navigation(
        [
            st.Page(
                "components/pages/gallery_page.py", title="ギャラリー", default=True
            ),
            st.Page("components/pages/implementation_page.py", title="実行"),
            st.Page("components/pages/result_page.py", title="結果"),
        ],
        position="hidden",
    )

    # アプリケーションを実行
    pg.run()


def initialize_session():
    """Initializes the session state."""
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
