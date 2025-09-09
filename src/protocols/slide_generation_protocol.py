from abc import ABC, abstractmethod
from typing import Any, Dict

from src.models.slide_template import SlideTemplate


class SlideGenerationProtocol(ABC):
    """Protocol for slide generation clients that support stage-specific methods"""

    @abstractmethod
    async def analyze_slides(self, template: SlideTemplate) -> Dict[str, Any]:
        """Stage 1: Analyze slide structure"""
        pass

    @abstractmethod
    async def generate_content(
        self, script_content: str, analysis: Dict[str, Any], template: SlideTemplate
    ) -> Dict[str, Any]:
        """Stage 2: Generate content based on analysis and script"""
        pass
