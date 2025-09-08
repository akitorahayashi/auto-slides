import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.models.slide_template import SlideTemplate
from src.services.placeholder_service import PlaceholderService


class TestPlaceholderService:
    """Unit tests for PlaceholderService"""

    def test_init(self):
        """Test PlaceholderService initialization"""
        service = PlaceholderService()
        assert service is not None

    def test_fill_placeholders_success(self):
        """Test successful placeholder substitution"""
        service = PlaceholderService()

        # Create mock template
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.read_markdown_content.return_value = (
            "# ${title}\n\n" "Author: ${author}\n" "Date: ${date}"
        )

        data = {
            "title": "Test Presentation",
            "author": "John Doe",
            "date": "2025-09-08",
        }

        result = service.fill_placeholders(mock_template, data)

        expected = "# Test Presentation\n\n" "Author: John Doe\n" "Date: 2025-09-08"

        assert result == expected
        mock_template.read_markdown_content.assert_called_once()

    def test_fill_placeholders_missing_key_error(self):
        """Test ValueError when required placeholder is missing"""
        service = PlaceholderService()

        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.read_markdown_content.return_value = (
            "# ${title}\n\n" "Author: ${author}\n" "Missing: ${missing_key}"
        )

        data = {
            "title": "Test Presentation",
            "author": "John Doe",
            # "missing_key" is not provided
        }

        with pytest.raises(ValueError) as exc_info:
            service.fill_placeholders(mock_template, data)

        assert "必要なplaceholder 'missing_key' が見つかりません" in str(exc_info.value)

    def test_fill_placeholders_template_error(self):
        """Test ValueError when template substitution fails"""
        service = PlaceholderService()

        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.read_markdown_content.return_value = "# ${invalid syntax"

        data = {"test": "value"}

        with pytest.raises(ValueError) as exc_info:
            service.fill_placeholders(mock_template, data)

        assert "テンプレート置換エラー" in str(exc_info.value)

    def test_fill_placeholders_with_complex_content(self):
        """Test placeholder substitution with complex markdown content"""
        service = PlaceholderService()

        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.read_markdown_content.return_value = """---
marp: true
theme: ${theme}
---

# ${presentation_title}

## ${section_1}

${content_1}

```python
${code_example}
```

Math: ${math_formula}
"""

        data = {
            "theme": "custom-theme",
            "presentation_title": "AI Technology",
            "section_1": "Introduction",
            "content_1": "Welcome to our presentation",
            "code_example": "print('Hello, World!')",
            "math_formula": "$f(x) = x^2$",
        }

        result = service.fill_placeholders(mock_template, data)

        expected = """---
marp: true
theme: custom-theme
---

# AI Technology

## Introduction

Welcome to our presentation

```python
print('Hello, World!')
```

Math: $f(x) = x^2$
"""

        assert result == expected

    def test_get_placeholder_names_simple(self):
        """Test extracting placeholder names from simple template"""
        service = PlaceholderService()

        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.read_markdown_content.return_value = (
            "# ${title}\n\n" "Author: ${author}\n" "Date: ${date}"
        )

        result = service.get_placeholder_names(mock_template)

        # Should return unique placeholder names
        expected = {"title", "author", "date"}
        assert set(result) == expected

    def test_get_placeholder_names_duplicates_removed(self):
        """Test that duplicate placeholder names are removed"""
        service = PlaceholderService()

        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.read_markdown_content.return_value = (
            "# ${title}\n\n" "First ${title}\n" "Second ${title}\n" "Author: ${author}"
        )

        result = service.get_placeholder_names(mock_template)

        # Should return unique placeholder names
        expected = {"title", "author"}
        assert set(result) == expected
        assert len(result) == 2  # No duplicates

    def test_get_placeholder_names_complex_patterns(self):
        """Test extracting placeholder names with complex patterns"""
        service = PlaceholderService()

        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.read_markdown_content.return_value = """
# ${presentation_title}

## ${topic_1}
${topic_1_content}

Code: ${code_example}
Math: ${inline_math} and ${block_math}

Footer: © ${company_name}
"""

        result = service.get_placeholder_names(mock_template)

        expected = {
            "presentation_title",
            "topic_1",
            "topic_1_content",
            "code_example",
            "inline_math",
            "block_math",
            "company_name",
        }
        assert set(result) == expected

    def test_get_placeholder_names_no_placeholders(self):
        """Test with template that has no placeholders"""
        service = PlaceholderService()

        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.read_markdown_content.return_value = (
            "# Static Title\n\n" "This is static content with no placeholders."
        )

        result = service.get_placeholder_names(mock_template)

        assert result == []

    def test_get_placeholder_names_edge_cases(self):
        """Test placeholder extraction with edge cases"""
        service = PlaceholderService()

        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.read_markdown_content.return_value = (
            "Normal ${placeholder}\n"
            "With numbers ${placeholder_123}\n"
            "With underscores ${my_long_placeholder_name}\n"
            "Invalid $placeholder (no braces)\n"
            "Invalid ${} (empty)\n"
            "Nested ${outer_${inner}} (not supported but should handle gracefully)"
        )

        result = service.get_placeholder_names(mock_template)

        # Should extract valid placeholders
        expected_placeholders = {
            "placeholder",
            "placeholder_123",
            "my_long_placeholder_name",
        }
        assert expected_placeholders.issubset(set(result))

    def test_create_mock_data_with_known_placeholders(self):
        """Test mock data creation with known placeholder names"""
        service = PlaceholderService()

        placeholder_names = [
            "presentation_title",
            "author_name",
            "company_name",
            "topic_1",
            "code_example",
        ]

        result = service.create_mock_data(placeholder_names)

        # All requested placeholders should be present
        for name in placeholder_names:
            assert name in result
            assert isinstance(result[name], str)
            assert len(result[name]) > 0

        # Check specific known values
        assert result["presentation_title"] == "AI技術の現状と未来"
        assert result["author_name"] == "山田太郎"
        assert result["company_name"] == "テック株式会社"

    def test_create_mock_data_with_unknown_placeholders(self):
        """Test mock data creation with unknown placeholder names"""
        service = PlaceholderService()

        placeholder_names = [
            "unknown_placeholder_1",
            "some_custom_field",
            "another_unknown",
        ]

        result = service.create_mock_data(placeholder_names)

        # All requested placeholders should be present with default values
        for name in placeholder_names:
            assert name in result
            assert result[name] == f"[{name}のサンプル内容]"

    def test_create_mock_data_mixed_known_unknown(self):
        """Test mock data creation with mix of known and unknown placeholders"""
        service = PlaceholderService()

        placeholder_names = [
            "presentation_title",  # known
            "unknown_field",  # unknown
            "author_name",  # known
            "custom_placeholder",  # unknown
        ]

        result = service.create_mock_data(placeholder_names)

        # Known placeholders should have specific values
        assert result["presentation_title"] == "AI技術の現状と未来"
        assert result["author_name"] == "山田太郎"

        # Unknown placeholders should have default values
        assert result["unknown_field"] == "[unknown_fieldのサンプル内容]"
        assert result["custom_placeholder"] == "[custom_placeholderのサンプル内容]"

    def test_create_mock_data_empty_list(self):
        """Test mock data creation with empty placeholder list"""
        service = PlaceholderService()

        result = service.create_mock_data([])

        assert result == {}

    def test_integration_full_workflow(self):
        """Integration test of the full placeholder workflow"""
        service = PlaceholderService()

        # Create a real template with actual content
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            markdown_file = template_dir / "content.md"
            css_file = template_dir / "theme.css"

            # Create test content with placeholders
            markdown_content = """# ${presentation_title}

Author: ${author_name}
Date: ${presentation_date}

## ${topic_1}
${topic_1_content}

## Code Example
```python
${code_example}
```
"""
            css_content = "body { color: blue; }"

            markdown_file.write_text(markdown_content, encoding="utf-8")
            css_file.write_text(css_content, encoding="utf-8")

            template = SlideTemplate(
                id="test",
                name="Test Template",
                description="Test",
                template_dir=template_dir,
            )

            # Test the full workflow
            # 1. Extract placeholder names
            placeholder_names = service.get_placeholder_names(template)
            expected_names = {
                "presentation_title",
                "author_name",
                "presentation_date",
                "topic_1",
                "topic_1_content",
                "code_example",
            }
            assert set(placeholder_names) == expected_names

            # 2. Create mock data
            mock_data = service.create_mock_data(placeholder_names)
            assert len(mock_data) == len(placeholder_names)

            # 3. Fill placeholders
            result = service.fill_placeholders(template, mock_data)

            # Verify no placeholders remain
            import re

            remaining_placeholders = re.findall(r"\$\{([^}]+)\}", result)
            assert len(remaining_placeholders) == 0

            # Verify content was substituted
            assert "AI技術の現状と未来" in result  # presentation_title
            assert "山田太郎" in result  # author_name
