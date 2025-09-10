"""
Services module for auto-slides application.

This module provides various services for slide generation and conversion:
- MarpService: Handles Marp CLI operations for slide generation
- SlideGenerator: LLM-based slide content generation
- PromptService: Handles prompt template management
"""

from .marp_service import MarpService
from .prompt_service import PromptService
from .slide_generator import SlideGenerator, extract_placeholders

__all__ = [
    "MarpService",
    "SlideGenerator",
    "PromptService",
    "extract_placeholders",
]
