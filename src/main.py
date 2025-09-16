from pathlib import Path

import streamlit as st

from src.backend.chains.slide_gen_chain import SlideGenChain
from src.backend.models.template_repository import TemplateRepository
from src.frontend.app_state import AppState
from src.protocols.protocols.marp_protocol import MarpProtocol
from src.protocols.slide_generation_protocol import SlideGenerationProtocol

st.set_page_config(
    page_title="Auto Slides",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def main():
    """
    The main function that runs the Streamlit application.
    """
    initialize_session()

    pg = st.navigation(
        [
            st.Page(
                "frontend/components/pages/gallery_page.py",
                title="ギャラリー",
                default=True,
            ),
            st.Page("frontend/components/pages/implementation_page.py", title="実行"),
            st.Page("frontend/components/pages/result_page.py", title="結果"),
        ],
        position="hidden",
    )

    pg.run()


def initialize_session():
    """Initializes the session state."""
    if "app_state" not in st.session_state:
        debug_value = st.secrets.get("DEBUG", "false")
        is_debug = str(debug_value).lower() == "true"

        slide_generator: SlideGenerationProtocol
        template_repository: TemplateRepository
        marp_service: MarpProtocol

        if is_debug:
            from dev.mocks import (
                MockMarpService,
                MockSlideGenerator,
                MockTemplateRepository,
            )

            template_repository = MockTemplateRepository(
                templates_dir=Path("src/backend/templates")
            )
            slide_generator = MockSlideGenerator()
            marp_service = MockMarpService("", "")
        else:
            from src.backend.services import MarpService

            template_repository = TemplateRepository()
            slide_generator = SlideGenChain()
            marp_service = MarpService("", "")

        st.session_state.app_state = AppState(
            template_repository=template_repository,
            slide_generator=slide_generator,
        )
        st.session_state.marp_service = marp_service


if __name__ == "__main__":
    main()
