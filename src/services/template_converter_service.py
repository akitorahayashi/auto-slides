import subprocess
import tempfile
from pathlib import Path

from src.models import SlideTemplate
from src.schemas import TemplateFormat


class TemplateConverterService:
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "auto-slides"
        self.temp_dir.mkdir(exist_ok=True)

    def convert_template_to_pdf(self, template: SlideTemplate) -> bytes:
        markdown_content = template.read_markdown_content()
        css_content = template.read_css_content()  # 必須なのでエラーハンドリングは不要
        temp_md_path = self.temp_dir / f"{template.id}.md"
        temp_css_path = self.temp_dir / f"{template.id}.css"
        temp_pdf_path = self.temp_dir / f"{template.id}.pdf"

        try:
            temp_md_path.write_text(markdown_content, encoding="utf-8")
            temp_css_path.write_text(css_content, encoding="utf-8")

            # CSSテーマを必ず適用
            command = [
                "marp",
                str(temp_md_path),
                "--theme",
                str(temp_css_path),
                "-o",
                str(temp_pdf_path),
            ]

            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

            if temp_pdf_path.exists():
                pdf_bytes = temp_pdf_path.read_bytes()
                return pdf_bytes
            else:
                raise Exception("PDF generation failed")

        except subprocess.CalledProcessError as e:
            raise Exception(f"Marp PDF generation failed: {e.stderr}")
        finally:
            if temp_md_path.exists():
                temp_md_path.unlink()
            if temp_css_path.exists():
                temp_css_path.unlink()
            if temp_pdf_path.exists():
                temp_pdf_path.unlink()

    def convert_template_to_html(self, template: SlideTemplate) -> str:
        markdown_content = template.read_markdown_content()
        css_content = template.read_css_content()  # 必須なのでエラーハンドリングは不要
        temp_md_path = self.temp_dir / f"{template.id}.md"
        temp_css_path = self.temp_dir / f"{template.id}.css"
        temp_html_path = self.temp_dir / f"{template.id}.html"

        try:
            temp_md_path.write_text(markdown_content, encoding="utf-8")
            temp_css_path.write_text(css_content, encoding="utf-8")

            # CSSテーマを必ず適用
            command = [
                "marp",
                str(temp_md_path),
                "--theme",
                str(temp_css_path),
                "-o",
                str(temp_html_path),
            ]

            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

            if temp_html_path.exists():
                html_content = temp_html_path.read_text(encoding="utf-8")
                return html_content
            else:
                raise Exception("HTML generation failed")

        except subprocess.CalledProcessError as e:
            raise Exception(f"Marp HTML generation failed: {e.stderr}")
        finally:
            if temp_md_path.exists():
                temp_md_path.unlink()
            if temp_css_path.exists():
                temp_css_path.unlink()
            if temp_html_path.exists():
                temp_html_path.unlink()

    def convert_template_to_pptx(self, template: SlideTemplate) -> bytes:
        markdown_content = template.read_markdown_content()
        css_content = template.read_css_content()  # 必須なのでエラーハンドリングは不要
        temp_md_path = self.temp_dir / f"{template.id}.md"
        temp_css_path = self.temp_dir / f"{template.id}.css"
        temp_pptx_path = self.temp_dir / f"{template.id}.pptx"

        try:
            temp_md_path.write_text(markdown_content, encoding="utf-8")
            temp_css_path.write_text(css_content, encoding="utf-8")

            # CSSテーマを必ず適用
            command = [
                "marp",
                str(temp_md_path),
                "--theme",
                str(temp_css_path),
                "-o",
                str(temp_pptx_path),
            ]

            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

            if temp_pptx_path.exists():
                pptx_bytes = temp_pptx_path.read_bytes()
                return pptx_bytes
            else:
                raise Exception("PPTX generation failed")

        except subprocess.CalledProcessError as e:
            raise Exception(f"Marp PPTX generation failed: {e.stderr}")
        finally:
            if temp_md_path.exists():
                temp_md_path.unlink()
            if temp_css_path.exists():
                temp_css_path.unlink()
            if temp_pptx_path.exists():
                temp_pptx_path.unlink()

    def get_filename(self, template: SlideTemplate, format: TemplateFormat) -> str:
        return f"{template.id}.{format.value}"

    def convert_markdown_to_pdf(
        self, markdown_content: str, css_content: str, filename_prefix: str = "slides"
    ) -> bytes:
        """直接MarkdownコンテンツからPDFを生成"""
        temp_md_path = self.temp_dir / f"{filename_prefix}.md"
        temp_css_path = self.temp_dir / f"{filename_prefix}.css"
        temp_pdf_path = self.temp_dir / f"{filename_prefix}.pdf"

        try:
            temp_md_path.write_text(markdown_content, encoding="utf-8")
            temp_css_path.write_text(css_content, encoding="utf-8")

            command = [
                "marp",
                str(temp_md_path),
                "--theme",
                str(temp_css_path),
                "-o",
                str(temp_pdf_path),
            ]

            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

            if temp_pdf_path.exists():
                pdf_bytes = temp_pdf_path.read_bytes()
                return pdf_bytes
            else:
                raise Exception("PDF generation failed")

        except subprocess.CalledProcessError as e:
            raise Exception(f"Marp PDF generation failed: {e.stderr}")
        finally:
            if temp_md_path.exists():
                temp_md_path.unlink()
            if temp_css_path.exists():
                temp_css_path.unlink()
            if temp_pdf_path.exists():
                temp_pdf_path.unlink()

    def convert_markdown_to_html(
        self, markdown_content: str, css_content: str, filename_prefix: str = "slides"
    ) -> str:
        """直接MarkdownコンテンツからHTMLを生成"""
        temp_md_path = self.temp_dir / f"{filename_prefix}.md"
        temp_css_path = self.temp_dir / f"{filename_prefix}.css"
        temp_html_path = self.temp_dir / f"{filename_prefix}.html"

        try:
            temp_md_path.write_text(markdown_content, encoding="utf-8")
            temp_css_path.write_text(css_content, encoding="utf-8")

            command = [
                "marp",
                str(temp_md_path),
                "--theme",
                str(temp_css_path),
                "-o",
                str(temp_html_path),
            ]

            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

            if temp_html_path.exists():
                html_content = temp_html_path.read_text(encoding="utf-8")
                return html_content
            else:
                raise Exception("HTML generation failed")

        except subprocess.CalledProcessError as e:
            raise Exception(f"Marp HTML generation failed: {e.stderr}")
        finally:
            if temp_md_path.exists():
                temp_md_path.unlink()
            if temp_css_path.exists():
                temp_css_path.unlink()
            if temp_html_path.exists():
                temp_html_path.unlink()

    def convert_markdown_to_pptx(
        self, markdown_content: str, css_content: str, filename_prefix: str = "slides"
    ) -> bytes:
        """直接MarkdownコンテンツからPPTXを生成"""
        temp_md_path = self.temp_dir / f"{filename_prefix}.md"
        temp_css_path = self.temp_dir / f"{filename_prefix}.css"
        temp_pptx_path = self.temp_dir / f"{filename_prefix}.pptx"

        try:
            temp_md_path.write_text(markdown_content, encoding="utf-8")
            temp_css_path.write_text(css_content, encoding="utf-8")

            command = [
                "marp",
                str(temp_md_path),
                "--theme",
                str(temp_css_path),
                "-o",
                str(temp_pptx_path),
            ]

            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

            if temp_pptx_path.exists():
                pptx_bytes = temp_pptx_path.read_bytes()
                return pptx_bytes
            else:
                raise Exception("PPTX generation failed")

        except subprocess.CalledProcessError as e:
            raise Exception(f"Marp PPTX generation failed: {e.stderr}")
        finally:
            if temp_md_path.exists():
                temp_md_path.unlink()
            if temp_css_path.exists():
                temp_css_path.unlink()
            if temp_pptx_path.exists():
                temp_pptx_path.unlink()
