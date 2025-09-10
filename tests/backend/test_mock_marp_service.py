import os

import pytest

from dev.mocks.mock_marp_service import MockMarpService


@pytest.mark.parametrize(
    "output_type, generator_method_name, output_filename",
    [
        (MockMarpService.OutputFormat.PDF, "generate_pdf", "test.pdf"),
        (MockMarpService.OutputFormat.HTML, "generate_html", "test.html"),
        (MockMarpService.OutputFormat.PNG, "generate_png", "test.png"),
        (MockMarpService.OutputFormat.PPTX, "generate_pptx", "test.pptx"),
    ],
)
def test_marp_service_generation(
    sample_template_path, tmp_path, output_type, generator_method_name, output_filename
):
    """
    Tests that the MockMarpService can generate all supported output file types without calling marp CLI.
    """
    # Create a temporary output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Create MockMarpService instance with temporary directory
    marp_service = MockMarpService(
        slides_path=str(sample_template_path), output_dir=str(output_dir)
    )

    # Get the generator method from the service instance
    generator_method = getattr(marp_service, generator_method_name)

    # Call the generator method (e.g., marp_service.generate_pdf("test.pdf"))
    output_path = generator_method(output_filename)

    # 1. Check that the output path is correct and the file exists
    assert os.path.exists(output_path)
    assert os.path.basename(output_path) == output_filename

    # 2. The file should be in the service's output directory (the temp dir)
    assert str(output_dir) in output_path

    # 3. For MockMarpService, verify the mock content is written correctly
    with open(output_path, "r") as f:
        content = f.read()
        assert f"Mock {output_type.value} file generated" in content
        assert str(sample_template_path) in content


def test_mock_marp_service_with_theme(sample_template_path, tmp_path):
    """
    Tests that MockMarpService includes theme information in mock files.
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    marp_service = MockMarpService(
        slides_path=str(sample_template_path), output_dir=str(output_dir)
    )

    test_theme = "gaia"
    output_path = marp_service.generate_pdf("themed_test.pdf", theme=test_theme)

    # Check that the theme is mentioned in the mock file content
    with open(output_path, "r") as f:
        content = f.read()
        assert f"with theme: {test_theme}" in content


def test_mock_marp_service_preview(sample_template_path, tmp_path, capsys):
    """
    Tests that MockMarpService preview method works without calling marp CLI.
    """
    marp_service = MockMarpService(
        slides_path=str(sample_template_path), output_dir=str(tmp_path)
    )

    # This should not raise an exception and should print mock messages
    marp_service.preview(server=True, watch=False)

    # Capture the printed output
    captured = capsys.readouterr()
    assert "MOCK: Starting Marp preview" in captured.out
    assert "Server: True, Watch: False" in captured.out
    assert "Mock preview started successfully" in captured.out
