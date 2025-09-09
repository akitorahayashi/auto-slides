from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Optional

from src.models.slide_template import SlideTemplate
from src.protocols.slide_generation_protocol import SlideGenerationProtocol
from src.services.structured_parser import StructuredResponseParser


class MockSlideGeneratorClient(SlideGenerationProtocol):
    """
    Mock client specifically for SlideGenerator that returns structured JSON responses.
    """

    def __init__(self):
        self.mock_dir = Path("dev/mocks/static/mock_responses")
        self.structured_response_file = self.mock_dir / "structured_response.txt"

    def _load_mock_response(self, stage: Optional[str] = None) -> str:
        """Load structured natural language mock response"""
        if stage:
            staged_file = self.mock_dir / f"{stage}.txt"
            if staged_file.exists():
                return staged_file.read_text(encoding="utf-8")

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

    async def analyze_slides(self, _template: SlideTemplate) -> Dict[str, Any]:
        """Stage 1: Analyze slide structure"""
        text = self._load_mock_response("stage1")
        parser = StructuredResponseParser()
        return parser.parse_enhanced_structure(text, set())

    async def generate_content(
        self, _script_content: str, _analysis: Dict[str, Any], _template: SlideTemplate
    ) -> Dict[str, Any]:
        """Stage 2: Generate content based on analysis and script"""
        text = self._load_mock_response("stage2")
        parser = StructuredResponseParser()
        return parser.parse_enhanced_structure(text, set())

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
