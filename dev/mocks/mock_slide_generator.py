import re
from string import Template
from typing import Set

from src.models.slide_template import SlideTemplate


class MockSlideGenerator:
    """Mock of the LangChain-powered slide generation workflow"""

    def __init__(self):
        print("🤖 MockSlideGenerator initialized.")

    async def generate_slide(self, script_content: str, template: SlideTemplate) -> str:
        """Mocks the agentic slide generation workflow"""

        template_content = template.read_markdown_content()
        placeholders = self._extract_placeholders(template_content)

        print("🔍 MOCK Agent: Analyzing script content...")
        # Mock analysis result
        analysis_result = {"main_theme": "Mock Theme", "title": "Mock Title"}
        print(f"📊 Mock Analysis: {analysis_result}")

        print("🎯 MOCK Agent: Planning content strategy...")
        # Mock content plan
        content_plan = {
            "generation_strategy": "Mock Strategy: Fill all placeholders with mock data."
        }
        print(f"📋 Mock Strategy: {content_plan}")

        print("✍️ MOCK Agent: Generating slide content...")
        # Mock content generation
        generated_content = {p: f"Mock content for {p}" for p in placeholders}
        print(f"📝 Mock Generated Content: {generated_content}")

        print("✅ MOCK Agent: Validating content quality...")
        # Mock validation
        validation_result = {"approved": True, "reason": "All mock data is valid."}
        print("🎉 MOCK Agent: Content approved!")

        final_content = generated_content
        return self._render_template(template_content, final_content)

    def generate_sync(self, script_content: str, template: SlideTemplate) -> str:
        """Synchronous wrapper for the mock generator"""
        import asyncio

        return asyncio.run(self.generate_slide(script_content, template))

    def _extract_placeholders(self, template_content: str) -> Set[str]:
        """Extract all ${placeholder} variables from template content"""
        pattern = r"\$\{([^}]+)\}"
        matches = re.findall(pattern, template_content)
        return set(matches)

    def _render_template(self, template_content: str, content_dict: dict) -> str:
        """Render template with content dictionary"""
        template = Template(template_content)
        return template.safe_substitute(content_dict)
