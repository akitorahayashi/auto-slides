from dataclasses import dataclass
from typing import Any, Optional

from src.models.slide_template import SlideTemplate
from src.protocols import TemplateRepositoryProtocol
from src.services.slide_generator import SlideGenerator


@dataclass
class AppState:
    """
    アプリケーションの状態を管理するデータクラス
    """

    template_repository: Optional[TemplateRepositoryProtocol] = None
    slide_generator: Optional[SlideGenerator] = None
    selected_template: Optional[SlideTemplate] = None
    user_inputs: Optional[dict[str, Any]] = None
    generated_markdown: Optional[str] = None
