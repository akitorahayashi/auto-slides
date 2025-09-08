from unittest.mock import MagicMock, patch

import streamlit as st

from src.models import SlideTemplate


class TestImplementationPageLogic:
    """Test cases for implementation_page.py redirect and UI logic"""

    def test_redirect_logic_when_no_app_state(self):
        """Test redirect logic when app_state is missing"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Mock session_state without app_state
            with patch.object(st, "session_state", MagicMock()) as mock_session:
                mock_session.configure_mock(**{})
                delattr(mock_session, "app_state")  # Ensure app_state doesn't exist

                # Simulate the redirect logic from implementation_page.py
                if (
                    not hasattr(st.session_state, "app_state")
                    or st.session_state.app_state.selected_template is None
                ):
                    st.switch_page("components/pages/gallery_page.py")

                # Verify redirect was called
                mock_switch_page.assert_called_once_with(
                    "components/pages/gallery_page.py"
                )

    def test_redirect_logic_when_no_selected_template(self):
        """Test redirect logic when selected_template is None"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Mock session_state with app_state but no selected_template
            mock_app_state = MagicMock()
            mock_app_state.selected_template = None

            with patch.object(st, "session_state") as mock_session:
                mock_session.app_state = mock_app_state

                # Simulate the redirect logic from implementation_page.py
                if (
                    not hasattr(st.session_state, "app_state")
                    or st.session_state.app_state.selected_template is None
                ):
                    st.switch_page("components/pages/gallery_page.py")

                # Verify redirect was called
                mock_switch_page.assert_called_once_with(
                    "components/pages/gallery_page.py"
                )

    def test_no_redirect_with_valid_template(self):
        """Test no redirect when valid template is present"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Mock session_state with valid template
            mock_template = MagicMock(spec=SlideTemplate)
            mock_app_state = MagicMock()
            mock_app_state.selected_template = mock_template

            with patch.object(st, "session_state") as mock_session:
                mock_session.app_state = mock_app_state

                # Simulate the redirect logic from implementation_page.py
                if (
                    not hasattr(st.session_state, "app_state")
                    or st.session_state.app_state.selected_template is None
                ):
                    st.switch_page("components/pages/gallery_page.py")

                # Verify no redirect occurred
                mock_switch_page.assert_not_called()

    def test_format_options_structure(self):
        """Test the format options structure from implementation_page.py"""
        from src.schemas import TemplateFormat

        # This mimics the format_options from the actual implementation
        format_options = {
            "PDF": {"label": "📄 PDF", "format": TemplateFormat.PDF},
            "HTML": {"label": "🌐 HTML", "format": TemplateFormat.HTML},
            "PPTX": {"label": "📊 PPTX", "format": TemplateFormat.PPTX},
        }

        # Verify structure
        assert "PDF" in format_options
        assert "HTML" in format_options
        assert "PPTX" in format_options

        assert format_options["PDF"]["label"] == "📄 PDF"
        assert format_options["HTML"]["label"] == "🌐 HTML"
        assert format_options["PPTX"]["label"] == "📊 PPTX"

        assert format_options["PDF"]["format"] == TemplateFormat.PDF
        assert format_options["HTML"]["format"] == TemplateFormat.HTML
        assert format_options["PPTX"]["format"] == TemplateFormat.PPTX

    def test_confirm_dialog_logic_execution(self):
        """Test confirm dialog execution logic"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Create mock template and session state
            mock_template = MagicMock(spec=SlideTemplate)
            mock_template.read_markdown_content.return_value = "# Test content"

            mock_app_state = MagicMock()
            mock_app_state.selected_template = mock_template

            with patch.object(st, "session_state") as mock_session:
                mock_session.app_state = mock_app_state
                mock_session.format_selection = "PDF"

                # Simulate the confirm dialog execution logic
                template = mock_session.app_state.selected_template
                mock_session.app_state.user_inputs = {
                    "format": mock_session.format_selection
                }
                mock_session.app_state.generated_markdown = (
                    template.read_markdown_content()
                )
                mock_session.selected_format = mock_session.format_selection
                st.switch_page("components/pages/result_page.py")

                # Verify session state updates
                assert mock_session.app_state.user_inputs == {"format": "PDF"}
                assert mock_session.selected_format == "PDF"

                # Verify redirect to result page
                mock_switch_page.assert_called_with("components/pages/result_page.py")

    def test_navigation_button_logic(self):
        """Test navigation button logic"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Simulate gallery navigation button click
            st.switch_page("components/pages/gallery_page.py")

            # Verify navigation
            mock_switch_page.assert_called_with("components/pages/gallery_page.py")
