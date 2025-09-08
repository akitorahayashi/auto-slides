from pathlib import Path
from typing import List, Optional

from .slide_template import SlideTemplate


class TemplateRepository:
    @staticmethod
    def get_all_templates() -> List[SlideTemplate]:
        templates_dir = Path("src/templates")
        templates = []

        for template_dir in templates_dir.iterdir():
            if template_dir.is_dir():
                template_id = template_dir.name
                template = SlideTemplate(
                    id=template_id,
                    name=template_id.replace("_", " ").title(),
                    description=f"Template: {template_id}",
                    template_dir=template_dir,
                )

                # content.mdとtheme.cssの両方が存在する場合のみ追加
                if template.exists():
                    templates.append(template)

        return templates

    @staticmethod
    def get_template_by_id(template_id: str) -> Optional[SlideTemplate]:
        templates = TemplateRepository.get_all_templates()
        return next((t for t in templates if t.id == template_id), None)
