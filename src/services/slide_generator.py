import asyncio
import json
from pathlib import Path
from string import Template
from typing import Any, Dict

from src.clients.ollama_client import OllamaClientManager
from src.models.slide_template import SlideTemplate


class SlideGenerator:
    """
    Generates presentation slides by running a two-stage LLM chain.
    Uses the unified olm-api SDK v1.4.0 interface.
    """

    def __init__(self):
        self.client, self.model = OllamaClientManager.create_client()
        self.prompts_dir = Path("src/static/prompts")

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON-formatted response"""
        try:
            text = text.strip()
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                if end != -1:
                    text = text[start:end].strip()
            elif "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                if end != -1:
                    text = text[start:end].strip()
            return json.loads(text)
        except (json.JSONDecodeError, ValueError) as e:
            return {"error": f"JSON parse failed: {str(e)}", "raw_text": text}

    async def _analyze_slides(self, template: SlideTemplate) -> Dict[str, Any]:
        """Stage 1: Analyze slide structure"""
        prompt_path = self.prompts_dir / "01_analyze_slides.md"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt not found: {prompt_path}")

        prompt_template = prompt_path.read_text(encoding="utf-8")
        template_content = template.read_markdown_content()

        filled_prompt = Template(prompt_template).substitute(
            template_content=template_content,
            duration_minutes=template.duration_minutes,
        )

        response = await self.client.gen_batch(
            prompt=filled_prompt, model_name=self.model
        )
        return self._parse_json_response(response)

    async def _generate_content(
        self, script_content: str, analysis: Dict[str, Any], template: SlideTemplate
    ) -> Dict[str, Any]:
        """Stage 2: Generate content"""
        prompt_path = self.prompts_dir / "02_generate_content.md"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt not found: {prompt_path}")

        prompt_template = prompt_path.read_text(encoding="utf-8")

        filled_prompt = Template(prompt_template).substitute(
            script_content=script_content,
            slide_analysis=json.dumps(analysis, ensure_ascii=False, indent=2),
            duration_minutes=template.duration_minutes,
        )

        response = await self.client.gen_batch(
            prompt=filled_prompt, model_name=self.model
        )
        return self._parse_json_response(response)


    def _fill_template(
        self, template_content: str, placeholder_data: Dict[str, Any]
    ) -> str:
        """Fill the template with placeholders"""
        try:
            if (
                isinstance(placeholder_data, dict)
                and "generated_content" in placeholder_data
            ):
                placeholder_data = placeholder_data["generated_content"]

            template = Template(template_content)
            return template.safe_substitute(placeholder_data)
        except Exception as e:
            print(f"Template filling failed: {e}")
            return template_content

    async def _run_two_stage_chain(
        self, script_content: str, template: SlideTemplate
    ) -> str:
        """Run two-stage chain"""
        analysis = await self._analyze_slides(template)
        if "error" in analysis:
            raise RuntimeError(f"Stage 1 failed: {analysis['error']}")

        content = await self._generate_content(script_content, analysis, template)
        if "error" in content:
            raise RuntimeError(f"Stage 2 failed: {content['error']}")

        template_content = template.read_markdown_content()
        placeholder_data = content.get("generated_content", content)

        return self._fill_template(template_content, placeholder_data)

    def generate(self, script_content: str, template: SlideTemplate) -> str:
        """Main function: Generate presentation"""
        return asyncio.run(self._run_two_stage_chain(script_content, template))
