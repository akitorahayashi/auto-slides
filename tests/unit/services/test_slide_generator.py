class TestSlideGenerator:
    """Unit tests for SlideGenerator methods"""

    def test_template_filling_success(self, mock_slide_generator):
        """Test successful template filling with SlideTemplate"""
        from pathlib import Path

        from src.models.slide_template import SlideTemplate

        # Create a simple test template
        template = SlideTemplate(
            id="test",
            name="Test Template",
            description="Test Description",
            template_dir=Path("tests/templates/k2g4h1x9"),
            duration_minutes=5,
        )

        data = {
            "presentation_title": "Test Presentation",
            "author_name": "John Doe",
            "presentation_date": "2025-09-08",
            "main_topic": "Test Topic",
        }

        result = mock_slide_generator.fill_template(template, data)

        # Check that key placeholders are replaced
        assert "Test Presentation" in result
        assert "John Doe" in result
        assert "2025-09-08" in result
        assert isinstance(result, str)
        assert len(result) > 100  # Should have substantial content

    def test_template_filling_missing_keys(self, mock_slide_generator):
        """Test template filling with missing placeholders"""
        from pathlib import Path

        from src.models.slide_template import SlideTemplate

        template = SlideTemplate(
            id="test",
            name="Test Template",
            description="Test Description",
            template_dir=Path("tests/templates/k2g4h1x9"),
            duration_minutes=5,
        )

        # Limited data - some placeholders will be missing
        data = {"presentation_title": "Test Presentation", "author_name": "John Doe"}

        result = mock_slide_generator.fill_template(template, data)

        # Should still work with missing placeholders (safe_substitute)
        assert "Test Presentation" in result
        assert "John Doe" in result
        assert isinstance(result, str)

    def test_structured_parser(self):
        """Test structured response parser"""
        from src.services.structured_parser import StructuredResponseParser

        parser = StructuredResponseParser()

        sample_text = """TITLE: Test Presentation Title
POINT1: First key point
POINT2: Second key point  
POINT3: Third key point
CONCLUSION: Final summary
AUTHOR: Test Author
DATE: 2024-01-01"""

        result = parser.parse_enhanced_structure(sample_text, set())

        assert result["presentation_title"] == "Test Presentation Title"
        assert "First key point" in result["topic_1_content"]
        assert "Second key point" in result["topic_2_content"]
        assert result["author_name"] == "Test Author"
        assert result["presentation_date"] == "2024-01-01"

    def test_template_analyzer(self):
        """Test template analyzer"""
        from pathlib import Path

        from src.models.slide_template import SlideTemplate
        from src.services.template_analyzer import TemplateAnalyzer

        analyzer = TemplateAnalyzer()
        template = SlideTemplate(
            id="test",
            name="Test Template",
            description="Test Description",
            template_dir=Path("tests/templates/k2g4h1x9"),
            duration_minutes=5,
        )

        analysis = analyzer.analyze_template(template)

        assert "placeholders" in analysis
        assert "categories" in analysis
        assert analysis["total_placeholders"] > 0
        assert isinstance(analysis["placeholders"], set)
