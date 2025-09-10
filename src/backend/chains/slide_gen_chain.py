import inspect
from typing import Any, Callable, Dict, List, Optional

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
        self.current_request = 0
        self.total_requests = 0
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
            | RunnableLambda(lambda x: self._increment_request_counter() or x)
            | self.llm
            | self.json_parser
        )

    def _increment_request_counter(self):
        """LLMリクエストカウンターを増加"""
        self.current_request += 1
        if self.progress_callback:
            # プログレスを0.0-1.0で計算
            progress = min(self.current_request / max(self.total_requests, 1), 1.0)
            print(
                f"📊 LLM Request {self.current_request}/{self.total_requests} (progress: {progress:.1%})"
            )
            # 現在のステージを決定
            if self.current_request == 1:
                stage = "analyzing"
            elif self.current_request == 2:
                stage = "composing"
            else:
                stage = "generating"
            
            # プログレスコールバックを呼び出し（セッションコンテキスト外での呼び出しを回避）
            try:
                self.progress_callback(stage, self.current_request, self.total_requests)
            except Exception as e:
                print(f"Progress callback failed: {e}")
        return None

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
            | RunnablePassthrough.assign(
                slide_functions_summary=RunnableLambda(
                    lambda x: self.slides_loader.create_slide_functions_summary(
                        x["template"].id
                    )
                )
            )
            | RunnableLambda(lambda x: self._report_progress("composing") or x)
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
            # 事前にLLMリクエスト数を計算
            self._calculate_total_requests(template)
            # カウンターを1から開始するために初期化
            self.current_request = 0
            self._report_progress("analyzing")
            print("🔍 Agent: Analyzing script content...")

            input_data = {"script_content": script_content, "template": template}
            print(
                f"🔍 Input data: script_length={len(script_content)}, template_id={template.id}"
            )
            print(f"🔍 Total LLM requests: {self.total_requests}")

            result = self.slide_gen_chain.invoke(input_data)
            self._report_progress("completed")
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

    def _calculate_total_requests(self, template: SlideTemplate) -> None:
        """事前にLLMリクエスト数を計算"""
        try:
            # 基本的なリクエスト: 分析(1) + 構成(1) = 2
            base_requests = 2

            # テンプレート関数の数を取得（これは利用可能な関数数であり、実際に使用される数ではない）
            functions = self.slides_loader.load_template_functions(template.id)

            # 初期値として利用可能な関数数を使用（後で動的に調整）
            # 実際の値は composition_plan 取得後に更新される
            estimated_slide_count = len(functions)

            # 各スライドのパラメータ生成リクエスト数
            parameter_requests = estimated_slide_count

            self.total_requests = base_requests + parameter_requests
            self.current_request = 0

            print(
                f"🔢 Initial request calculation: {self.total_requests} (base: {base_requests}, estimated slides: {estimated_slide_count})"
            )
        except Exception as e:
            print(f"⚠️ Error calculating requests: {e}")
            # エラー時はデフォルト値を使用
            self.total_requests = 5
            self.current_request = 0

    def _execute_slides(self, context: Dict) -> Dict:
        """Execute slide generation from composition plan"""
        print("✍️ Agent: Generating slide parameters...")

        composition_plan = context["composition_plan"]
        template = context["template"]
        script_content = context["script_content"]
        analysis_result = context["analysis_result"]

        # composition_planから実際のスライド数を取得してリクエスト数を更新
        slides_list = composition_plan.get("slides", [])
        actual_slide_count = len(slides_list)

        if actual_slide_count > 0:
            # 実際のスライド数に基づいてリクエスト数を再計算
            base_requests = 2  # 分析(1) + 構成(1)
            new_total_requests = base_requests + actual_slide_count

            print(
                f"🔄 Updating total requests: {self.total_requests} → {new_total_requests} (actual slides: {actual_slide_count})"
            )
            self.total_requests = new_total_requests
        else:
            print(
                f"⚠️ No slides found in composition plan, using original estimate: {self.total_requests}"
            )

        # プログレス表示を更新（現在のステージで最新の分母を表示）
        self._report_progress("generating")

        slide_parameters = []
        functions = self.slides_loader.load_template_functions(template.id)

        # composition_planの構造をデバッグ出力
        print(f"🔍 Composition plan structure: {composition_plan}")
        print(f"🔍 Slides list: {slides_list}")

        for i, slide_plan in enumerate(slides_list):
            print(f"🔍 Processing slide {i + 1}: {slide_plan}")

            # slide_nameの存在確認
            if not isinstance(slide_plan, dict):
                print(f"⚠️ Slide plan {i + 1} is not a dictionary: {type(slide_plan)}")
                continue

            slide_name = slide_plan.get("slide_name")
            if not slide_name:
                print(f"⚠️ Slide plan {i + 1} missing slide_name: {slide_plan}")
                continue

            if slide_name not in functions:
                print(f"⚠️ Function '{slide_name}' not available in template functions")
                continue

            try:
                params = self._create_chain_step(
                    self.prompt_service.build_parameter_prompt
                ).invoke(
                    {
                        "script_content": script_content,
                        "analysis_result": analysis_result,
                        "slide_name": slide_name,
                        "function_info": functions[slide_name],
                    }
                )
                slide_parameters.append(params)
                print(f"✅ Successfully generated parameters for {slide_name}")
            except Exception as param_error:
                print(f"⚠️ Error generating parameters for {slide_name}: {param_error}")
                continue

        self._report_progress("building")
        print("🏗️ Agent: Building slides...")
        slides = []

        for i, slide_param in enumerate(slide_parameters):
            print(f"🔍 Processing slide parameter {i + 1}: {slide_param}")

            if not isinstance(slide_param, dict):
                print(f"⚠️ Slide param {i + 1} is not a dictionary: {type(slide_param)}")
                continue

            slide_name = slide_param.get("slide_name")
            if not slide_name:
                print(f"⚠️ Slide param {i + 1} missing slide_name: {slide_param}")
                continue

            parameters = slide_param.get("parameters", {})

            func = self.slides_loader.get_function_by_name(template.id, slide_name)

            if func:
                try:
                    # 関数のシグネチャを取得して、有効なパラメータのみを渡す
                    sig = inspect.signature(func)
                    valid_params = {}

                    for param_name, param_value in parameters.items():
                        if param_name in sig.parameters:
                            valid_params[param_name] = param_value
                        else:
                            print(
                                f"🔧 Skipping invalid parameter '{param_name}' for function '{slide_name}'"
                            )

                    # 不足している必須パラメータがないかチェック
                    missing_params = []
                    for param_name, param in sig.parameters.items():
                        if (
                            param.default is inspect.Parameter.empty
                            and param_name not in valid_params
                        ):
                            missing_params.append(param_name)

                    if missing_params:
                        print(
                            f"⚠️ Missing required parameters for {slide_name}: {missing_params}"
                        )
                        continue

                    slide_content = func(**valid_params)
                    slides.append(slide_content)
                except Exception as e:
                    print(f"⚠️ Error executing {slide_name}: {e}")
                    print(f"   Parameters: {parameters}")
                    print(
                        f"   Valid parameters: {valid_params if 'valid_params' in locals() else 'N/A'}"
                    )
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
            # 完了時は最大値に設定、それ以外は現在のリクエスト数+1を表示（1から始まるため）
            if stage == "completed":
                current = self.total_requests
            else:
                current = self.current_request + 1  # 1から始まるように表示
            self.progress_callback(stage, current, self.total_requests)
