import streamlit as st

from src.protocols.marp_protocol import MarpProtocol
from src.state.app_state import AppState

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
    initialize_app_state()
    initialize_services()

    # st.navigationでページのリストを定義
    pg = st.navigation(
        [
            st.Page(
                "src/components/pages/gallery_page.py", title="ギャラリー", default=True
            ),
            st.Page("src/components/pages/implementation_page.py", title="実行"),
            st.Page("src/components/pages/result_page.py", title="結果"),
            st.Page("src/components/pages/download_page.py", title="ダウンロード"),
        ],
        position="hidden",
    )

    # アプリケーションを実行
    pg.run()


def initialize_app_state():
    """
    Initializes the application state using AppState class.
    If 'app_state' is not in st.session_state, it creates a new AppState object.
    """
    if "app_state" not in st.session_state:
        st.session_state.app_state = AppState()


def initialize_services():
    """Initializes the services required by the application."""
    if "marp_service" not in st.session_state:
        slides_path = "src/templates/sample/content.md"
        output_dir = "output"
        # .envファイルの代わりにst.secretsを使用
        is_debug = st.secrets.get("DEBUG", "false").lower() in (
            "true",
            "1",
            "yes",
            "on",
        )

        if is_debug:
            from dev.mocks.mock_marp_service import MockMarpService

            marp_service: MarpProtocol = MockMarpService(slides_path, output_dir)
        else:
            from src.services.marp_service import MarpService

            marp_service: MarpProtocol = MarpService(slides_path, output_dir)

        st.session_state.marp_service = marp_service


if __name__ == "__main__":
    main()
