from unittest.mock import MagicMock, patch

import streamlit as st

from dev.mocks.mock_slide_generator import MockSlideGenerator
from src.backend.chains.slide_gen_chain import SlideGenChain
from src.frontend.app_state import AppState
from src.main import initialize_session


def test_protocol_integration_with_real_chain():
    """
    Tests that the frontend can be integrated with the real SlideGenChain
    via the SlideGenerationProtocol.
    """
    # 1. Set secrets for non-debug mode
    with patch("streamlit.secrets") as mock_secrets:
        mock_secrets.get.return_value = "false"  # Not in debug mode

        # 2. Initialize the session state, which performs DI
        with patch.object(st, "session_state", MagicMock()) as mock_session:
            # make sure app_state is not in session
            if hasattr(mock_session, "app_state"):
                del mock_session.app_state
            initialize_session()

            # 3. Verify the injected generator is the real one
            app_state: AppState = st.session_state.app_state
            assert isinstance(app_state.slide_generator, SlideGenChain)


def test_protocol_integration_with_mock_generator():
    """
    Tests that the frontend can be integrated with the MockSlideGenerator
    via the SlideGenerationProtocol in debug mode.
    """
    # 1. Set secrets for debug mode
    with patch("streamlit.secrets") as mock_secrets:
        mock_secrets.get.return_value = "true"  # In debug mode

        # 2. Initialize the session state
        with patch.object(st, "session_state", MagicMock()) as mock_session:
            if hasattr(mock_session, "app_state"):
                del mock_session.app_state
            initialize_session()

            # 3. Verify the injected generator is the mock one
            app_state: AppState = st.session_state.app_state
            assert isinstance(app_state.slide_generator, MockSlideGenerator)
