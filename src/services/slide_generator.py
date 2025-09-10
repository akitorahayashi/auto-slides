import re
from typing import Set

from src.models.slide_template import SlideTemplate


class SlideGenerator:
    """LangChain-powered agentic slide generation workflow"""

    def __init__(self):
        from src.chains.slide_gen_chain import SlideGenChain
        self.chain = SlideGenChain()

    async def generate_slide(self, script_content: str, template: SlideTemplate) -> str:
        """Agentic slide generation workflow with observation and reasoning"""

        template_content = template.read_markdown_content()
        placeholders = extract_placeholders(template_content)

        try:
            # Phase 1: Analyze Script (Observation)
            print("🔍 Agent: Analyzing script content...")
            analysis_result = await self.chain.analysis_chain.ainvoke(
                {"script_content": script_content}
            )
            print(f"📊 Analysis: {analysis_result.get('main_theme', 'Unknown theme')}")

            # Phase 2: Plan Content Strategy (Reasoning)
            print("🎯 Agent: Planning content strategy...")
            content_plan = await self.chain.planning_chain.ainvoke(
                {"analysis_result": analysis_result, "placeholders": list(placeholders)}
            )
            print(
                f"📋 Strategy: {content_plan.get('generation_strategy', 'Default strategy')}"
            )

            # Phase 3: Generate Content (Action)
            print("✍️ Agent: Generating slide content...")
            generated_content = await self.chain.generation_chain.ainvoke(
                {
                    "script_content": script_content,
                    "placeholders": list(placeholders),
                    "content_plan": content_plan,
                }
            )

            # Phase 4: Validate and Improve (Self-reflection)
            print("✅ Agent: Validating content quality...")
            validation_result = await self.chain.validation_chain.ainvoke(
                {
                    "generated_content": generated_content,
                    "analysis_result": analysis_result,
                    "content_plan": content_plan,
                }
            )

            # Use validated content
            if validation_result.get("approved", False):
                final_content = generated_content
                print("🎉 Agent: Content approved!")
            else:
                print(
                    "⚠️ Agent: Content needs improvement, using generated content anyway..."
                )
                final_content = generated_content

        except Exception as e:
            print(f"🚨 Agent error: {e}")
            raise e

        # Final: Render template
        return render_template(template_content, final_content)

    def generate_sync(self, script_content: str, template: SlideTemplate) -> str:
        """Synchronous wrapper"""
        import asyncio

        return asyncio.run(self.generate_slide(script_content, template))


def extract_placeholders(template_content: str) -> Set[str]:
    """Extract all ${placeholder} variables from template content"""
    pattern = r"\$\{([^}]+)\}"
    matches = re.findall(pattern, template_content)
    return set(matches)


def render_template(template_content: str, content_dict: dict) -> str:
    """Render template with content dictionary"""
    from string import Template

    template = Template(template_content)
    return template.safe_substitute(content_dict)
