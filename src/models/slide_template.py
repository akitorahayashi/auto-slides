from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional


class TemplateFormat(Enum):
    PDF = "pdf"
    HTML = "html"
    PPTX = "pptx"


@dataclass
class SlideTemplate:
    id: str
    name: str
    description: str
    template_dir: Path

    @property
    def markdown_path(self) -> Path:
        return self.template_dir / "content.md"

    @property
    def css_path(self) -> Path:
        return self.template_dir / "theme.css"

    def exists(self) -> bool:
        return self.template_dir.exists() and self.markdown_path.exists()

    def read_markdown_content(self) -> str:
        if not self.markdown_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {self.markdown_path}")
        return self.markdown_path.read_text(encoding="utf-8")

    def read_css_content(self) -> Optional[str]:
        if self.css_path.exists():
            return self.css_path.read_text(encoding="utf-8")
        return None


class TemplateRepository:
    @staticmethod
    def get_all_templates() -> List[SlideTemplate]:
        templates_dir = Path("src/templates")
        templates = []

        for template_dir in templates_dir.iterdir():
            if template_dir.is_dir():
                template_id = template_dir.name
                templates.append(
                    SlideTemplate(
                        id=template_id,
                        name=template_id.replace("_", " ").title(),
                        description=f"Template: {template_id}",
                        template_dir=template_dir,
                    )
                )

        return templates

    @staticmethod
    def get_template_by_id(template_id: str) -> Optional[SlideTemplate]:
        templates = TemplateRepository.get_all_templates()
        return next((t for t in templates if t.id == template_id), None)
