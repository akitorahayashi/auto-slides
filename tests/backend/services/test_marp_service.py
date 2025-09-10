"""Tests for MarpService"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.backend.services import MarpService
from src.protocols.schemas import OutputFormat


class TestMarpService:
    """Test MarpService functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary files for testing
        self.temp_dir = tempfile.mkdtemp()
        self.slides_file = Path(self.temp_dir) / "test_slides.md"
        self.slides_file.write_text("# Test Slide\n\nContent")
        self.output_dir = Path(self.temp_dir) / "output"

    def teardown_method(self):
        """Clean up test files"""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_init_creates_output_dir(self):
        """Test that initialization creates output directory"""
        service = MarpService(str(self.slides_file), str(self.output_dir))
        assert self.output_dir.exists()
        assert service.slides_path == str(self.slides_file)
        assert service.output_dir == str(self.output_dir)

    def test_init_without_output_dir(self):
        """Test initialization without output directory"""
        service = MarpService(str(self.slides_file))
        assert service.slides_path == str(self.slides_file)
        assert service.output_dir is None

    @pytest.mark.parametrize(
        "output_format, method_name, output_filename",
        [
            (OutputFormat.PDF, "generate_pdf", "test.pdf"),
            (OutputFormat.HTML, "generate_html", "test.html"),
            (OutputFormat.PNG, "generate_png", "test.png"),
            (OutputFormat.PPTX, "generate_pptx", "test.pptx"),
        ],
    )
    @patch("subprocess.run")
    def test_generate_success(
        self, mock_run, output_format, method_name, output_filename
    ):
        """Test successful generation for all formats"""
        mock_run.return_value = Mock(stdout="Success", stderr="")

        service = MarpService(str(self.slides_file), str(self.output_dir))
        generator_method = getattr(service, method_name)
        result = generator_method(output_filename)

        expected_path = str(self.output_dir / output_filename)
        assert result == expected_path

        mock_run.assert_called_once_with(
            ["marp", str(self.slides_file), "-o", expected_path],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("subprocess.run")
    def test_generate_with_theme(self, mock_run):
        """Test generation with custom theme"""
        mock_run.return_value = Mock(stdout="Success", stderr="")

        service = MarpService(str(self.slides_file), str(self.output_dir))
        result = service.generate_pdf("test.pdf", theme="custom_theme.css")

        expected_path = str(self.output_dir / "test.pdf")
        assert result == expected_path

        mock_run.assert_called_once_with(
            [
                "marp",
                str(self.slides_file),
                "-o",
                expected_path,
                "--theme",
                "custom_theme.css",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_generate_without_output_dir_raises_error(self):
        """Test that generation without output directory raises error"""
        service = MarpService(str(self.slides_file))

        with pytest.raises(ValueError, match="Output directory must be set"):
            service.generate_pdf("test.pdf")

    @patch("subprocess.run")
    def test_generate_subprocess_error(self, mock_run):
        """Test handling of subprocess errors during generation"""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["marp"], stderr="Marp error"
        )

        service = MarpService(str(self.slides_file), str(self.output_dir))

        with pytest.raises(subprocess.CalledProcessError):
            service.generate_pdf("test.pdf")

    @patch("subprocess.run")
    def test_preview_default_options(self, mock_run):
        """Test preview with default options"""
        service = MarpService(str(self.slides_file), str(self.output_dir))
        service.preview()

        mock_run.assert_called_once_with(
            ["marp", str(self.slides_file), "-s", "-w"], check=True
        )

    @patch("subprocess.run")
    def test_preview_custom_options(self, mock_run):
        """Test preview with custom options"""
        service = MarpService(str(self.slides_file), str(self.output_dir))
        service.preview(server=False, watch=False)

        mock_run.assert_called_once_with(["marp", str(self.slides_file)], check=True)

    @patch("subprocess.run")
    def test_preview_subprocess_error(self, mock_run):
        """Test handling of subprocess errors during preview"""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["marp"], stderr="Preview error"
        )

        service = MarpService(str(self.slides_file), str(self.output_dir))

        with pytest.raises(subprocess.CalledProcessError):
            service.preview()

    @patch("subprocess.run")
    def test_preview_keyboard_interrupt(self, mock_run):
        """Test handling of KeyboardInterrupt during preview"""
        mock_run.side_effect = KeyboardInterrupt()

        service = MarpService(str(self.slides_file), str(self.output_dir))

        # Should not raise exception, just log and return
        service.preview()

    def test_output_format_enum_access(self):
        """Test that OutputFormat enum is accessible through service"""
        service = MarpService(str(self.slides_file))
        assert service.OutputFormat.PDF == OutputFormat.PDF
        assert service.OutputFormat.HTML == OutputFormat.HTML
        assert service.OutputFormat.PNG == OutputFormat.PNG
        assert service.OutputFormat.PPTX == OutputFormat.PPTX
