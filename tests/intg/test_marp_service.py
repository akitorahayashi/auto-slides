import os

import pytest

from src.services.marp_service import MarpService


@pytest.mark.parametrize(
    "output_type, generator_method_name, output_filename",
    [
        (MarpService.OutputType.PDF, "generate_pdf", "test.pdf"),
        (MarpService.OutputType.HTML, "generate_html", "test.html"),
        (MarpService.OutputType.PNG, "generate_png", "test.png"),
        (MarpService.OutputType.PPTX, "generate_pptx", "test.pptx"),
    ],
)
def test_marp_service_generation(
    sample_template_path, tmp_path, output_type, generator_method_name, output_filename
):
    """
    Tests that the MarpService can generate all supported output file types.
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

    # 2. The file should be in the service's output directory (the temp dir)
    assert str(output_dir) in output_path
