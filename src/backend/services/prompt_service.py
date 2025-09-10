import json
from pathlib import Path
from string import Template
from typing import Any, Dict


class PromptService:
    """Service for building and managing prompts from templates"""

    def __init__(self, template_dir: str = "src/backend/static/prompts"):
        self.template_dir = Path(template_dir)

    def _build_prompt(self, template_name: str, substitutions: Dict[str, Any]) -> str:
        """Build a prompt from a template file and substitutions."""
        prompt_file = self.template_dir / template_name
        prompt_template = Template(prompt_file.read_text(encoding="utf-8"))
        return prompt_template.substitute(substitutions)

    def build_analysis_prompt(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Build analysis prompt from template"""
        import streamlit as st

        script_content = input_dict["script_content"]
        divisor = st.secrets.get("ARGUMENT_FLOW_DIVISOR", 4)
        argument_flow_limit = len(script_content) // divisor
        substitutions = {
            "script_content": script_content,
            "argument_flow_limit": str(argument_flow_limit),
        }
        prompt = self._build_prompt("analyze_script.md", substitutions)
        return {**input_dict, "prompt": prompt}

    def build_composition_prompt(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Build slide composition prompt"""
        substitutions = {
            "script_content": input_dict["script_content"],
            "analysis_result": json.dumps(
                input_dict["analysis_result"], ensure_ascii=False
            ),
            "slide_functions_summary": input_dict["slide_functions_summary"],
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
            "slide_name": input_dict["slide_name"],
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
