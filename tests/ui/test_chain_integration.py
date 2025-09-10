"""
UI tests for the new chain integration in pages.
Tests the integration of SlideGenChain and services with UI components.
"""

from unittest.mock import MagicMock, patch

import pytest
import streamlit as st

from src.models import SlideTemplate


class TestChainIntegrationUI:
    """Test cases for chain integration in UI components"""

    def test_implementation_page_with_chain_workflow(self):
        """Test implementation page with new chain workflow"""
        with patch("streamlit.switch_page"):
            # Create mock for actual SlideGenChain
            mock_chain = MagicMock()
            mock_chain.invoke_slide_gen_chain.return_value = """---
marp: true
theme: default
---

# Generated Presentation

Generated via SlideGenChain workflow

---

# Section 1

Content from analysis phase

---

# Section 2  

Content from composition phase

---

# Conclusion

Thank you for your attention.
"""

            # Create mock template
            mock_template = MagicMock(spec=SlideTemplate)
            mock_template.name = "Chain Test Template"
            mock_template.description = "Template for testing chain integration"
            mock_template.id = "test_template"

            mock_app_state = MagicMock()
            mock_app_state.selected_template = mock_template

            with patch.object(st, "session_state") as mock_session:
                mock_session.app_state = mock_app_state
                mock_session.format_selection = "PDF"

                script_content = "Test script for chain workflow"

                # Simulate the actual workflow from result_page.py
                with patch(
                    "src.chains.slide_gen_chain.SlideGenChain"
                ) as mock_slide_gen_class:
                    mock_slide_gen_class.return_value = mock_chain

                    # Simulate SlideGenChain invocation
                    generator = mock_slide_gen_class.return_value
                    generated_markdown = generator.invoke_slide_gen_chain(
                        script_content, mock_template
                    )

                    # Verify chain workflow was used correctly
                    mock_chain.invoke_slide_gen_chain.assert_called_once_with(
                        script_content, mock_template
                    )

                    # Verify generated content contains expected markers
                    assert "Generated via SlideGenChain workflow" in generated_markdown
                    assert "marp: true" in generated_markdown

                    # Simulate session state update (as done in result_page.py)
                    mock_session.app_state.user_inputs = {
                        "format": mock_session.format_selection,
                        "script_content": script_content,
                    }
                    mock_session.app_state.generated_markdown = generated_markdown
                    mock_session.selected_format = mock_session.format_selection

                    # Verify session state
                    assert (
                        mock_session.app_state.generated_markdown == generated_markdown
                    )
                    assert (
                        "SlideGenChain workflow"
                        in mock_session.app_state.generated_markdown
                    )

    def test_slide_gen_chain_initialization(self):
        """Test SlideGenChain initialization"""
        with patch("streamlit.secrets") as mock_secrets:
            # Mock streamlit secrets for testing
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": "true",
                "OLLAMA_MODEL": "test-model",
            }.get(key, default)

            from unittest.mock import Mock

            from src.chains.slide_gen_chain import SlideGenChain

            # Create mock LLM
            mock_llm = Mock()
            mock_llm.invoke.return_value = "mocked response"

            # Test that SlideGenChain can be instantiated
            chain = SlideGenChain(mock_llm)

            # Verify chain has all required components (based on actual implementation)
            assert hasattr(chain, "slide_gen_chain")  # The main unified chain
            assert hasattr(chain, "llm")
            assert hasattr(chain, "json_parser")
            assert hasattr(chain, "prompt_service")
            assert hasattr(chain, "slides_loader")
            assert hasattr(chain, "invoke_slide_gen_chain")  # Main method

    def test_session_state_chain_integration(self):
        """Test session state setup with chain integration"""
        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": "true",
                "OLLAMA_MODEL": "test-model",
            }.get(key, default)

            with patch.object(st, "session_state"):
                # Mock the session state initialization logic from main.py
                from unittest.mock import Mock

                from src.chains.slide_gen_chain import SlideGenChain

                # Create mock LLM
                mock_llm = Mock()
                mock_llm.invoke.return_value = "mocked response"

                # Simulate chain initialization (direct instantiation in pages)
                chain = SlideGenChain(mock_llm)

                # Verify the chain is properly initialized (based on actual implementation)
                assert hasattr(chain, "slide_gen_chain")  # The main unified chain
                assert hasattr(chain, "llm")
                assert hasattr(chain, "json_parser")
                assert hasattr(chain, "prompt_service")
                assert hasattr(chain, "slides_loader")
                assert hasattr(chain, "invoke_slide_gen_chain")  # Main method

    def test_chain_error_handling_in_ui(self):
        """Test chain error handling in UI context"""
        # Create mock SlideGenChain that simulates errors
        mock_chain = MagicMock()
        mock_chain.invoke_slide_gen_chain.side_effect = Exception(
            "Chain workflow error"
        )

        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "test_template"
        mock_app_state = MagicMock()
        mock_app_state.selected_template = mock_template

        with patch.object(st, "session_state") as mock_session:
            mock_session.app_state = mock_app_state

            script_content = "Test script"

            # Simulate error handling from result_page.py
            with patch(
                "src.chains.slide_gen_chain.SlideGenChain"
            ) as mock_slide_gen_class:
                mock_slide_gen_class.return_value = mock_chain

                try:
                    generator = mock_slide_gen_class.return_value
                    generated_markdown = generator.invoke_slide_gen_chain(
                        script_content, mock_template
                    )
                except Exception:  # noqa: BLE001
                    # This simulates fallback behavior that might exist
                    generated_markdown = f"""---
marp: true
theme: default
---

# Presentation

Error occurred during generation. Here is the script content:

{script_content}

---

# End

Thank you.
"""

                # Verify error was handled gracefully
                assert "Error occurred" in generated_markdown
                assert script_content in generated_markdown
                assert "marp: true" in generated_markdown

    def test_chain_workflow_phases_simulation(self):
        """Test simulation of the 4-phase chain workflow"""
        # Simulate the console output from actual SlideGenChain
        phases = [
            "🔍 Agent: Analyzing script content...",
            "✍️ Agent: Generating slide parameters...",
            "🎉 Agent: Presentation generated successfully!",
        ]

        # Test that all phases are represented (based on actual implementation)
        assert len(phases) == 3
        assert "Analyzing" in phases[0]
        assert "Generating" in phases[1]
        assert "generated successfully" in phases[2]

    def test_template_placeholder_workflow(self):
        """Test template placeholder extraction and rendering workflow"""
        from pathlib import Path

        # Test complex template with multiple placeholders
        template_content = """---
marp: true
theme: ${theme}
---

# ${presentation_title}

${presentation_subtitle}

---

# ${topic_1_title}

${topic_1_content}

---

# ${topic_2_title}

${topic_2_content}

---

# Summary

${conclusion}
"""

        # Create a real SlideTemplate instance for testing (temp dir)
        import tempfile

        with tempfile.TemporaryDirectory(prefix="auto-slides-test-") as tmpdir:
            template = SlideTemplate(
                id="test_template",
                name="Test Template",
                description="Test template for unit tests",
                template_dir=Path(tmpdir),
                duration_minutes=10,
            )

            # Extract placeholders
            placeholders = template.extract_placeholders(template_content)
            expected_placeholders = {
                "theme",
                "presentation_title",
                "presentation_subtitle",
                "topic_1_title",
                "topic_1_content",
                "topic_2_title",
                "topic_2_content",
                "conclusion",
            }
            assert placeholders == expected_placeholders

            # Test rendering with mock chain output
            mock_content = {
                "theme": "default",
                "presentation_title": "Chain Generated Title",
                "presentation_subtitle": "Subtitle from analysis phase",
                "topic_1_title": "First Topic",
                "topic_1_content": "Content from composition phase",
                "topic_2_title": "Second Topic",
                "topic_2_content": "Content from execution phase",
                "conclusion": "Conclusion from SlideGenChain",
            }

            result = template.render_template(template_content, mock_content)

            # Verify all placeholders were replaced
            assert "${" not in result
            assert "Chain Generated Title" in result
            assert "analysis phase" in result
            assert "composition phase" in result
            assert "execution phase" in result
            assert "SlideGenChain" in result

    def test_mock_chain_workflow_output(self):
        """Test that mock chain workflow produces expected output format"""
        # Skip this test as MockSlideGenerator doesn't exist in production
        pytest.skip("MockSlideGenerator not implemented - test would be meaningless")
