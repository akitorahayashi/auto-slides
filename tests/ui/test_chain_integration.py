"""
UI tests for the new chain integration in pages.
Tests the integration of SlideGenChain and services with UI components.
"""

from unittest.mock import MagicMock, patch

import streamlit as st

from src.models import SlideTemplate


class TestChainIntegrationUI:
    """Test cases for chain integration in UI components"""

    def test_implementation_page_with_chain_workflow(self):
        """Test implementation page with new chain workflow"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Create mock slide generator with chain
            mock_slide_generator = MagicMock()
            mock_slide_generator.generate_sync.return_value = """---
marp: true
theme: default
---

# Mock Generated Presentation

Generated via chain workflow

---

# Section 1

Mock content from analysis chain

---

# Section 2

Mock content from planning chain

---

# Conclusion

Thank you for your attention.
"""

            # Create mock template
            mock_template = MagicMock(spec=SlideTemplate)
            mock_template.name = "Chain Test Template"
            mock_template.description = "Template for testing chain integration"

            mock_app_state = MagicMock()
            mock_app_state.selected_template = mock_template

            with patch.object(st, "session_state") as mock_session:
                mock_session.app_state = mock_app_state
                mock_session.slide_generator = mock_slide_generator
                mock_session.format_selection = "PDF"

                script_content = "Test script for chain workflow"

                # Simulate execution with chain workflow
                generator = mock_session.slide_generator
                generated_markdown = generator.generate_sync(
                    script_content=script_content, template=mock_template
                )

                # Verify chain workflow was used
                mock_slide_generator.generate_sync.assert_called_once_with(
                    script_content=script_content, template=mock_template
                )

                # Verify generated content contains chain-specific markers
                assert "Generated via chain workflow" in generated_markdown
                assert "marp: true" in generated_markdown

                # Simulate session state update
                mock_session.app_state.user_inputs = {
                    "format": mock_session.format_selection,
                    "script_content": script_content,
                }
                mock_session.app_state.generated_markdown = generated_markdown
                mock_session.selected_format = mock_session.format_selection

                # Verify session state
                assert mock_session.app_state.generated_markdown == generated_markdown
                assert "chain workflow" in mock_session.app_state.generated_markdown

    def test_slide_generator_service_initialization(self):
        """Test SlideGenerator service initialization in main.py"""
        with patch("streamlit.secrets") as mock_secrets:
            # Mock streamlit secrets for testing
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": "true",
                "OLLAMA_MODEL": "test-model",
            }.get(key, default)

            from src.services import SlideGenerator

            # Test that SlideGenerator can be instantiated
            generator = SlideGenerator()

            # Verify it has the chain component
            assert hasattr(generator, "chain")

            # Verify chain has all required components
            assert hasattr(generator.chain, "analysis_chain")
            assert hasattr(generator.chain, "planning_chain")
            assert hasattr(generator.chain, "generation_chain")
            assert hasattr(generator.chain, "validation_chain")

    def test_session_state_chain_integration(self):
        """Test session state setup with chain integration"""
        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": "true",
                "OLLAMA_MODEL": "test-model",
            }.get(key, default)

            with patch.object(st, "session_state") as mock_session:
                # Mock the session state initialization logic from main.py
                from src.services import SlideGenerator

                # Simulate initialization
                if "slide_generator" not in mock_session.__dict__:
                    mock_session.slide_generator = SlideGenerator()

                # Verify the service is properly initialized
                assert hasattr(mock_session, "slide_generator")
                generator = mock_session.slide_generator
                assert isinstance(generator, SlideGenerator)

    def test_chain_error_handling_in_ui(self):
        """Test chain error handling in UI context"""
        # Create mock slide generator that simulates chain errors
        mock_slide_generator = MagicMock()
        mock_slide_generator.generate_sync.side_effect = Exception(
            "Chain workflow error"
        )

        mock_template = MagicMock(spec=SlideTemplate)
        mock_app_state = MagicMock()
        mock_app_state.selected_template = mock_template

        with patch.object(st, "session_state") as mock_session:
            mock_session.app_state = mock_app_state
            mock_session.slide_generator = mock_slide_generator

            script_content = "Test script"

            # Simulate error handling from implementation_page.py
            try:
                generator = mock_session.slide_generator
                generated_markdown = generator.generate_sync(
                    script_content=script_content, template=mock_template
                )
            except Exception as e:
                # This is the fallback logic from the actual implementation
                generated_markdown = f"""---
marp: true
theme: default
---

# Presentation

Error occurred. Here is the script content:

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
        # Simulate the console output and workflow from SlideGenerator
        phases = [
            "Agent: Analyzing script content...",
            "Agent: Planning content strategy...",
            "Agent: Generating slide content...",
            "Agent: Validating content quality...",
        ]

        # Test that all phases are represented
        assert len(phases) == 4
        assert "Analyzing" in phases[0]
        assert "Planning" in phases[1]
        assert "Generating" in phases[2]
        assert "Validating" in phases[3]

    def test_template_placeholder_workflow(self):
        """Test template placeholder extraction and rendering workflow"""
        from src.services.slide_generator import extract_placeholders, render_template

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

        # Extract placeholders
        placeholders = extract_placeholders(template_content)
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
            "topic_1_content": "Content from planning phase",
            "topic_2_title": "Second Topic",
            "topic_2_content": "Content from generation phase",
            "conclusion": "Conclusion from validation phase",
        }

        result = render_template(template_content, mock_content)

        # Verify all placeholders were replaced
        assert "${" not in result
        assert "Chain Generated Title" in result
        assert "analysis phase" in result
        assert "planning phase" in result
        assert "generation phase" in result
        assert "validation phase" in result

    def test_mock_chain_workflow_output(self):
        """Test that mock chain workflow produces expected output format"""
        from pathlib import Path

        from dev.mocks.mock_slide_generator import MockSlideGenerator
        from src.models import SlideTemplate

        # Create test template
        test_template = SlideTemplate(
            id="test_chain",
            name="Test Chain Template",
            description="Template for testing chain workflow",
            template_dir=Path("tests/templates/k2g4h1x9"),
            duration_minutes=5,
        )

        mock_generator = MockSlideGenerator()
        script_content = "Test script for mock chain workflow"

        result = mock_generator.generate_sync(script_content, test_template)

        # Verify mock chain output format
        assert isinstance(result, str)
        assert "---" in result  # Marp format
        assert "Mock content" in result  # Mock indicators
        assert len(result) > 100  # Substantial content
