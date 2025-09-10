import inspect
from typing import Callable, Dict, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from src.backend.models.slide_template import SlideTemplate
from src.backend.services import JsonParser, PromptService, SlidesLoader
from src.protocols.protocols.olm_client_protocol import OlmClientProtocol
from src.protocols.slide_generation_protocol import SlideGenerationProtocol


class SlideGenChain(SlideGenerationProtocol):
    """LangChain LCEL chains for slide generation workflow"""

    def __init__(
        self,
        llm: OlmClientProtocol,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ):
        """
        Initialize slide generation chain.

        Args:
            llm: Required OlmClientProtocol implementation for text generation
            progress_callback: Optional callback function to report progress (stage, current, total)
        """
        self.llm = llm
        self.json_parser = JsonParser()
        self.str_parser = StrOutputParser()
        self.prompt_service = PromptService()
        self.slides_loader = SlidesLoader()
        self.progress_callback = progress_callback
        self.current_phase = 0
        self.total_phases = 4  # analyzing, composing, building, generating,
        self._setup_chains()

    def _create_chain_step(self, prompt_builder_method):
        """Create a standardized chain step"""
        return (
            RunnablePassthrough.assign(prompt=RunnableLambda(prompt_builder_method))
            | RunnableLambda(lambda x: x["prompt"])
            | RunnableLambda(
                lambda prompt_dict: {
                    **prompt_dict,
                    "prompt": self.prompt_service._truncate_prompt(
                        prompt_dict["prompt"]
                    ),
                }
            )
            | ChatPromptTemplate.from_template("{prompt}")
            | self.llm
            | RunnableLambda(self._log_llm_response)
            | self.json_parser
        )

    def _create_string_chain_step(self, prompt_builder_method):
        """Create a standardized chain step for string output"""
        return (
            RunnablePassthrough.assign(prompt=RunnableLambda(prompt_builder_method))
            | RunnableLambda(lambda x: x["prompt"])
            | RunnableLambda(
                lambda prompt_dict: {
                    **prompt_dict,
                    "prompt": self.prompt_service._truncate_prompt(
                        prompt_dict["prompt"]
                    ),
                }
            )
            | ChatPromptTemplate.from_template("{prompt}")
            | self.llm
            | RunnableLambda(self._log_llm_response)
            | self.str_parser
        )

    def _setup_chains(self):
        """Setup unified slide generation chain with placeholder approach"""
        self.slide_gen_chain = (
            # Phase 1: Analysis
            RunnablePassthrough.assign(
                analysis_result=self._create_chain_step(
                    self.prompt_service.build_analysis_prompt
                )
            )
            # Phase 2: Composition
            | RunnablePassthrough.assign(
                slide_functions_summary=RunnableLambda(
                    lambda x: self.slides_loader.create_slide_functions_summary(
                        x["template"].id
                    )
                )
            )
            | RunnableLambda(lambda x: self._report_phase_progress("analyzing") or x)
            | RunnablePassthrough.assign(
                composition_plan=self._create_chain_step(
                    self.prompt_service.build_composition_prompt
                )
            )
            # Phase 3: Build Template with Placeholders
            | RunnableLambda(lambda x: self._report_phase_progress("composing") or x)
            | RunnablePassthrough.assign(
                template_with_placeholders=RunnableLambda(
                    self._build_template_with_placeholders
                )
            )
            # Phase 4: Single LLM Call to Fill All Placeholders
            | RunnableLambda(lambda x: self._report_phase_progress("generating") or x)
            | RunnablePassthrough.assign(
                final_presentation=self._create_string_chain_step(
                    self.prompt_service.build_placeholder_prompt
                )
            )
            | RunnableLambda(lambda x: self._report_phase_progress("building") or x)
            | RunnableLambda(lambda x: self._report_phase_progress("completed") or x)
            | RunnableLambda(lambda x: x["final_presentation"])
        )

    def invoke_slide_gen_chain(
        self, script_content: str, template: SlideTemplate
    ) -> str:
        """Unified slide generation chain execution"""
        try:
            # 初期化
            self.current_phase = 0
            print("🔍 Agent: Starting presentation generation...")

            input_data = {"script_content": script_content, "template": template}
            print(
                f"🔍 Input data: script_length={len(script_content)}, template_id={template.id}"
            )

            result = self.slide_gen_chain.invoke(input_data)
            print("🎉 Agent: Presentation generated successfully!")
            print(f"🔍 Result length: {len(result) if result else 0}")
            return result
        except Exception as e:
            print(f"🚨 Agent error: {e}")
            print(f"🚨 Error type: {type(e).__name__}")
            print(
                f"🚨 Input was: script_length={len(script_content) if script_content else 0}, template_id={template.id if template else 'None'}"
            )
            raise e

    def _build_template_with_placeholders(self, context: Dict) -> str:
        """Build unified template by calling slide functions with placeholders"""
        print("🏗️ Agent: Building template with placeholders...")

        composition_plan = context["composition_plan"]
        template = context["template"]
        slides_list = composition_plan.get("slides", [])

        template_parts = []

        for i, slide_plan in enumerate(slides_list):
            if not isinstance(slide_plan, dict):
                continue

            slide_name = slide_plan.get("slide_name")
            if not slide_name:
                continue

            func = self.slides_loader.get_function_by_name(template.id, slide_name)
            if not func:
                continue

            # Create placeholder parameters based on function signature
            sig = inspect.signature(func)
            placeholder_params = {}

            for param_name in sig.parameters.keys():
                placeholder_params[param_name] = (
                    f"{{{{{slide_name.upper()}_{i}_{param_name.upper()}}}}}"
                )

            # Call the actual slide function with placeholders
            try:
                slide_with_placeholders = func(**placeholder_params)
                template_parts.append(slide_with_placeholders)
            except Exception as e:
                print(f"⚠️ Error creating placeholder template for {slide_name}: {e}")
                continue

        return "\n\n".join(template_parts)

    def _log_llm_response(self, response):
        """Log LLM response for debugging"""
        if hasattr(response, "content"):
            content = response.content
        else:
            content = str(response)

        print(f"AI Response ({len(content)} chars):")
        if len(content) > 500:
            print(f"   {content[:200]}...")
            print(f"   ...{content[-200:]}")
        else:
            print(f"   {content}")

        return response

    def _report_phase_progress(self, stage: str):
        """Report phase completion progress"""
        self.current_phase += 1
        print(f"✅ Phase {self.current_phase}/{self.total_phases} completed: {stage}")
        if self.progress_callback:
            try:
                self.progress_callback(stage, self.current_phase, self.total_phases)
            except Exception as callback_error:
                print(f"⚠️ Progress callback error: {callback_error}")
                # コールバックエラーでもチェーン処理は継続
