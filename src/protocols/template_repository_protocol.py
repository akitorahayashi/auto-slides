from typing import List, Optional, Protocol

from src.models.slide_template import SlideTemplate


class TemplateRepositoryProtocol(Protocol):
    """Protocol for template repository implementations"""

    def get_all_templates(self) -> List[SlideTemplate]:
        """Get all available slide templates"""
        ...

    def get_template_by_id(self, template_id: str) -> Optional[SlideTemplate]:
        """Get a specific template by ID"""
        ...
