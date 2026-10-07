import os
import pytest
from unittest.mock import patch, MagicMock
from src.gemini_adapter import generate, ConfigurationError, GenerationError
from google.genai import errors

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key", "GEMINI_MODEL": "test-model"}):
        yield

def test_successful_generation(mock_env):
    """Test 1: Mock Gemini to return exact text."""
    expected_response = "Alphabet Q4 2023 revenue was $86.3 billion. [ev_001]"
    
    with patch('src.gemini_adapter.genai.Client') as MockClient:
        mock_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.text = expected_response
        mock_instance.models.generate_content.return_value = mock_response
        
        result = generate("Test prompt")
        assert result == expected_response

def test_prompt_forwarding(mock_env):
    """Test 2: Verify the exact prompt is forwarded to the Gemini client."""
    exact_prompt = "This is the exact grounded prompt to forward."
    
    with patch('src.gemini_adapter.genai.Client') as MockClient:
        mock_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.text = "Response"
        mock_instance.models.generate_content.return_value = mock_response
        
        generate(exact_prompt)
        
        mock_instance.models.generate_content.assert_called_once_with(
            model="test-model",
            contents=exact_prompt
        )

def test_missing_api_key():
    """Test 3: Missing GEMINI_API_KEY produces configuration error."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ConfigurationError, match="GEMINI_API_KEY is not set in the environment."):
            generate("Test prompt")

def test_gemini_apierror_failure(mock_env):
    """Test 4.1: Mock an explicit APIError from Gemini and verify it is handled cleanly."""
    with patch('src.gemini_adapter.genai.Client') as MockClient:
        mock_instance = MockClient.return_value
        api_error = errors.APIError(400, {"message": "Simulated API error"})
        mock_instance.models.generate_content.side_effect = api_error
        
        with pytest.raises(GenerationError, match="Gemini API Error: Simulated API error"):
            generate("Test prompt")

def test_gemini_api_failure(mock_env):
    """Test 4.2: Mock a provider failure and verify the adapter handles it cleanly."""
    with patch('src.gemini_adapter.genai.Client') as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.models.generate_content.side_effect = Exception("Simulated network failure")
        
        with pytest.raises(GenerationError, match="An unexpected error occurred during generation: Simulated network failure"):
            generate("Test prompt")
            
def test_gemini_empty_response(mock_env):
    """Test 4.3: Mock an empty response failure."""
    with patch('src.gemini_adapter.genai.Client') as MockClient:
        mock_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.text = ""
        mock_instance.models.generate_content.return_value = mock_response
        
        with pytest.raises(GenerationError, match="Model returned an empty or invalid response."):
            generate("Test prompt")
