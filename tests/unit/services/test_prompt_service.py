import tempfile
from pathlib import Path

import pytest

from src.services import PromptService


class TestPromptService:
    """Unit tests for PromptService using real service (no external dependencies)"""

    @pytest.fixture
    def temp_template_dir(self):
        """Create temporary directory with test prompt templates"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test template files
            (temp_path / "analyze_script.md").write_text(
                "Analyze this script: ${script_content}", encoding="utf-8"
            )
            (temp_path / "plan_content.md").write_text(
                "Plan based on: ${analysis_result} and ${placeholders_list}",
                encoding="utf-8",
            )
            (temp_path / "generate_slide_content.md").write_text(
                "Generate content for: ${script_content}\nPlaceholders: ${placeholders_list}\nExample: ${json_example}",
                encoding="utf-8",
            )
            (temp_path / "validate_content.md").write_text(
                "Validate: ${generated_content} against ${analysis_result} and ${content_plan}",
                encoding="utf-8",
            )

            yield str(temp_path)

    @pytest.fixture
    def prompt_service(self, temp_template_dir):
        """Create a PromptService instance with test templates"""
        return PromptService(template_dir=temp_template_dir)

    def test_initialization_default_dir(self):
        """Test PromptService initialization with default template directory"""
        service = PromptService()
        assert service.template_dir == Path("src/static/prompts")

    def test_initialization_custom_dir(self, prompt_service, temp_template_dir):
        """Test PromptService initialization with custom template directory"""
        assert str(prompt_service.template_dir) == temp_template_dir

    def test_build_prompt_success(self, temp_template_dir):
        """Test successful prompt building with real template files"""
        service = PromptService(template_dir=temp_template_dir)

        # Test with existing analyze_script.md template
        substitutions = {"script_content": "Test script content"}
        result = service._build_prompt("analyze_script.md", substitutions)

        assert result == "Analyze this script: Test script content"

    def test_build_analysis_prompt(self, prompt_service):
        """Test building analysis prompt with real service"""
        input_dict = {"script_content": "This is a test script"}
        result = prompt_service.build_analysis_prompt(input_dict)

        expected = {
            "script_content": "This is a test script",
            "prompt": "Analyze this script: This is a test script",
        }
        assert result == expected

    def test_build_planning_prompt(self, prompt_service):
        """Test building planning prompt with real service"""
        input_dict = {
            "analysis_result": {"theme": "AI", "points": ["ML", "DL"]},
            "placeholders": ["title", "content"],
        }
        result = prompt_service.build_planning_prompt(input_dict)

        assert "prompt" in result
        assert "theme" in result["prompt"]
        assert "- title" in result["prompt"]
        assert "- content" in result["prompt"]

    def test_build_generation_prompt(self, prompt_service):
        """Test building generation prompt with real service"""
        input_dict = {
            "script_content": "Test script",
            "placeholders": ["title", "content"],
            "content_plan": {"strategy": "educational"},
        }
        result = prompt_service.build_generation_prompt(input_dict)

        assert "prompt" in result
        assert "Test script" in result["prompt"]
        assert "- title" in result["prompt"]
        assert "- content" in result["prompt"]

    def test_build_validation_prompt(self, prompt_service):
        """Test building validation prompt with real service"""
        input_dict = {
            "script_content": "Original script",
            "generated_content": {"title": "Test Title"},
            "placeholders": ["title"],
            "analysis_result": {"theme": "Test"},
            "content_plan": {"strategy": "test"},
        }
        result = prompt_service.build_validation_prompt(input_dict)

        assert "prompt" in result
        assert "Test Title" in result["prompt"]

    def test_build_prompt_missing_substitution(self, temp_template_dir):
        """Test prompt building with missing substitution values"""
        service = PromptService(template_dir=temp_template_dir)

        # Only provide partial substitutions for analyze_script.md
        substitutions = {}  # Missing script_content

        with pytest.raises(KeyError):
            service._build_prompt("analyze_script.md", substitutions)

    def test_build_prompt_file_not_found(self, prompt_service):
        """Test prompt building when template file doesn't exist"""
        with pytest.raises(FileNotFoundError):
            prompt_service._build_prompt("nonexistent.md", {})

    def test_prompt_service_with_real_templates(self):
        """Test PromptService with actual template files if they exist"""
        service = PromptService()  # Use default template directory

        # Test if real template files exist and work
        if (service.template_dir / "analyze_script.md").exists():
            input_dict = {"script_content": "Real test script"}
            result = service.build_analysis_prompt(input_dict)

            assert "prompt" in result
            assert "Real test script" in result["prompt"]
