from typing import Dict

from src.models.slide_template import SlideTemplate


class TemplateAnalyzer:
    """Simplified template analyzer for LangChain-based workflow"""

    def analyze_template(self, template: SlideTemplate) -> Dict[str, any]:
        """Basic template analysis - simplified for LangChain workflow"""
        try:
            content = template.read_slides_content()
            placeholders = template.extract_placeholders(content)

            return {
                "placeholders": placeholders,
                "total_placeholders": len(placeholders),
                "has_dynamic_content": len(placeholders) > 5,
            }
        except (FileNotFoundError, UnicodeDecodeError, OSError) as e:
            return {
                "error": str(e),
                "placeholders": set(),
                "total_placeholders": 0,
                "has_dynamic_content": False,
            }
