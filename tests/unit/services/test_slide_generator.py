import pytest

from src.services.slide_generator import SlideGenerator


class TestSlideGenerator:
    """Unit tests for SlideGenerator methods"""

    def test_fill_template_success(self, mock_slide_generator):
        """Test successful placeholder substitution"""
        template_content = "# ${title}\n\nAuthor: ${author}\nDate: ${date}"
        data = {
            "title": "Test Presentation",
            "author": "John Doe",
            "date": "2025-09-08",
        }
        result = mock_slide_generator._fill_template(template_content, data)
        expected = "# Test Presentation\n\nAuthor: John Doe\nDate: 2025-09-08"
        assert result == expected

    def test_fill_template_missing_key(self, mock_slide_generator):
        """Test that missing placeholders are left as is"""
        template_content = "# ${title}\n\nAuthor: ${author}\nMissing: ${missing_key}"
        data = {
            "title": "Test Presentation",
            "author": "John Doe",
        }
        result = mock_slide_generator._fill_template(template_content, data)
        # safe_substitute will leave the missing placeholder
        expected = "# Test Presentation\n\nAuthor: John Doe\nMissing: ${missing_key}"
        assert result == expected

    def test_fill_template_with_generated_content_key(self, mock_slide_generator):
        """Test that it uses the 'generated_content' dictionary if present"""
        template_content = "# ${title}"
        data = {"generated_content": {"title": "My Title"}, "other_key": "some_value"}
        result = mock_slide_generator._fill_template(template_content, data)
        assert result == "# My Title"

    def test_ensure_placeholder_defaults_known(self, mock_slide_generator):
        """Test that known placeholders get default values"""
        data = {"topic_1": "My Topic"}
        result = mock_slide_generator._ensure_placeholder_defaults(data)
        assert result["topic_1"] == "My Topic"
        assert result["presentation_title"] == "Title"

    def test_ensure_placeholder_defaults_unknown(self, mock_slide_generator):
        """Test that unknown placeholders are added"""
        data = {"new_field": "new_value"}
        result = mock_slide_generator._ensure_placeholder_defaults(data)
        assert result["new_field"] == "new_value"
        assert result["presentation_title"] == "Title"

    def test_ensure_placeholder_defaults_non_string(self, mock_slide_generator):
        """Test that non-string values are converted to strings"""
        data = {"number": 123}
        result = mock_slide_generator._ensure_placeholder_defaults(data)
        assert result["number"] == "123"
