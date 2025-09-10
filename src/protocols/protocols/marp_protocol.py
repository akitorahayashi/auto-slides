from typing import Protocol


class MarpProtocol(Protocol):
    slides_path: str
    output_dir: str | None

    def generate_pdf(
        self, output_filename: str = "slides.pdf", theme: str | None = None
    ) -> str:
        """Generate PDF from slides"""
        ...

    def generate_html(
        self, output_filename: str = "slides.html", theme: str | None = None
    ) -> str:
        """Generate HTML from slides"""
        ...

    def generate_png(
        self, output_filename: str = "slides.png", theme: str | None = None
    ) -> str:
        """Generate PNG from slides"""
        ...

    def generate_pptx(
        self, output_filename: str = "slides.pptx", theme: str | None = None
    ) -> str:
        """Generate PPTX from slides"""
        ...

    def preview(self, server: bool = True, watch: bool = True) -> None:
        """Launch Marp preview"""
        ...
