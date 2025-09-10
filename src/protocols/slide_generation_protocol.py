from typing import Protocol

from src.backend.models.slide_template import SlideTemplate


class SlideGenerationProtocol(Protocol):
    """
    Protocol for slide generation chains.
    """

    def invoke_slide_gen_chain(
        self, script_content: str, template: SlideTemplate
    ) -> str:
        """
        Invokes the slide generation chain.

        Args:
            script_content: The script content for the slides.
            template: The slide template to be used.

        Returns:
            The generated slides in markdown format.
        """
        ...
