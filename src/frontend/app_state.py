from dataclasses import dataclass
from typing import Any, Optional

from src.backend.models.slide_template import SlideTemplate
from src.protocols.protocols.template_repository_protocol import (
    TemplateRepositoryProtocol,
)
from src.protocols.slide_generation_protocol import SlideGenerationProtocol


@dataclass
class AppState:
    """
    アプリケーションの状態を管理するデータクラス
    """

    template_repository: Optional[TemplateRepositoryProtocol] = None
    slide_generator: Optional[SlideGenerationProtocol] = None
    selected_template: Optional[SlideTemplate] = None
    user_inputs: Optional[dict[str, Any]] = None
    generated_markdown: Optional[str] = None
