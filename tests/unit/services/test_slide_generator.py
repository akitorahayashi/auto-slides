from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models import SlideTemplate
from src.services import SlideGenerator, extract_placeholders


class TestSlideGenerator:
    """Unit tests for SlideGenerator with LangChain chains"""

    def test_slide_generator_initialization(self):
        """Test SlideGenerator initializes with LangChain chain"""
        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.return_value = "false"  # Ensure debug mode is off
            generator = SlideGenerator()
            assert generator.chain is not None
            assert hasattr(generator, "generate_slide")
            assert hasattr(generator, "generate_sync")

    @pytest.fixture
    def mock_template(self):
        """Create a mock SlideTemplate for testing"""
        template = MagicMock(spec=SlideTemplate)
        template.id = "test_template"
        template.name = "Test Template"
        template.description = "Test template for unit tests"
        template.duration_minutes = 10
        template.read_markdown_content.return_value = (
            "# ${title}\n\n${content}\n\n## ${author}"
        )
        return template

    @pytest.mark.asyncio
    async def test_generate_slide_success(self, mock_template):
        """Test successful slide generation with mocked chains"""
        script_content = "This is a test presentation about AI technology."

        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.return_value = "false"  # Ensure debug mode is off
            generator = SlideGenerator()

        # Mock all chain operations
        with (
            patch.object(generator.chain, "analysis_chain") as mock_analysis,
            patch.object(generator.chain, "planning_chain") as mock_planning,
            patch.object(generator.chain, "generation_chain") as mock_generation,
            patch.object(generator.chain, "validation_chain") as mock_validation,
        ):

            # Setup mock returns for each chain stage
            mock_analysis.ainvoke = AsyncMock(
                return_value={
                    "main_theme": "AI Technology",
                    "key_points": ["Machine Learning", "Deep Learning"],
                }
            )
            mock_planning.ainvoke = AsyncMock(
                return_value={
                    "generation_strategy": "Educational presentation approach"
                }
            )
            mock_generation.ainvoke = AsyncMock(
                return_value={
                    "title": "AI Technology Overview",
                    "content": "Comprehensive guide to AI technology",
                    "author": "Test Author",
                }
            )
            mock_validation.ainvoke = AsyncMock(
                return_value={"approved": True, "quality_score": 0.9}
            )

            result = await generator.generate_slide(script_content, mock_template)

            # Should return rendered template with generated content
            assert isinstance(result, str)
            assert len(result) > 0

            # Verify all chains were called
            mock_analysis.ainvoke.assert_called_once()
            mock_planning.ainvoke.assert_called_once()
            mock_generation.ainvoke.assert_called_once()
            mock_validation.ainvoke.assert_called_once()

    def test_generate_sync_method(self, mock_template):
        """Test synchronous generate method wraps async method"""
        script_content = "Test content"

        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.return_value = "false"  # Ensure debug mode is off
            generator = SlideGenerator()

        with patch.object(generator, "generate_slide") as mock_async:
            with patch("asyncio.run") as mock_run:
                mock_run.return_value = "Generated slide content"

                result = generator.generate_sync(script_content, mock_template)

                assert result == "Generated slide content"
                mock_run.assert_called_once()


class TestExtractPlaceholders:
    """Tests for the extract_placeholders utility function"""

    def test_extract_placeholders_basic(self):
        """Test extracting basic placeholders"""
        content = "Hello ${name}, welcome to ${event}!"
        placeholders = extract_placeholders(content)

        assert placeholders == {"name", "event"}

    def test_extract_placeholders_empty(self):
        """Test extracting from content with no placeholders"""
        content = "Hello world, no placeholders here!"
        placeholders = extract_placeholders(content)

        assert placeholders == set()

    def test_extract_placeholders_duplicate(self):
        """Test that duplicate placeholders are deduplicated"""
        content = "${name} loves ${name} and ${name} again!"
        placeholders = extract_placeholders(content)

        assert placeholders == {"name"}

    def test_extract_placeholders_complex(self):
        """Test extracting complex placeholders"""
        content = """
        # ${presentation_title}
        
        By: ${author_name}
        Date: ${presentation_date}
        
        ## Topic 1: ${topic_1_title}
        ${topic_1_content}
        
        ## Topic 2: ${topic_2_title}  
        ${topic_2_content}
        """
        placeholders = extract_placeholders(content)

        expected = {
            "presentation_title",
            "author_name",
            "presentation_date",
            "topic_1_title",
            "topic_1_content",
            "topic_2_title",
            "topic_2_content",
        }
        assert placeholders == expected
