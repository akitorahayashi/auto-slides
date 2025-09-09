import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.models.slide_template import SlideTemplate


class TestSlideTemplate:
    """Unit tests for SlideTemplate model"""

    def test_init(self):
        """Test SlideTemplate initialization"""
        template_dir = Path("/test/template")
        template = SlideTemplate(
            id="test_template",
            name="Test Template",
            description="A test template",
            template_dir=template_dir,
            duration_minutes=10,
        )

        assert template.id == "test_template"
        assert template.name == "Test Template"
        assert template.description == "A test template"
        assert template.template_dir == template_dir

    def test_markdown_path_property(self):
        """Test markdown_path property returns correct path"""
        template_dir = Path("/test/template")
        template = SlideTemplate(
            id="test",
            name="Test",
            description="Test",
            template_dir=template_dir,
            duration_minutes=10,
        )

        expected_path = template_dir / "content.md"
        assert template.markdown_path == expected_path

    def test_css_path_property(self):
        """Test css_path property returns correct path"""
        template_dir = Path("/test/template")
        template = SlideTemplate(
            id="test",
            name="Test",
            description="Test",
            template_dir=template_dir,
            duration_minutes=10,
        )

        expected_path = template_dir / "theme.css"
        assert template.css_path == expected_path

    @patch("pathlib.Path.exists")
    def test_exists_returns_true_when_all_files_exist(self, mock_exists):
        """Test exists() returns True when all required files exist"""
        mock_exists.return_value = True

        template = SlideTemplate(
            id="test",
            name="Test",
            description="Test",
            template_dir=Path("/test/template"),
            duration_minutes=10,
        )

        result = template.exists()

        assert result is True
        assert mock_exists.call_count == 3  # template_dir, markdown_path, css_path

    @patch("pathlib.Path.exists")
    def test_exists_returns_false_when_template_dir_missing(self, mock_exists):
        """Test exists() returns False when template directory doesn't exist"""
        # Configure mock to return False on first call (template_dir), True for others
        mock_exists.side_effect = [False, True, True]

        template = SlideTemplate(
            id="test",
            name="Test",
            description="Test",
            template_dir=Path("/test/template"),
            duration_minutes=10,
        )

        result = template.exists()

        assert result is False

    @patch("pathlib.Path.exists")
    def test_exists_returns_false_when_markdown_missing(self, mock_exists):
        """Test exists() returns False when markdown file doesn't exist"""
        # Configure mock to return True, False, True (template_dir, markdown, css)
        mock_exists.side_effect = [True, False, True]

        template = SlideTemplate(
            id="test",
            name="Test",
            description="Test",
            template_dir=Path("/test/template"),
            duration_minutes=10,
        )

        result = template.exists()

        assert result is False

    @patch("pathlib.Path.exists")
    def test_exists_returns_false_when_css_missing(self, mock_exists):
        """Test exists() returns False when CSS file doesn't exist"""
        # Configure mock to return True, True, False (template_dir, markdown, css)
        mock_exists.side_effect = [True, True, False]

        template = SlideTemplate(
            id="test",
            name="Test",
            description="Test",
            template_dir=Path("/test/template"),
            duration_minutes=10,
        )

        result = template.exists()

        assert result is False

    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    def test_read_markdown_content_success(self, mock_exists, mock_read_text):
        """Test successful reading of markdown content"""
        mock_exists.return_value = True
        mock_read_text.return_value = "# Test Content"

        template = SlideTemplate(
            id="test",
            name="Test",
            description="Test",
            template_dir=Path("/test/template"),
            duration_minutes=10,
        )

        result = template.read_markdown_content()

        assert result == "# Test Content"
        mock_read_text.assert_called_once_with(encoding="utf-8")

    @patch("pathlib.Path.exists")
    def test_read_markdown_content_file_not_found(self, mock_exists):
        """Test FileNotFoundError when markdown file doesn't exist"""
        mock_exists.return_value = False

        template = SlideTemplate(
            id="test",
            name="Test",
            description="Test",
            template_dir=Path("/test/template"),
            duration_minutes=10,
        )

        with pytest.raises(FileNotFoundError) as exc_info:
            template.read_markdown_content()

        assert "Markdown file not found" in str(exc_info.value)
        assert "/test/template/content.md" in str(exc_info.value)

    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    def test_read_css_content_success(self, mock_exists, mock_read_text):
        """Test successful reading of CSS content"""
        mock_exists.return_value = True
        mock_read_text.return_value = "/* CSS content */"

        template = SlideTemplate(
            id="test",
            name="Test",
            description="Test",
            template_dir=Path("/test/template"),
            duration_minutes=10,
        )

        result = template.read_css_content()

        assert result == "/* CSS content */"
        mock_read_text.assert_called_once_with(encoding="utf-8")

    @patch("pathlib.Path.exists")
    def test_read_css_content_file_not_found(self, mock_exists):
        """Test FileNotFoundError when CSS file doesn't exist"""
        mock_exists.return_value = False

        template = SlideTemplate(
            id="test",
            name="Test",
            description="Test",
            template_dir=Path("/test/template"),
            duration_minutes=10,
        )

        with pytest.raises(FileNotFoundError) as exc_info:
            template.read_css_content()

        assert "CSS theme file not found" in str(exc_info.value)
        assert "/test/template/theme.css" in str(exc_info.value)

    def test_template_with_real_files(self):
        """Integration test with real temporary files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)

            # Create test files
            markdown_file = template_dir / "content.md"
            css_file = template_dir / "theme.css"

            markdown_content = "# Test Slide\n\nTest content"
            css_content = "body { color: blue; }"

            markdown_file.write_text(markdown_content, encoding="utf-8")
            css_file.write_text(css_content, encoding="utf-8")

            template = SlideTemplate(
                id="test",
                name="Test Template",
                description="A test template",
                template_dir=template_dir,
                duration_minutes=10,
            )

            # Test existence
            assert template.exists() is True

            # Test content reading
            assert template.read_markdown_content() == markdown_content
            assert template.read_css_content() == css_content

    def test_template_with_missing_files(self):
        """Test template behavior when files are missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)

            template = SlideTemplate(
                id="test",
                name="Test Template",
                description="A test template",
                template_dir=template_dir,
                duration_minutes=10,
            )

            # Directory exists but files don't
            assert template.exists() is False

            # Reading should raise FileNotFoundError
            with pytest.raises(FileNotFoundError):
                template.read_markdown_content()

            with pytest.raises(FileNotFoundError):
                template.read_css_content()
