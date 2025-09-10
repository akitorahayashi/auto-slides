"""Tests for PromptService"""

import tempfile
from pathlib import Path

import pytest

from src.backend.services import PromptService


class TestPromptService:
    """Test PromptService functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary directory for test templates
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = Path(self.temp_dir) / "prompts"
        self.template_dir.mkdir()

        # Create test template files
        self.create_test_templates()

        self.service = PromptService(str(self.template_dir))

    def teardown_method(self):
        """Clean up test files"""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def create_test_templates(self):
        """Create test template files"""
        templates = {
            "analyze_script.md": "Analyze this script: $script_content\nLimit: $argument_flow_limit characters",
            "compose_slides.md": "Compose slides for: $script_content\nAnalysis: $analysis_result\nFunctions: $slide_functions_summary\nTarget: $target_slide_count slides",
            "generate_parameters.md": "Generate parameters for: $slide_name\nPurpose: $function_purpose\nSignature: $function_signature\nArgs: $arguments_list\nScript: $script_content\nAnalysis: $analysis_result",
        }

        for filename, content in templates.items():
            (self.template_dir / filename).write_text(content)

    def test_init_with_default_template_dir(self):
        """Test initialization with default template directory"""
        service = PromptService()
        assert service.template_dir == Path("src/backend/static/prompts")

    def test_init_with_custom_template_dir(self):
        """Test initialization with custom template directory"""
        custom_dir = "/custom/path"
        service = PromptService(custom_dir)
        assert service.template_dir == Path(custom_dir)

    def test_build_analysis_prompt(self):
        """Test building analysis prompt"""
        input_dict = {"script_content": "This is a test script"}
        result = self.service.build_analysis_prompt(input_dict)

        assert "prompt" in result
        assert "script_content" in result
        expected_limit = len("This is a test script") // 4
        expected_prompt = f"Analyze this script: This is a test script\nLimit: {expected_limit} characters"
        assert result["prompt"] == expected_prompt

    def test_build_composition_prompt(self):
        """Test building composition prompt"""
        input_dict = {
            "script_content": "Test script",
            "analysis_result": {"summary": "Analysis"},
            "slide_functions_summary": "Function list",
        }
        result = self.service.build_composition_prompt(input_dict)

        assert "prompt" in result
        expected_prompt = 'Compose slides for: Test script\nAnalysis: {"summary": "Analysis"}\nFunctions: Function list\nTarget: 2 slides'
        assert result["prompt"] == expected_prompt

    def test_build_parameter_prompt(self):
        """Test building parameter prompt"""
        input_dict = {
            "script_content": "Test script",
            "analysis_result": {"summary": "Analysis"},
            "slide_name": "test_function",
            "function_info": {
                "docstring": "Test function purpose\nMore details",
                "signature": "test_function(arg1, arg2)",
                "args_info": {"arg1": "First argument", "arg2": "Second argument"},
            },
        }
        result = self.service.build_parameter_prompt(input_dict)

        assert "prompt" in result
        expected_prompt = 'Generate parameters for: test_function\nPurpose: Test function purpose\nSignature: test_function(arg1, arg2)\nArgs:   - arg1: First argument\n  - arg2: Second argument\nScript: Test script\nAnalysis: {"summary": "Analysis"}'
        assert result["prompt"] == expected_prompt

    def test_build_parameter_prompt_empty_docstring(self):
        """Test building parameter prompt with empty docstring"""
        input_dict = {
            "script_content": "Test script",
            "analysis_result": {"summary": "Analysis"},
            "slide_name": "test_function",
            "function_info": {
                "docstring": "",
                "signature": "test_function()",
                "args_info": {},
            },
        }
        result = self.service.build_parameter_prompt(input_dict)

        assert "prompt" in result
        assert "Purpose: " in result["prompt"]

    def test_build_parameter_prompt_no_docstring(self):
        """Test building parameter prompt with no docstring key"""
        input_dict = {
            "script_content": "Test script",
            "analysis_result": {"summary": "Analysis"},
            "slide_name": "test_function",
            "function_info": {"signature": "test_function()", "args_info": {}},
        }
        result = self.service.build_parameter_prompt(input_dict)

        assert "prompt" in result
        assert "Purpose: " in result["prompt"]

    def test_build_prompt_preserves_input_dict(self):
        """Test that building prompts preserves original input dictionary"""
        original_input = {"script_content": "Test", "other_key": "value"}
        result = self.service.build_analysis_prompt(original_input)

        # Check that original keys are preserved
        assert result["script_content"] == "Test"
        assert result["other_key"] == "value"
        # Check that prompt is added
        assert "prompt" in result

    def test_missing_template_file_raises_error(self):
        """Test that missing template file raises FileNotFoundError"""
        # Remove a template file
        (self.template_dir / "analyze_script.md").unlink()

        input_dict = {"script_content": "Test"}
        with pytest.raises(FileNotFoundError):
            self.service.build_analysis_prompt(input_dict)
