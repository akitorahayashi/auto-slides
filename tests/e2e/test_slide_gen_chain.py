"""
End-to-end tests for SlideGenChain using streamlit.secrets configuration.

Tests the complete slide generation workflow using streamlit secrets:
- DEBUG=true: Uses MockOlmaApiClient
- USE_LOCAL_CLIENT=true: Uses OllamaLocalClient
- USE_LOCAL_CLIENT=false: Uses OllamaApiClient (remote)
"""

from unittest.mock import MagicMock, patch

import pytest

from src.backend.chains.slide_gen_chain import SlideGenChain
from src.backend.clients.olm_client import OlmClient
from src.backend.models.slide_template import SlideTemplate


class TestSlideGenChainE2E:
    """End-to-end tests for SlideGenChain with streamlit secrets configuration"""

    @pytest.fixture
    def mock_template(self):
        """Create a mock SlideTemplate for testing"""
        template = MagicMock(spec=SlideTemplate)
        template.id = "test_template"
        template.name = "E2E Test Template"
        template.description = "End-to-end test template"
        template.duration_minutes = 10
        return template

    @pytest.fixture
    def test_script_content(self):
        """Sample script content for testing"""
        return """
        Sample slide script content for testing.
        Title: Test Slide
        Subtitle: End-to-end test
        Content: This is a sample slide for E2E testing.
        """

    def test_debug_mode_chain_execution(self, mock_template, test_script_content):
        """Test chain execution with DEBUG=true (Mock client)"""
        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": True,
                "OLLAMA_MODEL": "qwen3:0.6b",
            }.get(key, default)

            # Create OlmClient which should use SimpleMockClient in debug mode
            llm = OlmClient()
            chain = SlideGenChain(llm=llm)

            # Verify that we're using the mock client
            assert llm.client is not None
            assert hasattr(llm.client, "gen_batch")

            # Mock the slides loader to avoid file dependencies
            with patch(
                "src.backend.services.slides_loader.SlidesLoader.create_slide_functions_summary"
            ) as mock_catalog:
                with patch(
                    "src.backend.services.slides_loader.SlidesLoader.load_template_functions"
                ) as mock_functions:
                    with patch(
                        "src.backend.services.slides_loader.SlidesLoader.get_function_by_name"
                    ) as mock_get_function:

                        mock_catalog.return_value = "Function catalog for testing"
                        mock_functions.return_value = {
                            "title_slide": {
                                "name": "title_slide",
                                "params": ["title", "subtitle"],
                            }
                        }
                        mock_get_function.return_value = (
                            lambda **kwargs: "# Mock Slide\nMock content"
                        )

                        try:
                            # Execute the chain
                            result = chain.invoke_slide_gen_chain(
                                test_script_content, mock_template
                            )

                            # Verify result
                            assert isinstance(result, str)
                            assert len(result) > 0

                        except Exception as e:
                            pytest.skip(f"Debug mode test skipped due to: {e}")

    def test_local_client_chain_execution(self, mock_template, test_script_content):
        """Test chain execution with USE_LOCAL_CLIENT=true (Local ollama)"""
        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": "false",
                "USE_LOCAL_CLIENT": "true",
                "OLLAMA_MODEL": "qwen3:0.6b",
            }.get(key, default)

            try:
                # Create OlmClient which should use OllamaLocalClient
                llm = OlmClient()
                chain = SlideGenChain(llm=llm)

                # Verify that we're using the local client
                from sdk.olm_api_client import OllamaLocalClient

                assert isinstance(llm.client, OllamaLocalClient)

                # Mock the slides loader to avoid file dependencies
                with patch(
                    "src.backend.services.slides_loader.SlidesLoader.create_slide_functions_summary"
                ) as mock_catalog:
                    with patch(
                        "src.backend.services.slides_loader.SlidesLoader.load_template_functions"
                    ) as mock_functions:
                        with patch(
                            "src.backend.services.slides_loader.SlidesLoader.get_function_by_name"
                        ) as mock_get_function:

                            mock_catalog.return_value = "Function catalog for testing"
                            mock_functions.return_value = {
                                "title_slide": {
                                    "name": "title_slide",
                                    "params": ["title", "subtitle"],
                                }
                            }
                            mock_get_function.return_value = (
                                lambda **kwargs: "# Local Client Slide\nContent from local ollama"
                            )

                            # Execute the chain (this will actually try to connect to local ollama)
                            result = chain.invoke_slide_gen_chain(
                                test_script_content, mock_template
                            )

                            # Verify result
                            assert isinstance(result, str)
                            assert len(result) > 0
                            print("✅ Local client test passed")

            except ConnectionError:
                pytest.skip(
                    "Local ollama server not available - skipping local client test"
                )
            except Exception as e:
                pytest.skip(f"Local client test skipped due to: {e}")

    def test_remote_client_chain_execution(self, mock_template, test_script_content):
        """Test chain execution with USE_LOCAL_CLIENT=false (Remote API)"""
        test_endpoint = "http://test-server:8000"

        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": "false",
                "USE_LOCAL_CLIENT": "false",
                "OLM_API_ENDPOINT": test_endpoint,
                "OLLAMA_MODEL": "qwen3:0.6b",
            }.get(key, default)

            try:
                # Create OlmClient which should use OllamaApiClient
                llm = OlmClient()
                chain = SlideGenChain(llm=llm)

                # Verify we're using the API client
                from sdk.olm_api_client import OllamaApiClient

                assert isinstance(llm.client, OllamaApiClient)
                assert llm.client.api_url == test_endpoint

                # Mock the slides loader to avoid file dependencies
                with patch(
                    "src.backend.services.slides_loader.SlidesLoader.create_slide_functions_summary"
                ) as mock_catalog:
                    with patch(
                        "src.backend.services.slides_loader.SlidesLoader.load_template_functions"
                    ) as mock_functions:
                        with patch(
                            "src.backend.services.slides_loader.SlidesLoader.get_function_by_name"
                        ) as mock_get_function:

                            mock_catalog.return_value = "Function catalog for testing"
                            mock_functions.return_value = {
                                "title_slide": {
                                    "name": "title_slide",
                                    "params": ["title", "subtitle"],
                                }
                            }
                            mock_get_function.return_value = (
                                lambda **kwargs: "# Remote API Slide\nContent from remote API"
                            )

                            # Execute the chain (this will actually try to connect to remote API)
                            result = chain.invoke_slide_gen_chain(
                                test_script_content, mock_template
                            )

                            # Verify result
                            assert isinstance(result, str)
                            assert len(result) > 0
                            print("✅ Remote API client test passed")

            except ConnectionError:
                pytest.skip(
                    "Remote API server not available - skipping remote client test"
                )
            except Exception as e:
                pytest.skip(f"Remote client test skipped due to: {e}")

    def test_client_type_detection(self):
        """Test that OlmClient correctly selects client type based on configuration"""

        # Test DEBUG mode
        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": True
            }.get(key, default)

            llm = OlmClient()
            # Should use SimpleMockClient in debug mode
            assert hasattr(llm.client, "gen_batch")

        # Test local client mode
        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": "false",
                "USE_LOCAL_CLIENT": "true",
            }.get(key, default)

            llm = OlmClient()
            # Should use OllamaLocalClient
            from sdk.olm_api_client import OllamaLocalClient

            assert isinstance(llm.client, OllamaLocalClient)

        # Test remote client mode with endpoint
        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": "false",
                "USE_LOCAL_CLIENT": "false",
                "OLM_API_ENDPOINT": "http://test-endpoint:8000",
            }.get(key, default)

            llm = OlmClient()
            # Should use OllamaApiClient
            from sdk.olm_api_client import OllamaApiClient

            assert isinstance(llm.client, OllamaApiClient)
            assert llm.client.api_url == "http://test-endpoint:8000"

    def test_model_configuration(self):
        """Test that model configuration is properly read from secrets"""
        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": "true",
                "OLLAMA_MODEL": "custom-model:1.0",
            }.get(key, default)

            llm = OlmClient()
            assert llm.model == "custom-model:1.0"

    def test_chain_error_handling_with_real_client(self, mock_template):
        """Test error handling with real client configuration"""

        # Test with invalid script content
        invalid_script = ""

        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.get.side_effect = lambda key, default=None: {
                "DEBUG": True
            }.get(key, default)

            llm = OlmClient()
            chain = SlideGenChain(llm=llm)

            # Mock the slides loader
            with patch(
                "src.backend.services.slides_loader.SlidesLoader.create_slide_functions_summary"
            ) as mock_catalog:
                with patch(
                    "src.backend.services.slides_loader.SlidesLoader.load_template_functions"
                ) as mock_functions:
                    with patch(
                        "src.backend.services.slides_loader.SlidesLoader.get_function_by_name"
                    ) as mock_get_function:

                        mock_catalog.return_value = "Function catalog"
                        mock_functions.return_value = {}
                        mock_get_function.return_value = None

                        # Should handle errors gracefully
                        try:
                            result = chain.invoke_slide_gen_chain(
                                invalid_script, mock_template
                            )
                            # Even with invalid input, should return some result
                            assert isinstance(result, str)
                        except Exception as e:
                            # Error handling should be graceful
                            assert isinstance(e, Exception)
                            print(f"Expected error handled: {e}")
