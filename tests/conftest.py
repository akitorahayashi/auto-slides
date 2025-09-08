import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.models import SlideTemplate
from src.services import MarpService, TemplateConverterService


@pytest.fixture
def project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_template_path(project_root):
    """Path to the sample template content.md"""
    return project_root / "src" / "templates" / "k2g4h1x9" / "content.md"


@pytest.fixture
def sample_template(sample_template_path):
    """Sample SlideTemplate instance using the actual sample content"""
    return SlideTemplate(
        id="k2g4h1x9",
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
    template = MagicMock(spec=SlideTemplate)
    template.id = "test_template"
    template.name = "Test Template"
    template.read_markdown_content.return_value = "# Test Slide\n\nTest content"
    return template


@pytest.fixture
def mock_streamlit_secrets():
    """Mock streamlit.secrets for consistent testing"""
    with patch('streamlit.secrets') as mock_secrets:
        mock_secrets.get.return_value = "false"
        yield mock_secrets


@pytest.fixture
def mock_slide_generator(mock_streamlit_secrets):
    """Mock SlideGenerator with mocked Streamlit secrets"""
    from src.services.slide_generator import SlideGenerator
    with patch('src.services.slide_generator.SlideGenerator._get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        generator = SlideGenerator()
        yield generator


@pytest.fixture
def mock_template_repository():
    """Mock TemplateRepository for testing"""
    from src.models.template_repository import TemplateRepository
    with patch.object(TemplateRepository, '_get_all_templates') as mock_get_all:
        mock_get_all.return_value = []
        yield TemplateRepository
