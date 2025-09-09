from pathlib import Path
from string import Template
from typing import Any, Dict

from src.clients.ollama_client import OllamaClientManager
from src.models.slide_template import SlideTemplate
from src.services.structured_parser import StructuredResponseParser
from src.services.template_analyzer import TemplateAnalyzer


class SlideGenerator:
    """
    Simplified slide generator using structured natural language approach.
    Single LLM call + structured parsing instead of complex JSON chains.
    """

    def __init__(self):
        self.client, self.model = OllamaClientManager.create_client()
        self.parser = StructuredResponseParser()
        self.analyzer = TemplateAnalyzer()

    async def generate_content(
        self, script_content: str, template: SlideTemplate
    ) -> Dict[str, Any]:
        """Generate slide content using dynamic template analysis"""
        # Analyze template to understand required placeholders
        analysis = self.analyzer.analyze_template(template)

        if analysis.get("error"):
            # Fallback to basic prompt if analysis fails
            prompt = self.create_structured_prompt(script_content, template)
        else:
            # Use dynamic prompt based on template analysis
            prompt = self.analyzer.create_dynamic_prompt(
                script_content, template, analysis["placeholders"]
            )

        # Single LLM call
        response = await self.client.gen_batch(prompt, self.model)

        # Parse structured response with enhanced parser
        content = self.parser.parse_enhanced_structure(
            response, analysis.get("placeholders", set())
        )

        return content

    def fill_template(self, template: SlideTemplate, content: Dict[str, Any]) -> str:
        """Fill template with generated content"""
        template_content = template.read_markdown_content()

        # Use safe_substitute to handle missing placeholders gracefully
        template_obj = Template(template_content)
        return template_obj.safe_substitute(content)

    async def generate(self, script_content: str, template: SlideTemplate) -> str:
        """Main generation method - simple and fast"""
        # Step 1: Generate content with single LLM call
        content = await self.generate_content(script_content, template)

        # Step 2: Fill template
        result = self.fill_template(template, content)

        return result

    # Sync wrapper for compatibility
    def generate_sync(self, script_content: str, template: SlideTemplate) -> str:
        """Synchronous wrapper for generate method"""
        import asyncio

        return asyncio.run(self.generate(script_content, template))


# Test function
async def test_slide_generator():
    """Test the slide generator"""
    generator = SlideGenerator()

    template = SlideTemplate(
        id="test",
        name="Test Template",
        description="Test Description",
        template_dir=Path("src/templates/k2g4h1x9"),
        duration_minutes=5,
    )

    script = """
    Pythonの非同期プログラミングについて説明します。
    asyncioライブラリを使用することで、I/Oバウンドなタスクを効率的に処理できます。
    基本的なasync/await構文から、実際のWebアプリケーションでの活用例まで紹介します。
    """

    result = await generator.generate(script, template)

    print("=== GENERATED SLIDE ===")
    print(result[:500] + "..." if len(result) > 500 else result)
    print("\n=== STATS ===")
    print(f"Total length: {len(result)}")
    print(f"Remaining placeholders: {result.count('${')}")

    return result


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_slide_generator())
