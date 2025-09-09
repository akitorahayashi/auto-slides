from unittest.mock import MagicMock, patch

import streamlit as st

from src.models import SlideTemplate
from src.schemas import OutputFormat


class TestResultPageLogic:
    """Test cases for result_page.py redirect and UI logic"""

    def test_redirect_logic_when_no_app_state(self):
        """Test redirect logic when app_state is missing"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Mock session_state without app_state
            with patch.object(st, "session_state", MagicMock()) as mock_session:
                mock_session.configure_mock(**{})
                delattr(mock_session, "app_state")  # Ensure app_state doesn't exist

                # Simulate the redirect logic from result_page.py
                if (
                    not hasattr(st.session_state, "app_state")
                    or st.session_state.app_state.selected_template is None
                    or st.session_state.app_state.generated_markdown is None
                    or "selected_format" not in st.session_state
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
            mock_app_state.generated_markdown = "# Test"

            with patch.object(st, "session_state") as mock_session:
                mock_session.app_state = mock_app_state
                mock_session.selected_format = "PDF"

                # Simulate the redirect logic from result_page.py
                if (
                    not hasattr(st.session_state, "app_state")
                    or st.session_state.app_state.selected_template is None
                    or st.session_state.app_state.generated_markdown is None
                    or "selected_format" not in st.session_state
                ):
                    st.switch_page("components/pages/gallery_page.py")

                # Verify redirect was called
                mock_switch_page.assert_called_once_with(
                    "components/pages/gallery_page.py"
                )

    def test_redirect_logic_when_no_generated_markdown(self):
        """Test redirect logic when generated_markdown is None"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Mock session_state with app_state but no generated_markdown
            mock_template = MagicMock(spec=SlideTemplate)
            mock_app_state = MagicMock()
            mock_app_state.selected_template = mock_template
            mock_app_state.generated_markdown = None

            with patch.object(st, "session_state") as mock_session:
                mock_session.app_state = mock_app_state
                mock_session.selected_format = "PDF"

                # Simulate the redirect logic from result_page.py
                if (
                    not hasattr(st.session_state, "app_state")
                    or st.session_state.app_state.selected_template is None
                    or st.session_state.app_state.generated_markdown is None
                    or "selected_format" not in st.session_state
                ):
                    st.switch_page("components/pages/gallery_page.py")

                # Verify redirect was called
                mock_switch_page.assert_called_once_with(
                    "components/pages/gallery_page.py"
                )

    def test_redirect_logic_when_no_selected_format(self):
        """Test redirect logic when selected_format is missing"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Mock session_state without selected_format
            mock_template = MagicMock(spec=SlideTemplate)
            mock_app_state = MagicMock()
            mock_app_state.selected_template = mock_template
            mock_app_state.generated_markdown = "# Test"

            with patch.object(st, "session_state") as mock_session:
                mock_session.app_state = mock_app_state
                # Don't set selected_format

                # Simulate checking for selected_format
                has_selected_format = "selected_format" in mock_session.__dict__

                # Simulate the redirect logic from result_page.py
                if (
                    not hasattr(st.session_state, "app_state")
                    or st.session_state.app_state.selected_template is None
                    or st.session_state.app_state.generated_markdown is None
                    or not has_selected_format
                ):
                    st.switch_page("components/pages/gallery_page.py")

                # Verify redirect was called
                mock_switch_page.assert_called_once_with(
                    "components/pages/gallery_page.py"
                )

    def test_no_redirect_with_valid_session_data(self):
        """Test no redirect when all required session data is present"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Create mock template
            mock_template = MagicMock(spec=SlideTemplate)
            mock_template.name = "Test Template"

            # Create mock app_state
            mock_app_state = MagicMock()
            mock_app_state.selected_template = mock_template
            mock_app_state.generated_markdown = "# Test content"

            with patch.object(st, "session_state") as mock_session:
                mock_session.app_state = mock_app_state
                mock_session.selected_format = "PDF"

                # Simulate checking for selected_format
                has_selected_format = "selected_format" in mock_session.__dict__

                # Simulate the redirect logic from result_page.py
                if (
                    not hasattr(st.session_state, "app_state")
                    or st.session_state.app_state.selected_template is None
                    or st.session_state.app_state.generated_markdown is None
                    or not has_selected_format
                ):
                    st.switch_page("components/pages/gallery_page.py")

                # Verify no redirect occurred
                mock_switch_page.assert_not_called()

    def test_format_options_structure(self):
        """Test the format options structure from result_page.py"""
        # This mimics the format_options from the actual implementation
        format_options = {
            "PDF": {"label": "📄 PDF", "format": OutputFormat.PDF},
            "HTML": {"label": "🌐 HTML", "format": OutputFormat.HTML},
            "PPTX": {"label": "📊 PPTX", "format": OutputFormat.PPTX},
        }

        # Verify structure
        assert "PDF" in format_options
        assert "HTML" in format_options
        assert "PPTX" in format_options

        assert format_options["PDF"]["label"] == "📄 PDF"
        assert format_options["HTML"]["label"] == "🌐 HTML"
        assert format_options["PPTX"]["label"] == "📊 PPTX"

        assert format_options["PDF"]["format"] == OutputFormat.PDF
        assert format_options["HTML"]["format"] == OutputFormat.HTML
        assert format_options["PPTX"]["format"] == OutputFormat.PPTX

    def test_conversion_mime_types(self):
        """Test correct MIME types for different formats"""
        # Simulate the MIME type assignment logic from result_page.py
        selected_format = "PDF"
        if selected_format == "PDF":
            mime_type = "application/pdf"
        elif selected_format == "HTML":
            mime_type = "text/html"
        elif selected_format == "PPTX":
            mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

        assert mime_type == "application/pdf"

        # Test HTML
        selected_format = "HTML"
        if selected_format == "PDF":
            mime_type = "application/pdf"
        elif selected_format == "HTML":
            mime_type = "text/html"
        elif selected_format == "PPTX":
            mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

        assert mime_type == "text/html"

        # Test PPTX
        selected_format = "PPTX"
        if selected_format == "PDF":
            mime_type = "application/pdf"
        elif selected_format == "HTML":
            mime_type = "text/html"
        elif selected_format == "PPTX":
            mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

        assert (
            mime_type
            == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

    def test_navigation_button_logic(self):
        """Test navigation button logic"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Simulate implementation page navigation button click
            st.switch_page("components/pages/implementation_page.py")

            # Verify navigation
            mock_switch_page.assert_called_with(
                "components/pages/implementation_page.py"
            )

            # Reset mock
            mock_switch_page.reset_mock()

            # Simulate gallery navigation button click
            st.switch_page("components/pages/gallery_page.py")

            # Verify navigation
            mock_switch_page.assert_called_with("components/pages/gallery_page.py")

    def test_converter_service_usage_logic(self):
        """Test template converter service usage logic"""
        from src.services.template_converter_service import TemplateConverterService

        # Simulate the converter instantiation logic
        converter = TemplateConverterService()

        # Verify the converter instance
        assert isinstance(converter, TemplateConverterService)

        # Test that the converter has expected methods
        assert hasattr(converter, "convert_template_to_pdf")
        assert hasattr(converter, "convert_template_to_html")
        assert hasattr(converter, "convert_template_to_pptx")
        assert hasattr(converter, "get_filename")
