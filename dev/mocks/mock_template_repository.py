from pathlib import Path

from src.models import TemplateRepository


class MockTemplateRepository(TemplateRepository):
    """Mock implementation of TemplateRepository for development and testing"""

    def __init__(self, templates_dir: Path):
        super().__init__(templates_dir)
