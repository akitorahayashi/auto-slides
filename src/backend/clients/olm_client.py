import re
from typing import Any, List, Optional

import streamlit as st
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from sdk.olm_api_client import (
    MockOllamaApiClient,
    OllamaApiClient,
    OllamaLocalClient,
)

from src.protocols.protocols.olm_client_protocol import OlmClientProtocol


class OlmClient(LLM):
    """
    Unified OLM client with LangChain integration.

    Provides a LangChain-compatible interface for Ollama clients.
    Automatically selects appropriate client implementation based on configuration:
    - MockOllamaApiClient for debug mode
    - OllamaLocalClient for local development
    - OllamaApiClient for remote API communication

    Configuration via environment variables or Streamlit secrets:
    - DEBUG: Enable mock mode for testing
    - USE_LOCAL_CLIENT: Use local ollama serve instance
    - OLM_API_ENDPOINT: Remote API server URL
    - OLLAMA_MODEL: Model name to use (default: qwen3:0.6b)
    """

    model: str = "qwen3:4b"
    client: OlmClientProtocol = None

    def __init__(self):
        super().__init__()
        self._setup_client()

    def _clean_output(self, text: str) -> str:
        """Clean LLM output by removing think tags and other artifacts"""
        # Remove <think> tags and their content
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

        # Remove other common artifacts
        cleaned = re.sub(r"<reasoning>.*?</reasoning>", "", cleaned, flags=re.DOTALL)
        cleaned = re.sub(r"<analysis>.*?</analysis>", "", cleaned, flags=re.DOTALL)

        # Clean up extra whitespace
        cleaned = re.sub(r"\n\s*\n", "\n\n", cleaned)
        cleaned = cleaned.strip()

        return cleaned

    def _setup_client(self):
        """Setup Ollama client based on configuration"""
        debug_value = st.secrets.get("DEBUG", "false")
        if isinstance(debug_value, bool):
            debug = debug_value
        else:
            debug = str(debug_value).lower() == "true"

        self.model = st.secrets.get("OLLAMA_MODEL", "qwen3:0.6b")

        if debug:
            # Use mock client for debug mode
            self.client = MockOllamaApiClient(
                responses=[
                    '{"result": "Mock response for testing"}',
                    '{"result": "Debug mode active - using mock responses"}',
                ]
            )
            return

        use_local_value = st.secrets.get("USE_LOCAL_CLIENT", "false")
        if isinstance(use_local_value, bool):
            use_local = use_local_value
        else:
            use_local = str(use_local_value).lower() == "true"

        if use_local:
            self.client = OllamaLocalClient()
        else:
            api_endpoint = st.secrets.get("OLM_API_ENDPOINT")

            if not api_endpoint:
                print("Warning: OLM_API_ENDPOINT not set, using mock client")
                # Use mock client when endpoint is not configured
                self.client = MockOllamaApiClient(
                    responses=[
                        '{"result": "Mock API response - endpoint not configured"}'
                    ]
                )
            else:
                self.client = OllamaApiClient(api_url=api_endpoint)

    @property
    def _llm_type(self) -> str:
        return "ollama_client"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        import asyncio

        result = asyncio.run(self.client.gen_batch(prompt, self.model))
        return self._clean_output(result)

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        result = await self.client.gen_batch(prompt, self.model)
        return self._clean_output(result)
