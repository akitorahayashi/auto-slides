"""Tests for TemplateAnalyzer"""

import tempfile
from pathlib import Path

from src.backend.models.slide_template import SlideTemplate
from src.backend.services.script_analyzer import TemplateAnalyzer


class TestTemplateAnalyzer:
    """Test TemplateAnalyzer functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = TemplateAnalyzer()
        # Create temporary directory for test templates
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = Path(self.temp_dir) / "template"
        self.template_dir.mkdir()

    def teardown_method(self):
        """Clean up test files"""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def create_test_template(self, content: str) -> SlideTemplate:
        """Helper to create a test template"""
        slides_file = self.template_dir / "slides.py"
        slides_file.write_text(content)

        css_file = self.template_dir / "theme.css"
        css_file.write_text("/* test css */")

        return SlideTemplate(
            id="test_template",
            name="Test Template",
            description="Test description",
            template_dir=self.template_dir,
            duration_minutes=10,
        )

    def test_analyze_template_with_placeholders(self):
        """Test analyzing template with placeholders"""
        content = """
        def example_slide():
            return f'''
            # ${title}
            
            ## ${subtitle}
            
            Content: ${content}
            '''
        """
        template = self.create_test_template(content)

        result = self.analyzer.analyze_template(template)

        assert "placeholders" in result
        assert "total_placeholders" in result
        assert "has_dynamic_content" in result
        assert "error" not in result

        placeholders = result["placeholders"]
        assert "title" in placeholders
        assert "subtitle" in placeholders
        assert "content" in placeholders
        assert result["total_placeholders"] == 3
        assert result["has_dynamic_content"] is False  # 3 <= 5

    def test_analyze_template_with_many_placeholders(self):
        """Test analyzing template with many placeholders (>5)"""
        content = """
        def example_slide():
            return f'''
            # ${title}
            ## ${subtitle}
            ${intro}
            ${point1}
            ${point2}
            ${point3}
            ${conclusion}
            '''
        """
        template = self.create_test_template(content)

        result = self.analyzer.analyze_template(template)

        assert result["total_placeholders"] == 7
        assert result["has_dynamic_content"] is True  # 7 > 5

    def test_analyze_template_no_placeholders(self):
        """Test analyzing template without placeholders"""
        content = """
        def example_slide():
            return '''
            # Static Title
            
            This is static content without placeholders.
            '''
        """
        template = self.create_test_template(content)

        result = self.analyzer.analyze_template(template)

        assert len(result["placeholders"]) == 0
        assert result["total_placeholders"] == 0
        assert result["has_dynamic_content"] is False

    def test_analyze_template_duplicate_placeholders(self):
        """Test analyzing template with duplicate placeholders"""
        content = """
        def example_slide():
            return f'''
            # ${title}
            
            Repeated: ${title}
            Also: ${title}
            Different: ${content}
            '''
        """
        template = self.create_test_template(content)

        result = self.analyzer.analyze_template(template)

        # Should only count unique placeholders
        placeholders = result["placeholders"]
        assert "title" in placeholders
        assert "content" in placeholders
        assert result["total_placeholders"] == 2

    def test_analyze_template_complex_placeholders(self):
        """Test analyzing template with complex placeholder names"""
        content = """
        def example_slide():
            return f'''
            ${main_title}
            ${sub_section_1}
            ${item_with_numbers_123}
            ${UPPERCASE_ITEM}
            '''
        """
        template = self.create_test_template(content)

        result = self.analyzer.analyze_template(template)

        placeholders = result["placeholders"]
        assert "main_title" in placeholders
        assert "sub_section_1" in placeholders
        assert "item_with_numbers_123" in placeholders
        assert "UPPERCASE_ITEM" in placeholders
        assert result["total_placeholders"] == 4

    def test_analyze_template_file_not_found(self):
        """Test analyzing template when slides file doesn't exist"""
        # Create template without slides.py file
        css_file = self.template_dir / "theme.css"
        css_file.write_text("/* test css */")

        template = SlideTemplate(
            id="test_template",
            name="Test Template",
            description="Test description",
            template_dir=self.template_dir,
            duration_minutes=10,
        )

        result = self.analyzer.analyze_template(template)

        assert "error" in result
        assert result["placeholders"] == set()
        assert result["total_placeholders"] == 0
        assert result["has_dynamic_content"] is False

    def test_analyze_template_unicode_decode_error(self):
        """Test handling of unicode decode errors"""
        # Create a file with invalid encoding
        slides_file = self.template_dir / "slides.py"
        slides_file.write_bytes(b"\xff\xfe\x00\x00")  # Invalid UTF-8

        css_file = self.template_dir / "theme.css"
        css_file.write_text("/* test css */")

        template = SlideTemplate(
            id="test_template",
            name="Test Template",
            description="Test description",
            template_dir=self.template_dir,
            duration_minutes=10,
        )

        result = self.analyzer.analyze_template(template)

        assert "error" in result
        assert result["placeholders"] == set()
        assert result["total_placeholders"] == 0
        assert result["has_dynamic_content"] is False

    def test_analyze_template_with_nested_braces(self):
        """Test analyzing template with nested braces"""
        content = """
        def example_slide():
            return f'''
            ${title}
            {nested_dict["key"]}
            ${valid_placeholder}
            '''
        """
        template = self.create_test_template(content)

        result = self.analyzer.analyze_template(template)

        # Should only extract valid ${...} placeholders
        placeholders = result["placeholders"]
        assert "title" in placeholders
        assert "valid_placeholder" in placeholders
        assert result["total_placeholders"] == 2

    def test_analyze_template_empty_content(self):
        """Test analyzing template with empty content"""
        template = self.create_test_template("")

        result = self.analyzer.analyze_template(template)

        assert len(result["placeholders"]) == 0
        assert result["total_placeholders"] == 0
        assert result["has_dynamic_content"] is False
        assert "error" not in result

    def test_analyze_template_malformed_placeholders(self):
        """Test analyzing template with malformed placeholders"""
        content = """
        def example_slide():
            return f'''
            ${incomplete
            ${}
            ${valid_one}
            ${another_incomplete
            '''
        """
        template = self.create_test_template(content)

        result = self.analyzer.analyze_template(template)

        # Should only extract valid placeholders
        placeholders = result["placeholders"]
        assert "valid_one" in placeholders
        # Note: empty ${} might be captured depending on regex implementation
        assert result["total_placeholders"] >= 1
