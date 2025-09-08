import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.models import SlideTemplate
from src.schemas import OutputFormat
from src.services.template_converter_service import TemplateConverterService


class TestTemplateConverterService:
    """Unit tests for TemplateConverterService - testing logic without external dependencies"""

    @patch("tempfile.gettempdir")
    @patch("pathlib.Path.mkdir")
    def test_init(self, mock_mkdir, mock_gettempdir):
        """Test service initialization"""
        mock_gettempdir.return_value = "/tmp"

        service = TemplateConverterService()

        assert service.temp_dir == Path("/tmp/auto-slides")
        mock_mkdir.assert_called_once_with(exist_ok=True)

    @patch("subprocess.run")
    @patch("pathlib.Path.read_bytes")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.unlink")
    def test_convert_template_to_pdf_success(
        self,
        mock_unlink,
        mock_write_text,
        mock_exists,
        mock_read_bytes,
        mock_subprocess,
    ):
        """Test successful PDF conversion"""
        # Setup
        service = TemplateConverterService()
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "test_template"
        mock_template.read_markdown_content.return_value = "# Test Slide"
        mock_template.read_css_content.return_value = "/* CSS content */"

        mock_exists.return_value = True
        mock_read_bytes.return_value = b"PDF content"
        mock_subprocess.return_value = MagicMock()

        # Execute
        result = service.convert_template_to_pdf(mock_template)

        # Verify
        assert result == b"PDF content"
        mock_template.read_markdown_content.assert_called_once()
        mock_template.read_css_content.assert_called_once()
        assert mock_write_text.call_count == 2  # markdown and css files
        mock_subprocess.assert_called_once()
        assert mock_unlink.call_count == 3  # Clean up md, css, and pdf files

    @patch("subprocess.run")
    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.unlink")
    def test_convert_template_to_html_success(
        self, mock_unlink, mock_write_text, mock_exists, mock_read_text, mock_subprocess
    ):
        """Test successful HTML conversion"""
        # Setup
        service = TemplateConverterService()
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "test_template"
        mock_template.read_markdown_content.return_value = "# Test Slide"
        mock_template.read_css_content.return_value = "/* CSS content */"

        mock_exists.return_value = True
        mock_read_text.return_value = "<html>Test</html>"
        mock_subprocess.return_value = MagicMock()

        # Execute
        result = service.convert_template_to_html(mock_template)

        # Verify
        assert result == "<html>Test</html>"
        mock_template.read_markdown_content.assert_called_once()
        mock_template.read_css_content.assert_called_once()
        mock_read_text.assert_called_once_with(encoding="utf-8")
        assert mock_write_text.call_count == 2  # markdown and css files
        assert mock_unlink.call_count == 3  # Clean up md, css, and html files

    @patch("subprocess.run")
    @patch("pathlib.Path.read_bytes")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.unlink")
    def test_convert_template_to_pptx_success(
        self,
        mock_unlink,
        mock_write_text,
        mock_exists,
        mock_read_bytes,
        mock_subprocess,
    ):
        """Test successful PPTX conversion"""
        # Setup
        service = TemplateConverterService()
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "test_template"
        mock_template.read_markdown_content.return_value = "# Test Slide"
        mock_template.read_css_content.return_value = "/* CSS content */"

        mock_exists.return_value = True
        mock_read_bytes.return_value = b"PPTX content"
        mock_subprocess.return_value = MagicMock()

        # Execute
        result = service.convert_template_to_pptx(mock_template)

        # Verify
        assert result == b"PPTX content"
        mock_template.read_markdown_content.assert_called_once()
        mock_template.read_css_content.assert_called_once()
        assert mock_write_text.call_count == 2  # markdown and css files
        assert mock_unlink.call_count == 3  # Clean up md, css, and pptx files

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.unlink")
    @patch("pathlib.Path.write_text")
    @patch("subprocess.run")
    def test_convert_to_pdf_subprocess_error(
        self, mock_subprocess, mock_write_text, mock_unlink, mock_exists
    ):
        """Test PDF conversion handles subprocess errors"""
        # Setup
        service = TemplateConverterService()
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "test_template"
        mock_template.read_markdown_content.return_value = "# Test Slide"
        mock_template.read_css_content.return_value = "/* CSS content */"

        error = subprocess.CalledProcessError(1, "marp")
        error.stderr = "Marp failed"
        mock_subprocess.side_effect = error

        # Execute & Verify
        with pytest.raises(Exception, match="Marp PDF generation failed: Marp failed"):
            service.convert_template_to_pdf(mock_template)

        # Cleanup should happen (2 files: md and css)
        assert mock_unlink.call_count >= 2

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.unlink")
    def test_convert_to_pdf_file_not_exists(
        self, mock_unlink, mock_write_text, mock_exists, mock_subprocess
    ):
        """Test PDF conversion when output file doesn't exist"""
        # Setup
        service = TemplateConverterService()
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "test_template"
        mock_template.read_markdown_content.return_value = "# Test Slide"
        mock_template.read_css_content.return_value = "/* CSS content */"

        mock_exists.return_value = False
        mock_subprocess.return_value = MagicMock()

        # Execute & Verify
        with pytest.raises(Exception, match="PDF generation failed"):
            service.convert_template_to_pdf(mock_template)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.unlink")
    def test_convert_to_html_file_not_exists(
        self, mock_unlink, mock_write_text, mock_exists, mock_subprocess
    ):
        """Test HTML conversion when output file doesn't exist"""
        # Setup
        service = TemplateConverterService()
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "test_template"
        mock_template.read_markdown_content.return_value = "# Test Slide"
        mock_template.read_css_content.return_value = "/* CSS content */"

        mock_exists.return_value = False
        mock_subprocess.return_value = MagicMock()

        # Execute & Verify
        with pytest.raises(Exception, match="HTML generation failed"):
            service.convert_template_to_html(mock_template)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.unlink")
    def test_convert_to_pptx_file_not_exists(
        self, mock_unlink, mock_write_text, mock_exists, mock_subprocess
    ):
        """Test PPTX conversion when output file doesn't exist"""
        # Setup
        service = TemplateConverterService()
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "test_template"
        mock_template.read_markdown_content.return_value = "# Test Slide"
        mock_template.read_css_content.return_value = "/* CSS content */"

        mock_exists.return_value = False
        mock_subprocess.return_value = MagicMock()

        # Execute & Verify
        with pytest.raises(Exception, match="PPTX generation failed"):
            service.convert_template_to_pptx(mock_template)

    @pytest.mark.parametrize(
        "format_enum,expected_extension",
        [
            (OutputFormat.PDF, "pdf"),
            (OutputFormat.HTML, "html"),
            (OutputFormat.PPTX, "pptx"),
        ],
    )
    def test_get_filename(self, format_enum, expected_extension):
        """Test filename generation for different formats"""
        service = TemplateConverterService()
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "test_template"

        result = service.get_filename(mock_template, format_enum)

        assert result == f"test_template.{expected_extension}"

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.unlink")
    @patch("pathlib.Path.write_text")
    @patch("subprocess.run")
    def test_cleanup_always_called(
        self, mock_subprocess, mock_write_text, mock_unlink, mock_exists
    ):
        """Test that cleanup (unlink) is always called even when exceptions occur"""
        # Setup
        service = TemplateConverterService()
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "test_template"
        mock_template.read_markdown_content.return_value = "# Test Slide"
        mock_template.read_css_content.return_value = "/* CSS content */"

        mock_subprocess.side_effect = Exception("Some error")

        # Execute & Verify
        with pytest.raises(Exception):
            service.convert_template_to_pdf(mock_template)

        # Cleanup should be called (at least for markdown and css files)
        assert mock_unlink.call_count >= 2
