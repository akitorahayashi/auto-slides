import json
from pathlib import Path
from string import Template
from typing import Any, Dict


class PromptService:
    """Service for building and managing prompts from templates"""

    def __init__(self, template_dir: str = "src/static/prompts"):
        self.template_dir = Path(template_dir)

    def _build_prompt(self, template_name: str, substitutions: Dict[str, Any]) -> str:
        """Build a prompt from a template file and substitutions."""
        prompt_file = self.template_dir / template_name
        prompt_template = Template(prompt_file.read_text(encoding="utf-8"))
        return prompt_template.substitute(substitutions)

    def build_analysis_prompt(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Build analysis prompt from template"""
        substitutions = {"script_content": input_dict["script_content"]}
        prompt = self._build_prompt("analyze_script.md", substitutions)
        return {**input_dict, "prompt": prompt}

    def build_planning_prompt(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Build planning prompt from template"""
        substitutions = {
            "analysis_result": json.dumps(
                input_dict["analysis_result"], ensure_ascii=False
            ),
            "placeholders_list": "\n".join(
                [f"- {p}" for p in input_dict["placeholders"]]
            ),
        }
        prompt = self._build_prompt("plan_content.md", substitutions)
        return {**input_dict, "prompt": prompt}

    def build_generation_prompt(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Build generation prompt from template"""
        placeholders = input_dict["placeholders"]
        substitutions = {
            "script_content": input_dict["script_content"],
            "placeholders_list": "\n".join([f"- {p}" for p in placeholders]),
            "json_example": ",\n".join(
                [f'  "{p}": "対応する内容"' for p in placeholders]
            ),
        }
        prompt = self._build_prompt("generate_slide_content.md", substitutions)
        return {**input_dict, "prompt": prompt}

    def build_validation_prompt(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Build validation prompt from template"""
        substitutions = {
            "generated_content": json.dumps(
                input_dict["generated_content"], ensure_ascii=False
            ),
            "analysis_result": json.dumps(
                input_dict["analysis_result"], ensure_ascii=False
            ),
            "content_plan": json.dumps(input_dict["content_plan"], ensure_ascii=False),
        }
        prompt = self._build_prompt("validate_content.md", substitutions)
        return {**input_dict, "prompt": prompt}

    def build_composition_prompt(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Build slide composition prompt"""
        substitutions = {
            "script_content": input_dict["script_content"],
            "analysis_result": json.dumps(
                input_dict["analysis_result"], ensure_ascii=False
            ),
            "function_catalog": input_dict["function_catalog"],
        }
        prompt = self._build_prompt("compose_slides.md", substitutions)
        return {**input_dict, "prompt": prompt}

    def build_parameter_prompt(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Build parameter generation prompt"""
        function_info = input_dict["function_info"]
        substitutions = {
            "script_content": input_dict["script_content"],
            "analysis_result": json.dumps(
                input_dict["analysis_result"], ensure_ascii=False
            ),
            "function_name": input_dict["function_name"],
            "function_purpose": (
                function_info.get("docstring", "").split("\n")[0]
                if function_info.get("docstring")
                else ""
            ),
            "function_signature": function_info.get("signature", ""),
            "arguments_list": "\n".join(
                [
                    f"  - {name}: {desc}"
                    for name, desc in function_info.get("args_info", {}).items()
                ]
            ),
        }
        prompt = self._build_prompt("generate_parameters.md", substitutions)
        return {**input_dict, "prompt": prompt}
