from dataclasses import dataclass
from pathlib import Path


@dataclass
class SlideTemplate:
    id: str
    name: str
    description: str
    template_dir: Path
    duration_minutes: int

    @property
    def markdown_path(self) -> Path:
        return self.template_dir / "content.md"

    @property
    def css_path(self) -> Path:
        return self.template_dir / "theme.css"

    def exists(self) -> bool:
        """Check if both content.md and theme.css exist"""
        return (
            self.template_dir.exists()
            and self.markdown_path.exists()
            and self.css_path.exists()
        )

    def read_markdown_content(self) -> str:
        if not self.markdown_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {self.markdown_path}")
        return self.markdown_path.read_text(encoding="utf-8")

    def read_css_content(self) -> str:
        """Read CSS theme file"""
        if not self.css_path.exists():
            raise FileNotFoundError(f"CSS theme file not found: {self.css_path}")
        return self.css_path.read_text(encoding="utf-8")
