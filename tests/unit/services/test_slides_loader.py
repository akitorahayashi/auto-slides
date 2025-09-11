"""Tests for SlidesLoader"""

from unittest.mock import Mock, patch

import pytest

from src.backend.services import SlidesLoader


class TestSlidesLoader:
    """Test SlidesLoader functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.loader = SlidesLoader()

    @patch("importlib.import_module")
    def test_load_template_functions_success(self, mock_import):
        """Test successful loading of template functions"""

        # Create mock module with test functions
        def test_function(arg1: str, arg2: int):
            """Test function description

            Args:
                arg1: First argument description
                arg2: Second argument description

            Returns:
                str: Return value description
            """
            return f"test result: {arg1}, {arg2}"

        mock_module = Mock()
        mock_module.__all__ = ["test_function"]
        mock_module.test_function = test_function
        mock_import.return_value = mock_module

        result = self.loader.load_template_functions("test_template")

        assert "test_function" in result
        function_info = result["test_function"]

        assert "function" in function_info
        assert "docstring" in function_info
        assert "signature" in function_info
        assert "args_info" in function_info

        assert function_info["function"] == test_function
        assert "Test function description" in function_info["docstring"]
        assert "arg1: str" in function_info["signature"]
        assert "arg2: int" in function_info["signature"]

        args_info = function_info["args_info"]
        assert "arg1" in args_info
        assert "arg2" in args_info
        assert args_info["arg1"] == "First argument description"
        assert args_info["arg2"] == "Second argument description"

    @patch("importlib.import_module")
    def test_load_template_functions_no_all_attribute(self, mock_import):
        """Test loading when module has no __all__ attribute"""
        mock_module = Mock()
        # Remove __all__ attribute
        del mock_module.__all__
        mock_import.return_value = mock_module

        result = self.loader.load_template_functions("test_template")

        assert result == {}

    @patch("importlib.import_module")
    def test_load_template_functions_import_error(self, mock_import):
        """Test handling of import errors"""
        mock_import.side_effect = ImportError("Module not found")

        with pytest.raises(ImportError, match="Cannot load template 'test_template'"):
            self.loader.load_template_functions("test_template")

    @patch("importlib.import_module")
    def test_load_template_functions_empty_docstring(self, mock_import):
        """Test loading function with empty docstring"""

        def empty_doc_function():
            pass

        mock_module = Mock()
        mock_module.__all__ = ["empty_doc_function"]
        mock_module.empty_doc_function = empty_doc_function
        mock_import.return_value = mock_module

        result = self.loader.load_template_functions("test_template")

        function_info = result["empty_doc_function"]
        assert function_info["docstring"] == ""
        assert function_info["args_info"] == {}

    @patch("importlib.import_module")
    def test_parse_function_args_complex_docstring(self, mock_import):
        """Test parsing arguments from complex docstring"""

        def complex_function(param1, param2, param3):
            """Complex function with detailed documentation

            This function does something complex.

            Args:
                param1: First parameter with description
                param2: Second parameter with colon: in description
                param3: Third parameter
                    with multiline description

            Returns:
                dict: A dictionary containing results

            Raises:
                ValueError: If parameters are invalid
            """
            pass

        mock_module = Mock()
        mock_module.__all__ = ["complex_function"]
        mock_module.complex_function = complex_function
        mock_import.return_value = mock_module

        result = self.loader.load_template_functions("test_template")

        args_info = result["complex_function"]["args_info"]
        assert "param1" in args_info
        assert "param2" in args_info
        assert "param3" in args_info
        assert args_info["param1"] == "First parameter with description"
        assert "colon:" in args_info["param2"]

    @patch("importlib.import_module")
    def test_create_slide_functions_summary(self, mock_import):
        """Test creating function catalog"""

        def slide_function(title: str, content: str):
            """Create a slide with title and content

            Args:
                title: The slide title
                content: The slide content
            """
            return f"# {title}\n\n{content}"

        mock_module = Mock()
        mock_module.__all__ = ["slide_function"]
        mock_module.slide_function = slide_function
        mock_import.return_value = mock_module

        catalog = self.loader.create_slide_functions_summary("test_template")

        assert "Function: slide_function" in catalog
        assert "Purpose: Create a slide with title and content" in catalog
        assert "Signature:" in catalog
        assert "Arguments:" in catalog
        assert "title: The slide title" in catalog
        assert "content: The slide content" in catalog

    @patch("importlib.import_module")
    def test_create_slide_functions_summary_no_description(self, mock_import):
        """Test creating catalog for function without description"""

        def no_desc_function():
            pass

        mock_module = Mock()
        mock_module.__all__ = ["no_desc_function"]
        mock_module.no_desc_function = no_desc_function
        mock_import.return_value = mock_module

        catalog = self.loader.create_slide_functions_summary("test_template")

        assert "Function: no_desc_function" in catalog
        # Empty purpose should result in empty string, not "No description"
        assert "Purpose:" in catalog

    @patch("importlib.import_module")
    def test_get_function_by_name(self, mock_import):
        """Test getting specific function by name"""

        def target_function():
            return "target result"

        def other_function():
            return "other result"

        mock_module = Mock()
        mock_module.__all__ = ["target_function", "other_function"]
        mock_module.target_function = target_function
        mock_module.other_function = other_function
        mock_import.return_value = mock_module

        result = self.loader.get_function_by_name("test_template", "target_function")

        assert result == target_function
        assert result() == "target result"

    @patch("importlib.import_module")
    def test_get_function_by_name_not_found(self, mock_import):
        """Test getting function that doesn't exist"""
        mock_module = Mock()
        mock_module.__all__ = ["existing_function"]
        mock_import.return_value = mock_module

        result = self.loader.get_function_by_name(
            "test_template", "nonexistent_function"
        )

        assert result is None

    @patch("importlib.import_module")
    def test_list_available_functions(self, mock_import):
        """Test listing all available function names"""
        mock_module = Mock()
        mock_module.__all__ = ["function1", "function2", "function3"]
        mock_import.return_value = mock_module

        result = self.loader.list_available_functions("test_template")

        assert result == ["function1", "function2", "function3"]

    @patch("importlib.import_module")
    def test_list_available_functions_empty(self, mock_import):
        """Test listing functions when none available"""
        mock_module = Mock()
        mock_module.__all__ = []
        mock_import.return_value = mock_module

        result = self.loader.list_available_functions("test_template")

        assert result == []

    def test_parse_function_args_no_args_section(self):
        """Test parsing docstring without Args section"""

        def no_args_function():
            """Function without Args section

            This function has no arguments documented.

            Returns:
                str: Some return value
            """
            pass

        args_info = self.loader._parse_function_args(no_args_function)
        assert args_info == {}

    def test_parse_function_args_malformed_docstring(self):
        """Test parsing malformed docstring"""

        def malformed_function():
            """Malformed docstring

            Args:
                param_without_colon
                param_with_colon: but no description
                : colon_at_start
            """
            pass

        args_info = self.loader._parse_function_args(malformed_function)

        # Should handle malformed entries gracefully
        assert "param_with_colon" in args_info
        assert args_info["param_with_colon"] == "but no description"

    @patch("importlib.import_module")
    def test_create_slide_functions_summary_multiple_functions(self, mock_import):
        """Test creating catalog with multiple functions"""

        def func1():
            """First function"""
            pass

        def func2():
            """Second function"""
            pass

        mock_module = Mock()
        mock_module.__all__ = ["func1", "func2"]
        mock_module.func1 = func1
        mock_module.func2 = func2
        mock_import.return_value = mock_module

        catalog = self.loader.create_slide_functions_summary("test_template")

        assert "Function: func1" in catalog
        assert "Function: func2" in catalog
        assert "=" * 50 in catalog  # Separator between functions
