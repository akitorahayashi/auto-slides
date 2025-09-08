import json
from pathlib import Path
from typing import Dict, List, Optional

from .slide_template import SlideTemplate


class TemplateRepository:
    @staticmethod
    def get_all_templates() -> List[SlideTemplate]:
        templates_dir = Path("src/templates")
        templates = []

        for template_dir in templates_dir.iterdir():
            if template_dir.is_dir():
                template_id = template_dir.name

                # config.jsonから設定を読み込み
                config = TemplateRepository._load_template_config(
                    template_dir, template_id
                )

                template = SlideTemplate(
                    id=template_id,
                    name=config["name"],
                    description=config["description"],
                    template_dir=template_dir,
                    duration_minutes=config["duration_minutes"],
                )

                # content.mdとtheme.cssの両方が存在する場合のみ追加
                if template.exists():
                    templates.append(template)

        return templates

    @staticmethod
    def _load_template_config(template_dir: Path, template_id: str) -> Dict:
        """テンプレートディレクトリからconfig.jsonを読み込み"""
        config_path = template_dir / "config.json"

        # config.jsonが存在する場合は読み込み
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, KeyError):
                pass  # エラーの場合はデフォルト設定を使用

        # デフォルト設定
        return {
            "name": template_id.replace("_", " ").title(),
            "description": f"Template: {template_id}（目安時間: 10分）",
            "duration_minutes": 10,
        }

    @staticmethod
    def get_template_by_id(template_id: str) -> Optional[SlideTemplate]:
        templates = TemplateRepository.get_all_templates()
        return next((t for t in templates if t.id == template_id), None)
