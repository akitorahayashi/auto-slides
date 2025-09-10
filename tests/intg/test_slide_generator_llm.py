"""
Integration tests for SlideGenerator with real LLM clients.
Tests the full 2-stage LLM chain with external dependencies.
"""

import asyncio
import os
from pathlib import Path
from unittest.mock import patch

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
        """Test SlideGenerator with mock chain (fast, no external dependency)"""
        # Use mock chain
        from dev.mocks.mock_slide_generator import MockSlideGenerator

        generator = MockSlideGenerator()
        result = generator.generate_sync(sample_script, test_template)

        # Basic validation
        assert isinstance(result, str)
        assert len(result) > 100  # Should have substantial content
        assert "---" in result  # Marp slide separators

        # Check that it's properly formatted Marp content
        assert "marp: true" in result
        assert "theme:" in result

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
        """Test the new async generation method with chain workflow"""
        with patch("streamlit.secrets") as mock_secrets:
            # Mock streamlit secrets for testing
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": "true",
                "OLLAMA_MODEL": "test-model",
            }.get(key, default)

            async def run_test():
                generator = SlideGenerator()

                # Test full generation chain
                result = await generator.generate_slide(sample_script, test_template)
                assert isinstance(result, str)
                assert len(result) > 100

                # Verify it contains expected Marp format
                assert "---" in result
                assert "marp: true" in result or "theme:" in result

            # Run the async test
            asyncio.run(run_test())

    def test_chain_workflow_validation(self):
        """Test the 4-phase agentic chain workflow"""
        from src.chains.slide_gen_chain import SlideGenChain

        chain = SlideGenChain()

        # Verify chain components exist
        assert hasattr(chain, "analysis_chain")
        assert hasattr(chain, "planning_chain")
        assert hasattr(chain, "generation_chain")
        assert hasattr(chain, "validation_chain")

        # Verify LLM and parser components
        assert hasattr(chain, "llm")
        assert hasattr(chain, "json_parser")
        assert hasattr(chain, "prompt_service")

    def test_placeholder_extraction_and_rendering(self):
        """Test placeholder extraction and template rendering"""
        from pathlib import Path

        from src.models import SlideTemplate

        # Create a real SlideTemplate instance
        template = SlideTemplate(
            id="test_template",
            name="Test Template",
            description="Test template for integration tests",
            template_dir=Path("/tmp/test_template"),
            duration_minutes=10,
        )

        # Test placeholder extraction
        template_content = "Hello ${name}, welcome to ${event} at ${location}!"
        placeholders = template.extract_placeholders(template_content)
        assert placeholders == {"name", "event", "location"}

        # Test template rendering
        content_dict = {"name": "John", "event": "Conference", "location": "Tokyo"}
        result = template.render_template(template_content, content_dict)
        assert result == "Hello John, welcome to Conference at Tokyo!"

        # Test with missing placeholder
        incomplete_dict = {"name": "John", "event": "Conference"}
        result = template.render_template(template_content, incomplete_dict)
        assert "John" in result
        assert "Conference" in result
        assert "${location}" in result  # Should remain unreplaced

    @pytest.mark.skipif(
        str(st.secrets.get("DEBUG", "false")).lower() == "true",
        reason="Skipping LLM response validation in DEBUG mode",
    )
    def test_llm_response_quality(self, sample_script, test_template):
        """Test that LLM responses meet quality expectations with chain workflow"""
        generator = SlideGenerator()
        result = generator.generate_sync(sample_script, test_template)

        # Quality checks
        assert isinstance(result, str)
        assert len(result) > 100  # Substantial content
        assert "---" in result  # Marp format

        # Check for slide structure
        lines = result.split("\n")
        non_empty_lines = [line for line in lines if line.strip()]
        assert len(non_empty_lines) > 10  # Should have substantial content

        # Check for Japanese content (matching our sample script)
        assert any(
            ord(char) > 127 for char in result
        )  # Contains non-ASCII (Japanese) characters
