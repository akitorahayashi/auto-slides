import json
from pathlib import Path
from typing import Dict, List, Optional

from src.protocols.template_repository_protocol import TemplateRepositoryProtocol

from .slide_template import SlideTemplate


class TemplateRepository(TemplateRepositoryProtocol):
    def __init__(self, templates_dir: Path = Path("src/templates")):
        self.templates_dir = templates_dir

    def get_all_templates(self) -> List[SlideTemplate]:
        """Get all available slide templates"""
        templates = []

        if not self.templates_dir.exists():
            return []

        for template_dir in self.templates_dir.iterdir():
            if not template_dir.is_dir():
                continue

            dir_name = template_dir.name
            config = self._load_template_config(template_dir)

            if config is None:
                print(f"Info: Using default config for template in '{template_dir}'.")
                config = {
                    "id": dir_name,
                    "name": dir_name.replace("_", " ").title(),
                    "description": f"Template: {dir_name}（目安時間: 10分）",
                    "duration_minutes": 10,
                }

            # Validate the config (either loaded or default)
            if "id" not in config or config["id"] != dir_name:
                print(
                    f"Warning: Skipping template in '{template_dir}'. "
                    f"ID '{config.get('id')}' in config.json does not match directory name '{dir_name}'."
                )
                continue

            template = SlideTemplate(
                id=config["id"],
                name=config.get("name", dir_name.replace("_", " ").title()),
                description=config.get("description", ""),
                template_dir=template_dir,
                duration_minutes=config.get("duration_minutes", 10),
            )

            if template.exists():
                templates.append(template)
            else:
                print(
                    f"Warning: Skipping template '{dir_name}'. Missing slides.py or theme.css."
                )

        return templates

    def _load_template_config(self, template_dir: Path) -> Optional[Dict]:
        config_path = template_dir / "config.json"
        if not config_path.exists():
            return None  # Explicitly return None if file is missing

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not parse config.json in '{template_dir}': {e}")
            return None  # Return None on parsing error too

    def get_template_by_id(self, template_id: str) -> Optional[SlideTemplate]:
        """Get a specific template by ID"""
        templates = self.get_all_templates()
        return next((t for t in templates if t.id == template_id), None)
