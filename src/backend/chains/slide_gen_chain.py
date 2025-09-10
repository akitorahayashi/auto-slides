from typing import Callable, Dict, List, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from src.backend.models.slide_template import SlideTemplate
from src.backend.services import JsonParser, PromptService, SlidesLoader
from src.protocols.protocols.olm_client_protocol import OlmClientProtocol
from src.protocols.slide_generation_protocol import SlideGenerationProtocol


class SlideGenChain(SlideGenerationProtocol):
    """LangChain LCEL chains for slide generation workflow"""

    def __init__(self, llm: OlmClientProtocol, progress_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize slide generation chain.

        Args:
            llm: Required OlmClientProtocol implementation for text generation
            progress_callback: Optional callback function to report progress
        """
        self.llm = llm
        self.json_parser = JsonParser()
        self.str_parser = StrOutputParser()
        self.prompt_service = PromptService()
        self.slides_loader = SlidesLoader()
        self.progress_callback = progress_callback
        self._setup_chains()

    def _create_chain_step(self, prompt_builder_method):
        """Create a standardized chain step"""
        return (
            RunnablePassthrough.assign(prompt=RunnableLambda(prompt_builder_method))
            | RunnableLambda(lambda x: x["prompt"])
            | ChatPromptTemplate.from_template("{prompt}")
            | self.llm
            | self.json_parser
        )

    def _setup_chains(self):
        """Setup unified slide generation chain"""
        self.slide_gen_chain = (
            # Phase 1: Analysis
            RunnablePassthrough.assign(
                analysis_result=self._create_chain_step(
                    self.prompt_service.build_analysis_prompt
                )
            )
            # Phase 2: Composition
            | RunnableLambda(lambda x: self._report_progress("composing") or x)
            | RunnablePassthrough.assign(
                function_catalog=RunnableLambda(
                    lambda x: self.slides_loader.create_function_catalog(
                        x["template"].id
                    )
                )
            )
            | RunnablePassthrough.assign(
                composition_plan=self._create_chain_step(
                    self.prompt_service.build_composition_prompt
                )
            )
            # Phase 3: Parameter Generation & Execution
            | RunnableLambda(self._execute_slides)
            # Phase 4: Combine slides
            | RunnableLambda(lambda x: self._combine_slides(x["slides"]))
        )

    def invoke_slide_gen_chain(
        self, script_content: str, template: SlideTemplate
    ) -> str:
        """Unified slide generation chain execution"""
        try:
            self._report_progress("analyzing")
            print("🔍 Agent: Analyzing script content...")
            result = self.slide_gen_chain.invoke(
                {"script_content": script_content, "template": template}
            )
            self._report_progress("completed")
            print("🎉 Agent: Presentation generated successfully!")
            return result
        except Exception as e:
            print(f"🚨 Agent error: {e}")
            raise e

    def _execute_slides(self, context: Dict) -> Dict:
        """Execute slide generation from composition plan"""
        self._report_progress("generating")
        print("✍️ Agent: Generating slide parameters...")

        composition_plan = context["composition_plan"]
        template = context["template"]
        script_content = context["script_content"]
        analysis_result = context["analysis_result"]

        slide_parameters = []
        functions = self.slides_loader.load_template_functions(template.id)

        for slide_plan in composition_plan.get("slides", []):
            function_name = slide_plan["function_name"]
            if function_name in functions:
                params = self._create_chain_step(
                    self.prompt_service.build_parameter_prompt
                ).invoke(
                    {
                        "script_content": script_content,
                        "analysis_result": analysis_result,
                        "function_name": function_name,
                        "function_info": functions[function_name],
                    }
                )
                slide_parameters.append(params)

        self._report_progress("building")
        print("🏗️ Agent: Building slides...")
        slides = []

        for slide_param in slide_parameters:
            function_name = slide_param.get("function_name")
            parameters = slide_param.get("parameters", {})

            func = self.slides_loader.get_function_by_name(template.id, function_name)

            if func:
                try:
                    slide_content = func(**parameters)
                    slides.append(slide_content)
                except Exception as e:
                    print(f"⚠️ Error executing {function_name}: {e}")
                    continue

        return {**context, "slides": slides}

    def _combine_slides(self, slides: List[str]) -> str:
        """Combine individual slides into complete presentation"""
        self._report_progress("combining")

        processed_slides = []
        for slide in slides:
            processed_slides.append(slide.rstrip("\n-"))

        return "\n\n".join(processed_slides)
    
    def _report_progress(self, stage: str):
        """Report progress to callback if available"""
        if self.progress_callback:
            self.progress_callback(stage)
