import os
from typing import Optional

import streamlit as st
from sdk.olm_api_client import (
    MockOllamaApiClient,
    OllamaApiClient,
    OllamaClientProtocol,
    OllamaLocalClient,
)


class OllamaClientManager:
    """
    Manages Ollama client creation using direct client initialization.
    Handles environment configuration and client initialization.
    """

    @staticmethod
    def create_client(
        debug: Optional[bool] = None,
        use_local: Optional[bool] = None,
        api_endpoint: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> tuple[OllamaClientProtocol, str]:
        """
        Create an Ollama client based on configuration.

        Returns:
            Tuple of (client, model_name)
        """
        if debug is None:
            debug_value = st.secrets.get("DEBUG", os.getenv("DEBUG", "false"))
            if isinstance(debug_value, bool):
                debug = debug_value
            else:
                debug = str(debug_value).lower() == "true"

        if model_name is None:
            model_name = st.secrets.get(
                "OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
            )

        if debug:
            return MockOllamaApiClient(), model_name

        if use_local is None:
            use_local_value = st.secrets.get(
                "USE_LOCAL_CLIENT", os.getenv("USE_LOCAL_CLIENT", "false")
            )
            if isinstance(use_local_value, bool):
                use_local = use_local_value
            else:
                use_local = str(use_local_value).lower() == "true"

        if use_local:
            return OllamaLocalClient(), model_name
        else:
            if api_endpoint is None:
                api_endpoint = st.secrets.get(
                    "OLM_API_ENDPOINT", os.getenv("OLM_API_ENDPOINT")
                )

            if not api_endpoint:
                print("Warning: OLM_API_ENDPOINT not set, using MockOllamaApiClient")
                return MockOllamaApiClient(), model_name

            return OllamaApiClient(api_url=api_endpoint), model_name
