import os

import pytest

from src.services.marp_service import MarpService


@pytest.fixture
def marp_service(tmp_path):
    """
    Pytest fixture to create a MarpService instance with a temporary output directory.
    """
    # tmp_path is a Path object provided by pytest
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # The slides_path is constant
    slides_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "src",
            "templates",
            "sample",
            "content.md",
        )
    )

    service = MarpService(slides_path=slides_path, output_dir=str(output_dir))
    return service


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
    marp_service, output_type, generator_method_name, output_filename
):
    """
    Tests that the MarpService can generate all supported output file types.
    """
    # Get the generator method from the service instance
    generator_method = getattr(marp_service, generator_method_name)

    # Call the generator method (e.g., marp_service.generate_pdf("test.pdf"))
    output_path = generator_method(output_filename)

    # 1. Check that the output path is correct and the file exists
    assert os.path.exists(output_path)
    assert os.path.basename(output_path) == output_filename

    # 2. The file should be in the service's output directory (the temp dir)
    assert marp_service.output_dir in output_path
