import tempfile
from pathlib import Path

import pytest

from src.models.slide_template import SlideTemplate
from src.services.marp_service import MarpService
from src.services.template_converter_service import TemplateConverterService


@pytest.fixture
def project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_template_path(project_root):
    """Path to the sample template content.md"""
    return project_root / "src" / "templates" / "sample" / "content.md"


@pytest.fixture
def sample_template(sample_template_path):
    """Sample SlideTemplate instance using the actual sample content"""
    return SlideTemplate(
        id="sample",
        name="Sample Template",
        description="Sample template for testing",
        template_dir=sample_template_path.parent,
    )


@pytest.fixture
def temp_output_dir():
    """Temporary directory for test outputs"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def marp_service(sample_template_path, temp_output_dir):
    """MarpService instance configured with sample template and temp output"""
    return MarpService(
        slides_path=str(sample_template_path), output_dir=temp_output_dir
    )


@pytest.fixture
def template_converter_service():
    """TemplateConverterService instance for testing"""
    return TemplateConverterService()


@pytest.fixture
def mock_template():
    """Mock SlideTemplate for unit tests"""
    from unittest.mock import MagicMock

    template = MagicMock(spec=SlideTemplate)
    template.id = "test_template"
    template.name = "Test Template"
    template.read_markdown_content.return_value = "# Test Slide\n\nTest content"
    return template
