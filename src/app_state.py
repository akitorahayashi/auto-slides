from dataclasses import dataclass
from typing import Any, Optional

from src.models.slide_template import SlideTemplate


@dataclass
class AppState:
    """
    アプリケーションの状態を管理するデータクラス
    """

    selected_template: Optional[SlideTemplate] = None
    user_inputs: Optional[dict[str, Any]] = None
    generated_markdown: Optional[str] = None
