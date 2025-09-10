import subprocess
from unittest.mock import MagicMock, patch

import pytest

from src.schemas import OutputFormat
from src.services import MarpService


class TestMarpService:
    """Unit tests for MarpService - testing logic without external dependencies"""

    def test_init_without_output_dir(self):
        """Test initialization without output directory"""
        service = MarpService(slides_path="test.md")
        assert service.slides_path == "test.md"
        assert service.output_dir is None

    @patch("os.makedirs")
    def test_init_with_output_dir(self, mock_makedirs):
        """Test initialization with output directory"""
        service = MarpService(slides_path="test.md", output_dir="/output")
        assert service.slides_path == "test.md"
        assert service.output_dir == "/output"
        mock_makedirs.assert_called_once_with("/output", exist_ok=True)

    def test_output_type_enum_access(self):
        """Test that OutputFormat enum is accessible through service"""
        assert MarpService.OutputFormat.PDF == OutputFormat.PDF
        assert MarpService.OutputFormat.HTML == OutputFormat.HTML
        assert MarpService.OutputFormat.PNG == OutputFormat.PNG
        assert MarpService.OutputFormat.PPTX == OutputFormat.PPTX

    @patch("os.makedirs")
    @patch("subprocess.run")
    def test_generate_pdf_success(self, mock_subprocess, mock_makedirs):
        """Test successful PDF generation"""
        # Setup
        service = MarpService(slides_path="test.md", output_dir="/output")
        mock_subprocess.return_value = MagicMock(stdout="Success")

        # Execute
        result = service.generate_pdf("test.pdf")

        # Verify
        assert result == "/output/test.pdf"
        mock_subprocess.assert_called_once_with(
            ["marp", "test.md", "-o", "/output/test.pdf"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("os.makedirs")
    @patch("subprocess.run")
    def test_generate_html_with_theme(self, mock_subprocess, mock_makedirs):
        """Test HTML generation with theme"""
        service = MarpService(slides_path="test.md", output_dir="/output")
        mock_subprocess.return_value = MagicMock(stdout="Success")

        result = service.generate_html("test.html", theme="custom")

        assert result == "/output/test.html"
        mock_subprocess.assert_called_once_with(
            ["marp", "test.md", "-o", "/output/test.html", "--theme", "custom"],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_generate_without_output_dir_raises_error(self):
        """Test that generation fails when no output directory is set"""
        service = MarpService(slides_path="test.md")

        with pytest.raises(ValueError, match="Output directory must be set"):
            service.generate_pdf()

    @patch("os.makedirs")
    @patch("subprocess.run")
    def test_generate_subprocess_error(self, mock_subprocess, mock_makedirs):
        """Test handling of subprocess errors during generation"""
        service = MarpService(slides_path="test.md", output_dir="/output")

        # Setup subprocess to raise CalledProcessError
        error = subprocess.CalledProcessError(1, "marp")
        error.stderr = "Marp command failed"
        mock_subprocess.side_effect = error

        with pytest.raises(subprocess.CalledProcessError):
            service.generate_pdf("test.pdf")

    @pytest.mark.parametrize(
        "method,output_type,default_filename",
        [
            ("generate_pdf", OutputFormat.PDF, "slides.pdf"),
            ("generate_html", OutputFormat.HTML, "slides.html"),
            ("generate_png", OutputFormat.PNG, "slides.png"),
            ("generate_pptx", OutputFormat.PPTX, "slides.pptx"),
        ],
    )
    @patch("os.makedirs")
    @patch("subprocess.run")
    def test_all_generation_methods(
        self, mock_subprocess, mock_makedirs, method, output_type, default_filename
    ):
        """Test all generation methods use correct parameters"""
        service = MarpService(slides_path="test.md", output_dir="/output")
        mock_subprocess.return_value = MagicMock(stdout="Success")

        # Call the method
        generator_method = getattr(service, method)
        result = generator_method()

        # Verify
        assert result == f"/output/{default_filename}"

    @patch("subprocess.run")
    def test_preview_default_options(self, mock_subprocess):
        """Test preview with default options"""
        service = MarpService(slides_path="test.md")

        service.preview()

        mock_subprocess.assert_called_once_with(
            ["marp", "test.md", "-s", "-w"], check=True
        )

    @patch("subprocess.run")
    def test_preview_custom_options(self, mock_subprocess):
        """Test preview with custom options"""
        service = MarpService(slides_path="test.md")

        service.preview(server=False, watch=False)

        mock_subprocess.assert_called_once_with(["marp", "test.md"], check=True)

    @patch("subprocess.run")
    def test_preview_subprocess_error(self, mock_subprocess):
        """Test preview handles subprocess errors"""
        service = MarpService(slides_path="test.md")
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "marp")

        with pytest.raises(subprocess.CalledProcessError):
            service.preview()

    @patch("subprocess.run")
    def test_preview_keyboard_interrupt(self, mock_subprocess):
        """Test preview handles keyboard interrupt gracefully"""
        service = MarpService(slides_path="test.md")
        mock_subprocess.side_effect = KeyboardInterrupt()

        # Should not raise, just print message
        service.preview()
