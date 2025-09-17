import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dev.mocks import MockTemplateRepository
from src.backend.models.slide_template import SlideTemplate
from src.backend.services import MarpService


@pytest.fixture
def project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def test_template_dir(project_root):
    """Path to the test template directory"""
    return project_root / "src" / "backend" / "templates" / "basic_presentation"


@pytest.fixture
def sample_template(test_template_dir):
    """Sample SlideTemplate instance using the test template"""
    return SlideTemplate(
        id="basic_presentation",
        name="サンプルテンプレート",
        description="4トピック構成のベーシックなプレゼンテーション",
        template_dir=test_template_dir,
        duration_minutes=10,
    )


@pytest.fixture
def mock_template_repository_with_sample(project_root):
    """MockTemplateRepository with sample template"""
    return MockTemplateRepository(
        templates_dir=project_root / "src" / "backend" / "templates"
    )


@pytest.fixture
def sample_template_path(test_template_dir):
    """Path to the sample template slides.py"""
    return test_template_dir / "slides.py"


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


# TemplateConverterService removed - using MarpService instead


@pytest.fixture
def mock_template():
    """Mock SlideTemplate for unit tests"""
    template = MagicMock(spec=SlideTemplate)
    template.id = "test_template"
    template.name = "Test Template"
    template.read_markdown_content.return_value = "# Test Slide\n\nTest content"
    return template


@pytest.fixture
def real_prompt_service():
    """Real PromptService for testing (no external dependencies)"""
    from src.backend.services import PromptService

    return PromptService()


@pytest.fixture
def mock_template_repository(project_root):
    """Mock TemplateRepository for testing"""
    # Create a temporary empty directory for templates
    with tempfile.TemporaryDirectory() as temp_dir:
        yield MockTemplateRepository(templates_dir=Path(temp_dir))
