import asyncio
import json
import os
from pathlib import Path
from string import Template
from typing import Any, Dict

import streamlit as st

from src.models.slide_template import SlideTemplate

try:
    from sdk.olm_api_client import (
        MockOllamaApiClient,
        OllamaApiClient,
        OllamaClientProtocol,
    )
except ImportError:
    raise ImportError("olm-api package is required")


class SlideGenerator:
    """
    Generates presentation slides by running a two-stage LLM chain.
    """

    def __init__(self):
        self.client = self._get_client()
        self.model = self._get_model()
        self.prompts_dir = Path("src/static/prompts")

    def _get_client(self) -> OllamaClientProtocol:
        """Get client (recommended olm-api pattern + demo responses support)"""
        debug = st.secrets.get("DEBUG", os.getenv("DEBUG", "true")).lower() == "true"
        use_demo = (
            st.secrets.get(
                "USE_DEMO_RESPONSES", os.getenv("USE_DEMO_RESPONSES", "false")
            ).lower()
            == "true"
        )

        if debug:
            if use_demo:

                def _read_mock_response(filename: str) -> str:
                    return (
                        Path(__file__).parent.parent
                        / "static"
                        / "mock_responses"
                        / filename
                    ).read_text(encoding="utf-8")

                responses = [
                    _read_mock_response("stage1_analyze_slides.txt"),
                    _read_mock_response("stage2_generate_content.txt"),
                ]
                return MockOllamaApiClient(responses=responses, token_delay=0)
            else:
                return MockOllamaApiClient(token_delay=0)
        else:
            api_url = st.secrets.get("OLM_API_ENDPOINT", os.getenv("OLM_API_ENDPOINT"))
            if not api_url:
                print("Warning: OLM_API_ENDPOINT not set, using MockOllamaApiClient")
                return MockOllamaApiClient(token_delay=0)
            return OllamaApiClient(api_url=api_url)

    def _get_model(self) -> str:
        """Get model name"""
        return st.secrets.get("OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "qwen3:0.6b"))

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

        response = await self.client.gen_batch(prompt=filled_prompt, model=self.model)
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

        response = await self.client.gen_batch(prompt=filled_prompt, model=self.model)
        return self._parse_json_response(response)

    def _ensure_placeholder_defaults(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Ensure default placeholder values"""
        defaults = {
            "presentation_title": "Title",
            "author_name": "Presenter",
            "presentation_date": "2024-01-01",
            "header_title": "Title",
            "company_name": "Company Name",
            "main_topic": "Main Topic",
            "topic_1": "Introduction",
            "topic_2": "Content",
            "topic_3": "Details",
            "topic_4": "Conclusion",
            "topic_1_content": "- Content 1",
            "topic_2_content": "- Content 2",
            "topic_3_content": "- Content 3",
            "conclusion_content": "- Conclusion",
            "code_example": "print('Hello, World!')",
            "math_description": "Example mathematical formula",
            "inline_math": "$x = y + z$",
            "block_math": "E = mc^2",
        }
        result = defaults.copy()
        if isinstance(data, dict):
            for key, value in data.items():
                result[key] = str(value) if not isinstance(value, str) else value
        return result

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
            safe_data = self._ensure_placeholder_defaults(placeholder_data)
            return template.safe_substitute(safe_data)
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
