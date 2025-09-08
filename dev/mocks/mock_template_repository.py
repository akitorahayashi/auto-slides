from typing import List, Optional

from src.models import SlideTemplate
from src.protocols import TemplateRepositoryProtocol


class MockTemplateRepository(TemplateRepositoryProtocol):
    """Mock implementation of TemplateRepositoryProtocol for testing"""

    def __init__(self, mock_templates: List[SlideTemplate] = None):
        self._templates = mock_templates or []

    def get_all_templates(self) -> List[SlideTemplate]:
        """Return mock templates"""
        return self._templates

    def get_template_by_id(self, template_id: str) -> Optional[SlideTemplate]:
        """Return mock template by ID"""
        return next((t for t in self._templates if t.id == template_id), None)
