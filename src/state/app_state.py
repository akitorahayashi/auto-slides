from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.models.slide_template import SlideTemplate


@dataclass
class AppState:
    """
    Manages the state of the application.

    Attributes:
        selected_template (Optional[SlideTemplate]): The slide template selected by the user.
        user_inputs (Optional[Dict[str, Any]]): User-provided values for template placeholders.
        generated_markdown (Optional[str]): The Markdown content generated from the template and user inputs.
    """

    selected_template: Optional[SlideTemplate] = None
    user_inputs: Optional[Dict[str, Any]] = None
    generated_markdown: Optional[str] = None
    selected_format: Optional[str] = None
