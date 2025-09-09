"""
Integration tests for SlideGenerator with real LLM clients.
Tests the full 2-stage LLM chain with external dependencies.
"""

import asyncio
import os
from pathlib import Path

import pytest
import streamlit as st

from src.models.slide_template import SlideTemplate
from src.services.slide_generator import SlideGenerator


class TestSlideGeneratorIntegration:
    """Integration tests for SlideGenerator with real LLM"""

    @pytest.fixture
    def sample_script(self):
        """Sample script content for testing"""
        return """
        今日はPythonの非同期プログラミングについて説明します。
        
        非同期プログラミングとは、複数のタスクを並行して実行する技術です。
        Pythonではasyncioライブラリを使用します。
        
        基本的な使い方：
        - async def で非同期関数を定義
        - await で非同期処理を待機
        - asyncio.run()で実行
        
        メリット：
        - I/O待機時間の短縮
        - CPUリソースの効率的利用
        - レスポンシブなアプリケーション
        
        実際のコード例も紹介します。
        """

    @pytest.fixture
    def test_template(self):
        """Test template using existing template data"""
        return SlideTemplate(
            id="test",
            name="Test Template",
            description="Test Description",
            template_dir=Path("tests/templates/k2g4h1x9"),
            duration_minutes=5,
        )

    def test_slide_generator_with_mock_client(self, sample_script, test_template):
        """Test SlideGenerator with mock client (fast, no external dependency)"""
        # Use mock client directly
        from dev.mocks.mock_slide_client import MockSlideGeneratorClient

        # Create generator with mock client directly
        generator = SlideGenerator()
        generator.client = MockSlideGeneratorClient()
        generator.model = "test-model"

        result = generator.generate_sync(sample_script, test_template)

        # Basic validation
        assert isinstance(result, str)
        assert len(result) > 100  # Should have substantial content
        assert "---" in result  # Marp slide separators

        # Check that some placeholders were filled
        assert "${" not in result or result.count("${") < 5  # Most should be replaced

    @pytest.mark.skipif(
        not str(st.secrets.get("USE_LOCAL_CLIENT", "false")).lower() == "true",
        reason="USE_LOCAL_CLIENT not enabled - set USE_LOCAL_CLIENT=true in secrets.toml",
    )
    def test_slide_generator_with_local_ollama(self, sample_script, test_template):
        """Test SlideGenerator with local Ollama (requires ollama serve running)"""
        # Force local client mode
        original_debug = os.environ.get("DEBUG")
        original_use_local = os.environ.get("USE_LOCAL_CLIENT")

        os.environ["DEBUG"] = "false"
        os.environ["USE_LOCAL_CLIENT"] = "true"

        try:
            generator = SlideGenerator()
            result = generator.generate_sync(sample_script, test_template)

            # Validate structure
            assert isinstance(result, str)
            assert len(result) > 200  # Should be substantial
            assert "---" in result  # Marp separators

            # Check for typical slide content
            assert any(
                keyword in result.lower()
                for keyword in ["python", "async", "非同期", "プログラミング"]
            )

            # Validate it's proper Marp format
            lines = result.split("\n")
            assert lines[0].strip() == "---"  # Should start with frontmatter
            assert "marp: true" in result

        finally:
            # Restore original settings
            if original_debug is None:
                os.environ.pop("DEBUG", None)
            else:
                os.environ["DEBUG"] = original_debug

            if original_use_local is None:
                os.environ.pop("USE_LOCAL_CLIENT", None)
            else:
                os.environ["USE_LOCAL_CLIENT"] = original_use_local

    def test_slide_generator_async_methods(self, sample_script, test_template):
        """Test the new async generation method"""

        async def run_test():
            # Use mock client directly
            from dev.mocks.mock_slide_client import MockSlideGeneratorClient

            generator = SlideGenerator()
            generator.client = MockSlideGeneratorClient()
            generator.model = "test-model"

            # Test content generation (main async method)
            content = await generator.generate_content(sample_script, test_template)
            assert isinstance(content, dict)
            assert "presentation_title" in content

            # Test full generation chain
            result = await generator.generate(sample_script, test_template)
            assert isinstance(result, str)
            assert len(result) > 100

            # Verify it contains expected content
            assert (
                "Mock Presentation Title" in result
                or content["presentation_title"] in result
            )

        # Run the async test
        asyncio.run(run_test())

    def test_structured_parsing(self):
        """Test structured response parsing"""
        from src.services.structured_parser import StructuredResponseParser

        parser = StructuredResponseParser()

        # Test valid structured response
        structured_text = """TITLE: Test Title
POINT1: First point
POINT2: Second point
CONCLUSION: Final thoughts"""

        result = parser.parse_enhanced_structure(structured_text, set())
        assert result["presentation_title"] == "Test Title"
        assert "First point" in result["topic_1_content"]
        assert "Second point" in result["topic_2_content"]

        # Test with think tags
        text_with_think = """<think>thinking...</think>
TITLE: Another Test
POINT1: Another point"""

        result = parser.parse_enhanced_structure(text_with_think, set())
        assert result["presentation_title"] == "Another Test"

    @pytest.mark.skipif(
        str(st.secrets.get("DEBUG", "false")).lower() == "true",
        reason="Skipping LLM response validation in DEBUG mode",
    )
    def test_llm_response_quality(self, sample_script, test_template):
        """Test that LLM responses meet quality expectations"""
        generator = SlideGenerator()
        result = generator.generate_sync(sample_script, test_template)

        # Quality checks
        assert "Mock" not in result  # Should not contain mock indicators
        assert (
            len([line for line in result.split("\n") if line.strip()]) > 10
        )  # Substantial content

        # Check for Japanese content (matching our sample script)
        assert any(
            ord(char) > 127 for char in result
        )  # Contains non-ASCII (Japanese) characters
