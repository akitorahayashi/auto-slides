import json
from pathlib import Path
from typing import Dict, List, Optional

from src.protocols.template_repository_protocol import TemplateRepositoryProtocol

from .slide_template import SlideTemplate


class TemplateRepository(TemplateRepositoryProtocol):
    def __init__(self, templates_dir: Path = Path("src/templates")):
        self.templates_dir = templates_dir

    @classmethod
    def get_all_templates(cls) -> List[SlideTemplate]:
        """Get all available slide templates"""
        instance = cls()
        return instance._get_all_templates()

    def _get_all_templates(self) -> List[SlideTemplate]:
        templates = []

        if not self.templates_dir.exists():
            return []

        for template_dir in self.templates_dir.iterdir():
            if template_dir.is_dir():
                dir_name = template_dir.name
                config = self._load_template_config(template_dir)

                if "id" in config and config["id"] == dir_name:
                    template = SlideTemplate(
                        id=config["id"],
                        name=config["name"],
                        description=config["description"],
                        template_dir=template_dir,
                        duration_minutes=config["duration_minutes"],
                    )
                    if template.exists():
                        templates.append(template)
                else:
                    print(
                        f"Warning: Skipping template in '{template_dir}'. "
                        f"ID in config.json does not match directory name or is missing."
                    )

        return templates

    def _load_template_config(self, template_dir: Path) -> Dict:
        config_path = template_dir / "config.json"
        dir_name = template_dir.name

        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, KeyError):
                pass

        return {
            "id": dir_name,
            "name": dir_name.replace("_", " ").title(),
            "description": f"Template: {dir_name}（目安時間: 10分）",
            "duration_minutes": 10,
        }

    @classmethod
    def get_template_by_id(cls, template_id: str) -> Optional[SlideTemplate]:
        """Get a specific template by ID"""
        instance = cls()
        return instance._get_template_by_id(template_id)

    def _get_template_by_id(self, template_id: str) -> Optional[SlideTemplate]:
        templates = self._get_all_templates()
        return next((t for t in templates if t.id == template_id), None)
