from pathlib import Path

import streamlit as st

from src.app_state import AppState
from src.models.template_repository import TemplateRepository
from src.protocols.marp_protocol import MarpProtocol
from src.services.slide_generator import SlideGenerator

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
        is_debug = st.secrets.get("DEBUG", False)

        if is_debug:
            from dev.mocks.mock_template_repository import MockTemplateRepository

            template_repository = MockTemplateRepository(
                templates_dir=Path("data/development/templates")
            )
        else:
            template_repository = TemplateRepository()

        templates = template_repository.get_all_templates()
        if not templates:
            st.error("テンプレートが見つかりません。")
            st.stop()
        default_template = templates[0]

        slides_path = default_template.markdown_path
        output_dir = "output"

        if is_debug:
            from dev.mocks.mock_marp_service import MockMarpService

            marp_service: MarpProtocol = MockMarpService(slides_path, output_dir)
        else:
            from src.services import MarpService

            marp_service: MarpProtocol = MarpService(slides_path, output_dir)

        st.session_state.marp_service = marp_service
        st.session_state.template_repository = template_repository

    if "slide_generator" not in st.session_state:
        st.session_state.slide_generator = SlideGenerator()

    if "app_state" not in st.session_state:
        st.session_state.app_state = AppState(
            template_repository=template_repository,
            slide_generator=st.session_state.slide_generator,
        )


if __name__ == "__main__":
    main()
