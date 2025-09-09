import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dev.mocks.mock_template_repository import MockTemplateRepository
from src.models import SlideTemplate
from src.services import MarpService, TemplateConverterService


@pytest.fixture
def project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def test_template_dir(project_root):
    """Path to the test template directory"""
    return project_root / "data" / "tests" / "templates" / "k2g4h1x9"


@pytest.fixture
def sample_template(test_template_dir):
    """Sample SlideTemplate instance using the test template"""
    return SlideTemplate(
        id="k2g4h1x9",
        name="サンプルテンプレート",
        description="4トピック構成のベーシックなプレゼンテーション",
        template_dir=test_template_dir,
        duration_minutes=10,
    )


@pytest.fixture
def mock_template_repository_with_sample(project_root):
    """MockTemplateRepository with sample template"""
    return MockTemplateRepository(
        templates_dir=project_root / "data" / "tests" / "templates"
    )


@pytest.fixture
def sample_template_path(test_template_dir):
    """Path to the sample template content.md (for backward compatibility)"""
    return test_template_dir / "content.md"


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
    with patch("streamlit.secrets") as mock_secrets:
        mock_secrets.get.return_value = "false"
        yield mock_secrets


@pytest.fixture
def mock_slide_generator(mock_streamlit_secrets):
    """Mock SlideGenerator with mocked Streamlit secrets"""
    from src.services.slide_generator import SlideGenerator

    with patch(
        "src.clients.ollama_client.OllamaClientManager.create_client"
    ) as mock_create_client:
        mock_client = MagicMock()
        mock_create_client.return_value = (mock_client, "test_model")
        generator = SlideGenerator()
        yield generator


@pytest.fixture
def mock_template_repository(project_root):
    """Mock TemplateRepository for testing"""
    # Create a temporary empty directory for templates
    with tempfile.TemporaryDirectory() as temp_dir:
        yield MockTemplateRepository(templates_dir=Path(temp_dir))
