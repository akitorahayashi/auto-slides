import logging
import os
import subprocess

from src.schemas import OutputFormat

# Configure basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MarpService:
    OutputFormat = OutputFormat

    def __init__(self, slides_path, output_dir=None):
        self.slides_path = slides_path
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf(self, output_filename="slides.pdf", theme=None):
        return self._generate(self.OutputFormat.PDF, output_filename, theme=theme)

    def generate_html(self, output_filename="slides.html", theme=None):
        return self._generate(self.OutputFormat.HTML, output_filename, theme=theme)

    def generate_png(self, output_filename="slides.png", theme=None):
        return self._generate(self.OutputFormat.PNG, output_filename, theme=theme)

    def generate_pptx(self, output_filename="slides.pptx", theme=None):
        return self._generate(self.OutputFormat.PPTX, output_filename, theme=theme)

    def _generate(self, output_type, output_filename, theme=None):
        if not self.output_dir:
            raise ValueError("Output directory must be set for generation.")
        output_path = os.path.join(self.output_dir, output_filename)
        command = ["marp", self.slides_path, "-o", output_path]
        if theme:
            command.extend(["--theme", theme])
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
            self.logger.info(
                f"{output_type.value.upper()} generation successful: {output_path}"
            )
            self.logger.debug(result.stdout)
            return output_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"{output_type.value.upper()} generation failed")
            self.logger.error(e.stderr)
            raise e

    def preview(self, server=True, watch=True):
        command = ["marp", self.slides_path]
        if server:
            command.append("-s")
        if watch:
            command.append("-w")

        self.logger.info(f"Starting Marp with command: {' '.join(command)}")
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error("Marp preview failed.")
            self.logger.error(e.stderr)
            raise e
        except KeyboardInterrupt:
            self.logger.info("\nStopping Marp preview server.")
