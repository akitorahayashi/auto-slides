"""
Services module for auto-slides application.

This module provides various services for slide generation and conversion:
- MarpService: Handles Marp CLI operations for slide generation
- PromptService: Handles prompt template management
"""

from .marp_service import MarpService
from .prompt_service import PromptService

__all__ = [
    "MarpService",
    "PromptService",
]
