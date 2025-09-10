"""Tests for JsonParser"""

import pytest

from src.services.json_parser import JsonParser


class TestJsonParser:
    """Test JsonParser functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.parser = JsonParser()

    def test_parse_valid_json(self):
        """Test parsing valid JSON"""
        json_text = '{"key": "value", "number": 42}'
        result = self.parser.parse(json_text)
        expected = {"key": "value", "number": 42}
        assert result == expected

    def test_parse_json_with_whitespace(self):
        """Test parsing JSON with extra whitespace"""
        json_text = '  {"key": "value"}  '
        result = self.parser.parse(json_text)
        expected = {"key": "value"}
        assert result == expected

    def test_parse_json_with_thinking_tags(self):
        """Test parsing JSON from text containing thinking tags"""
        text_with_json = """
        <think>
        I need to generate a JSON response
        </think>
        
        {"result": "success", "data": [1, 2, 3]}
        
        Some additional text here.
        """
        result = self.parser.parse(text_with_json)
        expected = {"result": "success", "data": [1, 2, 3]}
        assert result == expected

    def test_parse_json_from_mixed_content(self):
        """Test extracting JSON from text with mixed content"""
        mixed_text = """
        Here is some explanation text.
        
        The JSON response is:
        {"status": "ok", "message": "Hello World"}
        
        And here's more text after the JSON.
        """
        result = self.parser.parse(mixed_text)
        expected = {"status": "ok", "message": "Hello World"}
        assert result == expected

    def test_parse_nested_json(self):
        """Test parsing nested JSON objects"""
        nested_json = (
            '{"outer": {"inner": {"value": "test"}}, "array": [1, 2, {"nested": true}]}'
        )
        result = self.parser.parse(nested_json)
        expected = {
            "outer": {"inner": {"value": "test"}},
            "array": [1, 2, {"nested": True}],
        }
        assert result == expected

    def test_parse_multiple_json_objects(self):
        """Test that parser picks the first valid JSON when multiple exist"""
        text_with_multiple = """
        {"first": "json"}
        
        Some text in between
        
        {"second": "json"}
        """
        result = self.parser.parse(text_with_multiple)
        expected = {"first": "json"}
        assert result == expected

    def test_parse_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError"""
        invalid_text = "This is not JSON at all"
        with pytest.raises(ValueError, match="Could not extract valid JSON"):
            self.parser.parse(invalid_text)

    def test_parse_incomplete_json_raises_error(self):
        """Test that incomplete JSON raises ValueError"""
        # Test with text that has partial JSON that cannot be extracted as valid JSON
        incomplete_json = 'Some text {"key": "value", "incomplete":'
        with pytest.raises(ValueError, match="Could not extract valid JSON"):
            self.parser.parse(incomplete_json)

    def test_parse_empty_string(self):
        """Test parsing empty string"""
        with pytest.raises(ValueError, match="Could not extract valid JSON"):
            self.parser.parse("")

    def test_parse_json_with_unicode(self):
        """Test parsing JSON with unicode characters"""
        unicode_json = '{"message": "こんにちは", "emoji": "🎉"}'
        result = self.parser.parse(unicode_json)
        expected = {"message": "こんにちは", "emoji": "🎉"}
        assert result == expected

    def test_extract_json_from_code_block(self):
        """Test extracting JSON from markdown code block"""
        markdown_text = """
        Here's the response:
        
        ```json
        {"api_key": "secret", "enabled": true}
        ```
        """
        result = self.parser.parse(markdown_text)
        expected = {"api_key": "secret", "enabled": True}
        assert result == expected
