"""
Services module for auto-slides application.

This module provides various services for slide generation and conversion:
- MarpService: Handles Marp CLI operations for slide generation
- SlideGenerator: LLM-based slide content generation
- TemplateConverterService: Template conversion to various formats
"""

from .marp_service import MarpService
from .slide_generator import SlideGenerator
from .template_converter_service import TemplateConverterService

__all__ = [
    "MarpService",
    "SlideGenerator",
    "TemplateConverterService",
]
