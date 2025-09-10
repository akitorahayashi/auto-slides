import logging
import os

from src.protocols.schemas.output_format import OutputFormat

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MockMarpService:
    OutputFormat = OutputFormat

    def __init__(self, slides_path, output_dir=None):
        self.slides_path = slides_path
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf(self, output_filename="slides.pdf", theme=None):
        return self._mock_generate(self.OutputFormat.PDF, output_filename, theme=theme)

    def generate_html(self, output_filename="slides.html", theme=None):
        return self._mock_generate(self.OutputFormat.HTML, output_filename, theme=theme)

    def generate_png(self, output_filename="slides.png", theme=None):
        return self._mock_generate(self.OutputFormat.PNG, output_filename, theme=theme)

    def generate_pptx(self, output_filename="slides.pptx", theme=None):
        return self._mock_generate(self.OutputFormat.PPTX, output_filename, theme=theme)

    def _mock_generate(self, output_type, output_filename, theme=None):
        if not self.output_dir:
            raise ValueError("Output directory must be set for generation.")

        output_path = os.path.join(self.output_dir, output_filename)

        # Create a mock file for testing
        with open(output_path, "w") as f:
            f.write(f"Mock {output_type.value} file generated from {self.slides_path}")
            if theme:
                f.write(f" with theme: {theme}")

        self.logger.info(
            f"MOCK {output_type.value.upper()} generation successful: {output_path}"
        )
        return output_path

    def preview(self, server=True, watch=True):
        print(f"MOCK: Starting Marp preview for {self.slides_path}")
        print(f"Server: {server}, Watch: {watch}")
        print("Mock preview started successfully")
