from dataclasses import dataclass
from pathlib import Path
from typing import Optional


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
