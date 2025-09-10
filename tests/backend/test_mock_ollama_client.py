import pytest

from dev.mocks.mock_olm_client import MockOlmClient


class TestMockOlmClient:
    """Test cases for MockOlmClient"""

    @pytest.mark.asyncio
    async def test_default_responses(self):
        """Test mock client with default responses"""
        client = MockOlmClient()

        response = await client.gen_batch("analyze this", "qwen3:0.6b")
        assert "Analysis completed successfully" in response

        response = await client.gen_batch("generate content", "qwen3:0.6b")
        assert "Content generated for development testing" in response

    @pytest.mark.asyncio
    async def test_dictionary_responses(self):
        """Test mock client with dictionary-based responses"""
        responses = {
            "analyze": "Custom analysis response",
            "summarize": "Custom summary response",
            "default": "Default response",
        }
        client = MockOlmClient(responses=responses)

        # Exact match
        response = await client.gen_batch("analyze", "test-model")
        assert response == "Custom analysis response"

        # Substring match
        response = await client.gen_batch("analyze this content", "test-model")
        assert response == "Custom analysis response"

        # Default fallback
        response = await client.gen_batch("unknown prompt", "test-model")
        assert response == "Default response"

    @pytest.mark.asyncio
    async def test_gen_stream_functionality(self):
        """Test that gen_stream returns an async generator with chunks"""
        responses = {"test": "Test response for streaming"}
        client = MockOlmClient(responses=responses)

        chunks = []
        async for chunk in client.gen_stream("test prompt", "model"):
            chunks.append(chunk)

        # Verify chunks combine to form the complete response
        complete_response = "".join(chunks)
        assert complete_response == "Test response for streaming"

        # Verify we got multiple chunks
        assert len(chunks) > 1

    @pytest.mark.asyncio
    async def test_gen_stream_and_gen_batch_same_content(self):
        """Test that both gen_stream and gen_batch return the same content"""
        responses = {"test": "Test response"}
        client = MockOlmClient(responses=responses)

        batch_response = await client.gen_batch("test prompt", "model")

        stream_chunks = []
        async for chunk in client.gen_stream("test prompt", "model"):
            stream_chunks.append(chunk)
        stream_response = "".join(stream_chunks)

        assert batch_response == stream_response == "Test response"

    def test_initialization_with_none(self):
        """Test that client can be initialized with None responses"""
        client = MockOlmClient(responses=None)
        assert client.responses is not None
        assert isinstance(client.responses, dict)

    def test_initialization_with_empty_dict(self):
        """Test that client can be initialized with empty dict"""
        client = MockOlmClient(responses={})
        assert client.responses == {}
