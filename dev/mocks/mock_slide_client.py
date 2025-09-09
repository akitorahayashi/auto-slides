import json
from pathlib import Path
from typing import Any, AsyncGenerator, Dict

from src.models.slide_template import SlideTemplate
from src.protocols.slide_generation_protocol import SlideGenerationProtocol


class MockSlideGeneratorClient(SlideGenerationProtocol):
    """
    Mock client specifically for SlideGenerator that returns structured JSON responses.
    """

    def __init__(self):
        self.mock_dir = Path("dev/mocks/static/mock_responses")
        self.structured_response_file = self.mock_dir / "structured_response.txt"

    def _load_mock_response(self) -> str:
        """Load structured natural language mock response"""
        if self.structured_response_file.exists():
            return self.structured_response_file.read_text(encoding="utf-8")
        else:
            # Fallback to basic structured response
            return """TITLE: Default Mock Title
POINT1: Default first point
POINT2: Default second point  
POINT3: Default third point
CONCLUSION: Default conclusion
AUTHOR: Mock Author
DATE: 2024-01-01"""

    async def analyze_slides(self, template: SlideTemplate) -> Dict[str, Any]:
        """Stage 1: Analyze slide structure"""
        response = self._load_mock_response("stage1")
        return json.loads(response)

    async def generate_content(
        self, script_content: str, analysis: Dict[str, Any], template: SlideTemplate
    ) -> Dict[str, Any]:
        """Stage 2: Generate content based on analysis and script"""
        response = self._load_mock_response("stage2")
        return json.loads(response)

    # Keep original methods for backward compatibility with olm-api protocol
    def _detect_stage(self, prompt: str) -> str:
        """Detect which stage based on prompt file path"""
        if "01_analyze_slides.md" in prompt:
            return "stage1"
        elif "02_generate_content.md" in prompt:
            return "stage2"
        return "stage1"  # default

    async def gen_stream(
        self, prompt: str, model_name: str
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        stage = self._detect_stage(prompt)
        response = self._load_mock_response(stage)

        # Stream the response character by character
        for char in response:
            yield char

    async def gen_batch(self, prompt: str, model_name: str) -> str:
        """Generate complete response"""
        return self._load_mock_response()
