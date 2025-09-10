from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from src.clients.ollama_client import OlmClient
from src.services.output_parsers import RobustJsonOutputParser
from src.services.prompt_service import PromptService


class SlideGenChain:
    """LangChain LCEL chains for slide generation workflow"""

    def __init__(self):
        self.llm = OlmClient()
        self.json_parser = RobustJsonOutputParser()
        self.str_parser = StrOutputParser()
        self.prompt_service = PromptService()
        self._setup_chains()

    def _setup_chains(self):
        """Setup LangChain LCEL chains using OllamaClientManager"""

        # Phase 1: Script Analysis Chain (JSON出力)
        self.analysis_chain = (
            RunnablePassthrough.assign(
                prompt=RunnableLambda(self.prompt_service.build_analysis_prompt)
            )
            | RunnableLambda(lambda x: x["prompt"])
            | ChatPromptTemplate.from_template("{prompt}")
            | self.llm
            | self.json_parser
        )

        # Phase 2: Content Planning Chain
        self.planning_chain = (
            RunnablePassthrough.assign(
                prompt=RunnableLambda(self.prompt_service.build_planning_prompt)
            )
            | RunnableLambda(lambda x: x["prompt"])
            | ChatPromptTemplate.from_template("{prompt}")
            | self.llm
            | self.json_parser
        )

        # Phase 3: Content Generation Chain
        self.generation_chain = (
            RunnablePassthrough.assign(
                prompt=RunnableLambda(self.prompt_service.build_generation_prompt)
            )
            | RunnableLambda(lambda x: x["prompt"])
            | ChatPromptTemplate.from_template("{prompt}")
            | self.llm
            | self.json_parser
        )

        # Phase 4: Content Validation Chain
        self.validation_chain = (
            RunnablePassthrough.assign(
                prompt=RunnableLambda(self.prompt_service.build_validation_prompt)
            )
            | RunnableLambda(lambda x: x["prompt"])
            | ChatPromptTemplate.from_template("{prompt}")
            | self.llm
            | self.json_parser
        )
