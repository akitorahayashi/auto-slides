from typing import AsyncGenerator, Protocol, runtime_checkable


@runtime_checkable
class OlmClientProtocol(Protocol):
    """
    Unified protocol for OLM API clients.

    Defines the interface for all OLM client implementations:
    - OlmLocalClient: Direct communication with local ollama serve
    - OlmApiClient: Remote API communication via HTTP
    - MockOlmApiClient: In-memory simulation for testing

    All implementations must provide both streaming and batch generation methods.
    """

    def gen_stream(self, prompt: str, model_name: str) -> AsyncGenerator[str, None]:
        """
        Generate text using the model with streaming response.

        Args:
            prompt: The input prompt to send to the model
            model_name: The name/identifier of the model to use (e.g., "qwen3:0.6b")

        Returns:
            AsyncGenerator that yields text chunks as they are generated

        Raises:
            ConnectionError: If unable to connect to the OLM service
            ValueError: If model_name is invalid or not available
        """
        ...

    async def gen_batch(self, prompt: str, model_name: str) -> str:
        """
        Generate complete text using the model without streaming.

        Args:
            prompt: The input prompt to send to the model
            model_name: The name/identifier of the model to use (e.g., "qwen3:0.6b")

        Returns:
            Complete text response as a single string

        Raises:
            ConnectionError: If unable to connect to the OLM service
            ValueError: If model_name is invalid or not available
        """
        ...
