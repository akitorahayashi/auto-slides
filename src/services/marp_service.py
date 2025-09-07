import os
import subprocess

from src.protocols.marp_protocol import OutputType


class MarpService:
    OutputType = OutputType

    def __init__(self, slides_path, output_dir=None):
        self.slides_path = slides_path
        self.output_dir = output_dir
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf(self, output_filename="slides.pdf", theme=None):
        return self._generate(self.OutputType.PDF, output_filename, theme=theme)

    def generate_html(self, output_filename="slides.html", theme=None):
        return self._generate(self.OutputType.HTML, output_filename, theme=theme)

    def generate_png(self, output_filename="slides.png", theme=None):
        return self._generate(self.OutputType.PNG, output_filename, theme=theme)

    def generate_pptx(self, output_filename="slides.pptx", theme=None):
        return self._generate(self.OutputType.PPTX, output_filename, theme=theme)

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
            print(f"{output_type.value.upper()} generation successful: {output_path}")
            print(result.stdout)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"{output_type.value.upper()} generation failed")
            print(e.stderr)
            raise e

    def preview(self, server=True, watch=True):
        command = ["marp", self.slides_path]
        if server:
            command.append("-s")
        if watch:
            command.append("-w")

        print(f"Starting Marp with command: {' '.join(command)}")
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print("Marp preview failed.")
            print(e.stderr)
            raise e
        except KeyboardInterrupt:
            print("\nStopping Marp preview server.")
