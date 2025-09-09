import json
from pathlib import Path
from typing import AsyncGenerator

from sdk.olm_api_client import OllamaClientProtocol


class MockSlideGeneratorClient:
    """
    Mock client specifically for SlideGenerator that returns structured JSON responses.
    """
    
    def __init__(self):
        self.mock_dir = Path("dev/mocks/static/mock_responses")
        self.stage1_file = self.mock_dir / "stage1_analysis.json"
        self.stage2_file = self.mock_dir / "stage2_content.json"
    
    def _detect_stage(self, prompt: str) -> str:
        """Detect which stage based on prompt content"""
        if "スライド構造分析" in prompt or "analyze_slides" in prompt:
            return "stage1"
        elif "コンテンツ生成" in prompt or "generate_content" in prompt:
            return "stage2"
        return "stage1"  # default
    
    def _load_mock_response(self, stage: str) -> str:
        """Load appropriate mock response based on stage"""
        if stage == "stage1":
            file_path = self.stage1_file
        else:
            file_path = self.stage2_file
        
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        else:
            # Fallback to basic JSON
            return '{"error": "Mock file not found", "stage": "' + stage + '"}'
    
    async def gen_stream(self, prompt: str, model_name: str) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        stage = self._detect_stage(prompt)
        response = self._load_mock_response(stage)
        
        # Stream the response character by character
        for char in response:
            yield char
    
    async def gen_batch(self, prompt: str, model_name: str) -> str:
        """Generate complete response"""
        stage = self._detect_stage(prompt)
        return self._load_mock_response(stage)