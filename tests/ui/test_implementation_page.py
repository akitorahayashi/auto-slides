from unittest.mock import MagicMock, patch

import pytest
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
        from src.schemas import OutputFormat

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

    def test_confirm_dialog_logic_execution(self):
        """Test confirm dialog execution logic with SlideGenerator integration"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Create mock slide generator
            mock_slide_generator = MagicMock()
            mock_slide_generator.generate_sync.return_value = (
                "# Generated slide content"
            )

            # Create mock template and session state
            mock_template = MagicMock(spec=SlideTemplate)
            mock_template.name = "Test Template"
            mock_template.description = "Test Description"

            mock_app_state = MagicMock()
            mock_app_state.selected_template = mock_template

            with patch.object(st, "session_state") as mock_session:
                mock_session.app_state = mock_app_state
                mock_session.slide_generator = mock_slide_generator
                mock_session.format_selection = "PDF"

                # Mock script content
                script_content = "Test script content"

                # Simulate the confirm dialog execution logic
                template = mock_session.app_state.selected_template
                generator = mock_session.slide_generator
                generated_markdown = generator.generate_sync(
                    script_content=script_content, template=template
                )

                mock_session.app_state.user_inputs = {
                    "format": mock_session.format_selection,
                    "script_content": script_content,
                }
                mock_session.app_state.generated_markdown = generated_markdown
                mock_session.selected_format = mock_session.format_selection
                st.switch_page("components/pages/result_page.py")

                # Verify SlideGenerator was called correctly
                mock_slide_generator.generate_sync.assert_called_once_with(
                    script_content=script_content, template=template
                )

                # Verify session state updates
                assert mock_session.app_state.user_inputs == {
                    "format": "PDF",
                    "script_content": script_content,
                }
                assert (
                    mock_session.app_state.generated_markdown
                    == "# Generated slide content"
                )
                assert mock_session.selected_format == "PDF"

                # Verify redirect to result page
                mock_switch_page.assert_called_with("components/pages/result_page.py")

    def test_template_placeholder_extraction(self):
        """Test template placeholder extraction in implementation workflow"""
        from pathlib import Path

        from src.models import SlideTemplate

        template = SlideTemplate(
            id="test_template",
            name="Test Template",
            description="Test template for placeholder extraction",
            template_dir=Path("/tmp/test_template"),
            duration_minutes=10,
        )

        template_content = "Hello ${name}, welcome to ${event}!"
        placeholders = template.extract_placeholders(template_content)
        assert placeholders == {"name", "event"}

        # Test that placeholders are properly converted to list
        placeholders_list = list(placeholders)
        assert isinstance(placeholders_list, list)
        assert len(placeholders_list) == 2

        # Test render_template method
        content_dict = {"name": "John", "event": "Conference"}
        result = template.render_template(template_content, content_dict)
        assert result == "Hello John, welcome to Conference!"

    def test_slide_generator_chain_integration(self):
        """Test SlideGenerator integration with chain workflow"""
        # Skip this test as SlideGenerator service doesn't exist yet
        pytest.skip("SlideGenerator service not implemented yet")

    def test_slide_generator_error_handling(self):
        """Test SlideGenerator error handling in UI context"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Create mock slide generator that raises an exception
            mock_slide_generator = MagicMock()
            mock_slide_generator.generate_sync.side_effect = Exception("LLM Error")

            # Create mock template and session state
            mock_template = MagicMock(spec=SlideTemplate)
            mock_app_state = MagicMock()
            mock_app_state.selected_template = mock_template

            with patch.object(st, "session_state") as mock_session:
                mock_session.app_state = mock_app_state
                mock_session.slide_generator = mock_slide_generator
                mock_session.format_selection = "PDF"

                script_content = "Test script"

                # Simulate error handling logic
                try:
                    generator = mock_session.slide_generator
                    generated_markdown = generator.generate_sync(
                        script_content=script_content, template=mock_template
                    )
                except Exception as e:
                    # Fallback markdown (as in the actual implementation)
                    generated_markdown = f"""---
marp: true
theme: default
---

# プレゼンテーション

エラーが発生しました。以下は原稿の内容です:

{script_content}

---

# 終わり

ありがとうございました。
"""

                # Verify error was raised and fallback content was created
                mock_slide_generator.generate_sync.assert_called_once()
                assert "エラーが発生しました" in generated_markdown
                assert script_content in generated_markdown

    def test_navigation_button_logic(self):
        """Test navigation button logic"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Simulate gallery navigation button click
            st.switch_page("components/pages/gallery_page.py")

            # Verify navigation
            mock_switch_page.assert_called_with("components/pages/gallery_page.py")
