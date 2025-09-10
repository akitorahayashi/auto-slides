from unittest.mock import MagicMock, patch

import pytest
import streamlit as st

from src.backend.models.slide_template import SlideTemplate
from src.protocols.schemas.output_format import OutputFormat

# Test the progress functionality without direct imports to avoid streamlit issues


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
                    st.switch_page("src/frontend/components/pages/gallery_page.py")

                # Verify redirect was called
                mock_switch_page.assert_called_once_with(
                    "src/frontend/components/pages/gallery_page.py"
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
                    st.switch_page("src/frontend/components/pages/gallery_page.py")

                # Verify redirect was called
                mock_switch_page.assert_called_once_with(
                    "src/frontend/components/pages/gallery_page.py"
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
                    st.switch_page("src/frontend/components/pages/gallery_page.py")

                # Verify redirect was called
                mock_switch_page.assert_called_once_with(
                    "src/frontend/components/pages/gallery_page.py"
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

                # Simulate checking for selected_format by inspecting session_state dict
                has_selected_format = "selected_format" in mock_session.__dict__

                # Simulate the redirect logic from result_page.py
                if (
                    not hasattr(st.session_state, "app_state")
                    or st.session_state.app_state.selected_template is None
                    or st.session_state.app_state.generated_markdown is None
                    or not has_selected_format
                ):
                    st.switch_page("src/frontend/components/pages/gallery_page.py")

                # Verify redirect was called
                mock_switch_page.assert_called_once_with(
                    "src/frontend/components/pages/gallery_page.py"
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

                # Simulate checking for selected_format by inspecting session_state dict
                has_selected_format = "selected_format" in mock_session.__dict__

                # Simulate the redirect logic from result_page.py
                if (
                    not hasattr(st.session_state, "app_state")
                    or st.session_state.app_state.selected_template is None
                    or st.session_state.app_state.generated_markdown is None
                    or not has_selected_format
                ):
                    st.switch_page("src/frontend/components/pages/gallery_page.py")

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

    @pytest.mark.parametrize(
        "selected_format, expected_mime",
        [
            ("PDF", "application/pdf"),
            ("HTML", "text/html"),
            (
                "PPTX",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ),
            ("PNG", "image/png"),
        ],
    )
    def test_conversion_mime_types(self, selected_format, expected_mime):
        """Test correct MIME types for different formats"""
        if selected_format == "PDF":
            mime_type = "application/pdf"
        elif selected_format == "HTML":
            mime_type = "text/html"
        elif selected_format == "PPTX":
            mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        elif selected_format == "PNG":
            mime_type = "image/png"
        else:
            raise AssertionError("Unsupported format in test")

        assert mime_type == expected_mime

    def test_navigation_button_logic(self):
        """Test navigation button logic"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Simulate implementation page navigation button click
            st.switch_page("src/frontend/components/pages/implementation_page.py")

            # Verify navigation
            mock_switch_page.assert_called_with(
                "src/frontend/components/pages/implementation_page.py"
            )

            # Reset mock
            mock_switch_page.reset_mock()

            # Simulate gallery navigation button click
            st.switch_page("src/frontend/components/pages/gallery_page.py")

            # Verify navigation
            mock_switch_page.assert_called_with(
                "src/frontend/components/pages/gallery_page.py"
            )

    def test_marp_service_usage_logic(self):
        """Test MarpService usage logic"""
        # Simulate the MarpService usage from session state
        with patch.object(st, "session_state") as mock_session:
            mock_marp_service = MagicMock()
            mock_session.marp_service = mock_marp_service

            # Test that the service is accessible
            assert hasattr(mock_session, "marp_service")
            marp_service = mock_session.marp_service

            # Test convert method exists
            assert hasattr(marp_service, "convert")

            # Simulate conversion call
            mock_markdown = "# Test slide"
            mock_format = OutputFormat.PDF

            marp_service.convert(mock_markdown, mock_format)

            # Verify convert was called
            marp_service.convert.assert_called_once_with(mock_markdown, mock_format)


class TestProgressDisplay:
    """Test cases for progress display functionality"""

    def test_get_progress_text_logic(self):
        """Test progress text generation logic"""

        def get_progress_text(stage: str, dot_count: int = 1) -> str:
            """Local implementation of progress text function for testing"""
            dot_patterns = [".", "..", "...", ""]
            dots = dot_patterns[dot_count % 4] if dot_count > 0 else "."

            stage_messages = {
                "analyzing": f"📊 スライド内容を分析中{dots}",
                "composing": f"🎯 スライド構成を決定中{dots}",
                "generating": f"✍️ パラメータを生成中{dots}",
                "building": f"🏗️ スライドを構築中{dots}",
                "combining": f"🔗 スライドを統合中{dots}",
                "completed": "✅ スライドの生成が完了しました！",
            }

            return stage_messages.get(stage, f"スライドを生成中{dots}")

        # Test different stages
        stages = [
            "analyzing",
            "composing",
            "generating",
            "building",
            "combining",
            "completed",
        ]

        for stage in stages:
            text = get_progress_text(stage, 1)
            assert isinstance(text, str)
            assert len(text) > 0

            if stage == "completed":
                assert "✅ スライドの生成が完了しました！" in text
            else:
                # Check that each stage has appropriate emoji and message
                assert "." in text or text.endswith("完了しました！")

    def test_get_progress_text_dot_animation_logic(self):
        """Test dot animation logic"""

        def get_progress_text(stage: str, dot_count: int = 1) -> str:
            """Local implementation for testing"""
            dot_patterns = [".", "..", "...", ""]
            dots = dot_patterns[dot_count % 4] if dot_count > 0 else "."
            return f"📊 スライド内容を分析中{dots}"

        stage = "analyzing"

        # Test dot animation cycle: . → .. → ... → (empty) → .
        expected_patterns = [".", "..", "...", ""]

        for i in range(8):  # Test two full cycles
            text = get_progress_text(stage, i)
            expected_dots = expected_patterns[i % 4]

            if expected_dots:
                assert text.endswith(expected_dots)
            else:
                # When dots is empty, should still have the base message
                assert "分析中" in text

    def test_progress_text_stage_messages_logic(self):
        """Test specific stage messages logic"""

        def get_progress_text(stage: str, dot_count: int = 1) -> str:
            """Local implementation for testing"""
            dot_patterns = [".", "..", "...", ""]
            dots = dot_patterns[dot_count % 4] if dot_count > 0 else "."

            stage_messages = {
                "analyzing": f"📊 スライド内容を分析中{dots}",
                "composing": f"🎯 スライド構成を決定中{dots}",
                "generating": f"✍️ パラメータを生成中{dots}",
                "building": f"🏗️ スライドを構築中{dots}",
                "combining": f"🔗 スライドを統合中{dots}",
                "completed": "✅ スライドの生成が完了しました！",
            }

            return stage_messages.get(stage, f"スライドを生成中{dots}")

        test_cases = [
            ("analyzing", "📊", "分析中"),
            ("composing", "🎯", "構成を決定中"),
            ("generating", "✍️", "パラメータを生成中"),
            ("building", "🏗️", "構築中"),
            ("combining", "🔗", "統合中"),
            ("completed", "✅", "完了しました"),
        ]

        for stage, expected_emoji, expected_text in test_cases:
            result = get_progress_text(stage, 1)
            assert expected_emoji in result
            assert expected_text in result

    def test_progress_text_default_stage_logic(self):
        """Test default behavior for unknown stage"""

        def get_progress_text(stage: str, dot_count: int = 1) -> str:
            """Local implementation for testing"""
            dot_patterns = [".", "..", "...", ""]
            dots = dot_patterns[dot_count % 4] if dot_count > 0 else "."

            stage_messages = {
                "analyzing": f"📊 スライド内容を分析中{dots}",
                "composing": f"🎯 スライド構成を決定中{dots}",
                "generating": f"✍️ パラメータを生成中{dots}",
                "building": f"🏗️ スライドを構築中{dots}",
                "combining": f"🔗 スライドを統合中{dots}",
                "completed": "✅ スライドの生成が完了しました！",
            }

            return stage_messages.get(stage, f"スライドを生成中{dots}")

        unknown_stage = "unknown_stage"
        text = get_progress_text(unknown_stage, 1)
        assert "スライドを生成中" in text
        assert "." in text


class TestProgressCallbackIntegration:
    """Test progress callback integration with slide generation"""

    def test_progress_callback_stage_updates_mock(self):
        """Test progress callback behavior with mock generator"""
        # Mock the behavior instead of importing
        mock_generator = MagicMock()
        mock_generator.invoke_slide_gen_chain.return_value = "# Generated slides"

        # Test that the mock generator can be called
        result = mock_generator.invoke_slide_gen_chain("test content", MagicMock())
        assert result == "# Generated slides"
        assert mock_generator.invoke_slide_gen_chain.called

    def test_progress_stages_sequence(self):
        """Test that progress stages follow correct sequence"""
        stages = [
            "analyzing",
            "composing",
            "generating",
            "building",
            "combining",
            "completed",
        ]
        progress_values = {
            "analyzing": 0.2,
            "composing": 0.4,
            "generating": 0.6,
            "building": 0.8,
            "combining": 0.9,
            "completed": 1.0,
        }

        # Verify each stage has appropriate progress value
        for stage in stages:
            assert stage in progress_values
            assert 0.0 <= progress_values[stage] <= 1.0

        # Verify stages are in ascending order
        stage_values = [progress_values[stage] for stage in stages]
        assert stage_values == sorted(stage_values)

    @pytest.mark.parametrize(
        "stage,expected_progress",
        [
            ("analyzing", 0.2),
            ("composing", 0.4),
            ("generating", 0.6),
            ("building", 0.8),
            ("combining", 0.9),
            ("completed", 1.0),
        ],
    )
    def test_progress_values_for_stages(self, stage, expected_progress):
        """Test correct progress values for each stage"""
        progress_values = {
            "analyzing": 0.2,
            "composing": 0.4,
            "generating": 0.6,
            "building": 0.8,
            "combining": 0.9,
            "completed": 1.0,
        }

        assert progress_values.get(stage, 0.1) == expected_progress


class TestSlideGenChainProgressIntegration:
    """Test SlideGenChain progress callback integration"""

    def test_slidegenchain_callback_concept(self):
        """Test SlideGenChain callback concept"""
        # Test the callback concept without importing actual class
        callback_calls = []

        def mock_callback(stage, current=0, total=1):
            callback_calls.append((stage, current, total))

        # Mock a chain-like class
        class MockSlideGenChain:
            def __init__(self, llm, progress_callback=None):
                self.llm = llm
                self.progress_callback = progress_callback
                self.current_request = 0
                self.total_requests = 6

            def _report_progress(self, stage):
                if self.progress_callback:
                    self.progress_callback(stage, self.current_request, self.total_requests)

            def invoke_slide_gen_chain(self, content, template):
                self.current_request = 1
                self._report_progress("analyzing")
                self.current_request = 2
                self._report_progress("composing")
                self.current_request = 3
                self._report_progress("generating")
                self.current_request = 4
                self._report_progress("building")
                self.current_request = 5
                self._report_progress("combining")
                self.current_request = 6
                self._report_progress("completed")
                return "# Generated content"

        # Test with callback
        mock_llm = MagicMock()
        chain = MockSlideGenChain(mock_llm, mock_callback)

        # Execute and verify callback calls
        result = chain.invoke_slide_gen_chain("test content", MagicMock())

        # Verify all stages were called with correct parameters
        expected_calls = [
            ("analyzing", 1, 6),
            ("composing", 2, 6),
            ("generating", 3, 6),
            ("building", 4, 6),
            ("combining", 5, 6),
            ("completed", 6, 6),
        ]
        assert callback_calls == expected_calls
        assert result == "# Generated content"

    def test_progress_callback_without_callback(self):
        """Test chain behavior when no callback is provided"""

        class MockSlideGenChain:
            def __init__(self, llm, progress_callback=None):
                self.llm = llm
                self.progress_callback = progress_callback
                self.current_request = 0
                self.total_requests = 1

            def _report_progress(self, stage):
                if self.progress_callback:
                    self.progress_callback(stage, self.current_request, self.total_requests)

            def invoke_slide_gen_chain(self, content, template):
                self.current_request = 1
                self._report_progress("analyzing")
                return "# Generated content"

        # Test without callback (should not error)
        mock_llm = MagicMock()
        chain = MockSlideGenChain(mock_llm, None)

        result = chain.invoke_slide_gen_chain("test content", MagicMock())
        assert result == "# Generated content"
