from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.models.slide_template import SlideTemplate


@dataclass
class AppState:
    """
    アプリケーション全体の状態を管理するデータクラス。
    このクラスのインスタンスがst.session_stateに格納される。
    """

    selected_template: Optional[SlideTemplate] = None
    user_inputs: Optional[Dict[str, Any]] = None
    generated_markdown: Optional[str] = None
