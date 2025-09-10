import asyncio
from typing import Any, AsyncGenerator, Dict, Union

from langchain_core.runnables import Runnable

from src.protocols.olm_client_protocol import OlmClientProtocol


class MockOlmClient(Runnable, OlmClientProtocol):
    """
    Mock OLM client implementation for testing and development.

    Inherits from OlmClientProtocol to ensure interface compliance.
    Provides configurable response simulation without network dependencies.

    Response Configuration:
    - Dict[str, str]: Maps prompt substrings to specific responses (case-insensitive matching)
    - None: Uses built-in default testing responses

    Example Usage:
        # Default behavior
        client = MockOlmClient()

        # Specific responses for prompts
        client = MockOlmClient(responses={
            "analyze": "Mock analysis complete",
            "summarize": "Mock summary generated",
            "default": "Default mock response"
        })
    """

    def __init__(self, responses: Union[Dict[str, str], None] = None):
        """
        Initialize mock client with dictionary-based response configuration.

        Args:
            responses: Dict[str, str] mapping prompt substrings to responses (case-sensitive)
                      If None, uses default mock responses
        """
        self.responses = (
            responses if responses is not None else self._get_default_responses()
        )

    def _get_default_responses(self) -> Dict[str, str]:
        """Default mock responses for testing scenarios."""
        return {
            "analyze": "Mock response: Analysis completed successfully.",
            "summary": "Mock response: Summary generated from input text.",
            "generate": "Mock response: Content generated for development testing.",
            "default": "Mock response: Processing completed with test data.",
        }

    def _generate_response(self, prompt: str, model_name: str) -> str:
        """
        Generate appropriate mock response based on dictionary configuration.

        Args:
            prompt: Input prompt text
            model_name: Model identifier (for logging/debugging)

        Returns:
            Mock response string based on prompt matching
        """
        # Try exact prompt match first
        if prompt in self.responses:
            return self.responses[prompt]

        # Search for substring matches (returns first match)
        for substring, response in self.responses.items():
            if substring.lower() in prompt.lower():
                return response

        # Fallback to default response if available
        if "default" in self.responses:
            return self.responses["default"]

        # Ultimate fallback for unmatched prompts
        return f"Mock response for unrecognized prompt: {prompt[:50]}..."

    def gen_stream(self, prompt: str, model_name: str) -> AsyncGenerator[str, None]:
        """
        Override parent gen_stream method to simulate streaming text generation.

        Args:
            prompt: The prompt to send to the model
            model_name: The name of the model to use for generation

        Returns:
            AsyncGenerator yielding text chunks
        """
        # Call parent method for consistency
        super().gen_stream(prompt, model_name)

        async def _mock_stream():
            full_response = self._generate_response(prompt, model_name)

            # Split into words for realistic chunk simulation
            words = full_response.split()

            for i, word in enumerate(words):
                # Add space except for last word
                chunk = word + (" " if i < len(words) - 1 else "")
                yield chunk

                # Simulate realistic streaming delay
                await asyncio.sleep(0.01)

        return _mock_stream()

    async def gen_batch(self, prompt: str, model_name: str) -> str:
        """
        Override parent gen_batch method to generate complete text using the model without streaming.

        Args:
            prompt: The prompt to send to the model
            model_name: The name of the model to use for generation

        Returns:
            Complete text response
        """
        # Call parent method for consistency
        await super().gen_batch(prompt, model_name)

        # Simulate processing delay
        await asyncio.sleep(0.05)

        return self._generate_response(prompt, model_name)

    def invoke(self, input: Any, config: Any = None) -> str:
        """
        LangChain Runnable interface implementation.

        Args:
            input: Input prompt (string or dict with 'prompt' key)
            config: Optional configuration (ignored)

        Returns:
            Mock response string
        """
        if isinstance(input, str):
            prompt = input
        elif isinstance(input, dict) and "prompt" in input:
            prompt = input["prompt"]
        else:
            prompt = str(input)

        # Use default model for invoke
        return asyncio.run(self.gen_batch(prompt, "mock-model"))

    async def ainvoke(self, input: Any, config: Any = None) -> str:
        """
        Async LangChain Runnable interface implementation.

        Args:
            input: Input prompt (string or dict with 'prompt' key)
            config: Optional configuration (ignored)

        Returns:
            Mock response string
        """
        if isinstance(input, str):
            prompt = input
        elif isinstance(input, dict) and "prompt" in input:
            prompt = input["prompt"]
        else:
            prompt = str(input)

        return await self.gen_batch(prompt, "mock-model")
