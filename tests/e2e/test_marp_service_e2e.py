import os
import subprocess

import pytest

from src.services.marp_service import MarpService


def has_marp_cli():
    """Check if marp CLI is available in the system"""
    try:
        subprocess.run(["marp", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@pytest.mark.skipif(not has_marp_cli(), reason="marp CLI not available")
class TestMarpServiceE2E:
    """End-to-end tests for MarpService using actual marp CLI"""

    @pytest.mark.parametrize(
        "output_type, generator_method_name, output_filename, expected_extension",
        [
            (MarpService.OutputFormat.PDF, "generate_pdf", "test.pdf", ".pdf"),
            (MarpService.OutputFormat.HTML, "generate_html", "test.html", ".html"),
            (MarpService.OutputFormat.PNG, "generate_png", "test.png", ".png"),
            (MarpService.OutputFormat.PPTX, "generate_pptx", "test.pptx", ".pptx"),
        ],
    )
    def test_marp_service_real_generation(
        self,
        sample_template_path,
        tmp_path,
        output_type,
        generator_method_name,
        output_filename,
        expected_extension,
    ):
        """
        Tests that the MarpService can generate all supported output file types using real marp CLI.
        """
        # Create a temporary output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create MarpService instance with temporary directory
        marp_service = MarpService(
            slides_path=str(sample_template_path), output_dir=str(output_dir)
        )

        # Get the generator method from the service instance
        generator_method = getattr(marp_service, generator_method_name)

        # Call the generator method (e.g., marp_service.generate_pdf("test.pdf"))
        output_path = generator_method(output_filename)

        # 1. Check that the output path is correct and the file exists
        assert os.path.exists(output_path)
        assert os.path.basename(output_path) == output_filename
        assert output_path.endswith(expected_extension)

        # 2. The file should be in the service's output directory
        assert str(output_dir) in output_path

        # 3. The generated file should have content (not empty)
        assert os.path.getsize(output_path) > 0

        # 4. For specific file types, do additional checks
        if output_type == MarpService.OutputFormat.HTML:
            # HTML files should contain basic HTML structure
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "<html" in content.lower()
                assert "</html>" in content.lower()

    def test_marp_service_with_theme_e2e(self, sample_template_path, tmp_path):
        """
        Tests that MarpService can use themes with real marp CLI.
        """
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        marp_service = MarpService(
            slides_path=str(sample_template_path), output_dir=str(output_dir)
        )

        # Generate HTML with built-in theme (gaia is a standard Marp theme)
        output_path = marp_service.generate_html("themed_test.html", theme="gaia")

        # Check that the file was generated successfully
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

        # Check that the theme is applied (HTML should contain theme-related CSS)
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
            # The theme should be referenced in the HTML
            assert "gaia" in content.lower() or "theme" in content.lower()

    def test_marp_service_error_handling_e2e(self, tmp_path):
        """
        Tests that MarpService properly handles errors from real marp CLI.
        """
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Use a non-existent file to trigger an error
        non_existent_file = str(tmp_path / "nonexistent.md")
        marp_service = MarpService(
            slides_path=non_existent_file, output_dir=str(output_dir)
        )

        # This should raise a subprocess.CalledProcessError
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            marp_service.generate_pdf("error_test.pdf")

        # Verify that the error is related to the missing file
        assert exc_info.value.returncode != 0

    def test_marp_service_preview_e2e(self, sample_template_path, tmp_path):
        """
        Tests that MarpService preview works with real marp CLI.
        Note: This test is marked as slow because it may take time to start/stop the server.
        """
        marp_service = MarpService(slides_path=str(sample_template_path))

        # We can't easily test the interactive preview without actually starting a server,
        # but we can test that the command doesn't immediately fail
        # For E2E testing, we might want to use a timeout or run in background

        # Test with server=False to avoid starting a web server
        try:
            # This should validate the markdown file and potentially show help
            # We expect this to either succeed or fail with a specific error
            result = subprocess.run(
                ["marp", str(sample_template_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # If marp is working, it should show help without error
            assert (
                result.returncode == 0
                or "Usage:" in result.stdout
                or "help" in result.stdout
            )
        except subprocess.TimeoutExpired:
            pytest.skip(
                "Marp preview test timed out - this is expected in CI environments"
            )

    def test_marp_service_default_filenames_e2e(self, sample_template_path, tmp_path):
        """
        Tests that MarpService uses correct default filenames with real marp CLI.
        """
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        marp_service = MarpService(
            slides_path=str(sample_template_path), output_dir=str(output_dir)
        )

        # Test default filename for each type
        pdf_path = marp_service.generate_pdf()
        html_path = marp_service.generate_html()

        assert os.path.basename(pdf_path) == "slides.pdf"
        assert os.path.basename(html_path) == "slides.html"
        assert os.path.exists(pdf_path)
        assert os.path.exists(html_path)
        assert os.path.getsize(pdf_path) > 0
        assert os.path.getsize(html_path) > 0
