import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Set


@dataclass
class SlideTemplate:
    id: str
    name: str
    description: str
    template_dir: Path
    duration_minutes: int

    @property
    def slides_path(self) -> Path:
        return self.template_dir / "slides.py"

    @property
    def css_path(self) -> Path:
        return self.template_dir / "theme.css"

    def exists(self) -> bool:
        """Check if both slides.py and theme.css exist"""
        return (
            self.template_dir.exists()
            and self.slides_path.exists()
            and self.css_path.exists()
        )

    def read_slides_content(self) -> str:
        if not self.slides_path.exists():
            raise FileNotFoundError(f"Slides file not found: {self.slides_path}")
        return self.slides_path.read_text(encoding="utf-8")

    def read_css_content(self) -> str:
        """Read CSS theme file"""
        if not self.css_path.exists():
            raise FileNotFoundError(f"CSS theme file not found: {self.css_path}")
        return self.css_path.read_text(encoding="utf-8")

    def extract_placeholders(self, template_content: str = None) -> Set[str]:
        """Extract all ${placeholder} variables from template content"""
        if template_content is None:
            template_content = self.read_slides_content()

        pattern = r"\$\{([^}]+)\}"
        matches = re.findall(pattern, template_content)
        return set(matches)

    def render_template(self, template_content: str, variables: Dict[str, str]) -> str:
        """Render template content by replacing placeholders with variables"""
        result = template_content
        for key, value in variables.items():
            placeholder = f"${{{key}}}"
            result = result.replace(placeholder, value)
        return result
