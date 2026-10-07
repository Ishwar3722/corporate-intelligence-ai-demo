import os
import pytest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

@pytest.fixture(autouse=True)
def set_env():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
        yield

def test_supported_question_m9():
    """TEST 1: Supported question"""
    at = AppTest.from_file("../app.py", default_timeout=10)
    
    with patch("src.gemini_adapter.generate") as mock_generate:
        mock_generate.return_value = "Alphabet Q4 2023 revenue was $86.3 billion [ev_001]."
        at.run()
        at.text_input[0].input("What was Alphabet's revenue in Q4 2023?").run()
        # button[0] and [1] are suggested questions. button[2] is "Ask"
        at.button[2].click().run()
        
        # Regression Test: Ensure generate() is called without unsupported keyword arguments
        assert not mock_generate.call_args.kwargs, "generate() should not be called with keyword arguments like temperature"

        expanders = [e.label for e in at.expander]
        assert "Evidence Used" in expanders
        
        # Check for GROUNDED / ACCEPTED state
        assert len(at.success) > 0
        assert "GROUNDED / ACCEPTED" in at.success[0].value

def test_unsupported_question_m9():
    """TEST 2, 3: Unsupported question, zero Gemini calls"""
    at = AppTest.from_file("../app.py", default_timeout=10)
    
    with patch("src.gemini_adapter.generate") as mock_generate:
        at.run()
        # "cars" has 0 overlap with the sample evidence
        at.text_input[0].input("Tell me about cars.").run()
        at.button[2].click().run()
        
        # Verify zero Gemini calls (TEST 3)
        mock_generate.assert_not_called()
        
        # Verify insufficient-evidence state appears
        assert len(at.error) > 0
        assert "INSUFFICIENT EVIDENCE" in at.error[0].value
        
        # Verify markdown content
        markdown_text = "\n".join([m.value for m in at.markdown])
        assert "I couldn't find sufficient evidence" in markdown_text
        assert "will not generate an answer from outside knowledge" in markdown_text
        
        # Verify normal UI elements do not appear
        assert not any("GROUNDED / ACCEPTED" in s.value for s in at.success)

def test_rejected_answer_m9():
    """TEST: Rejected answer state"""
    at = AppTest.from_file("../app.py", default_timeout=10)
    
    with patch("src.gemini_adapter.generate") as mock_generate:
        # Mock generate to return something that will be rejected by the validator
        mock_generate.return_value = "Microsoft announced a new gaming console [ev_001]."
        at.run()
        at.text_input[0].input("What was Alphabet's revenue in Q4 2023?").run()
        at.button[2].click().run()
        
        # Check for REJECTED state
        assert len(at.error) > 0
        assert "REJECTED" in at.error[0].value
        
        markdown_text = "\n".join([m.value for m in at.markdown])
        assert "Unsupported Claims:" in markdown_text

def test_fallback_state_503():
    """TEST 1: Temporary 503-style GenerationError triggers fallback state"""
    from src.gemini_adapter import GenerationError
    at = AppTest.from_file("../app.py", default_timeout=10)
    
    with patch("src.gemini_adapter.generate") as mock_generate:
        mock_generate.side_effect = GenerationError("Gemini API Error", status_code=503)
        at.run()
        at.text_input[0].input("What was Alphabet's revenue in Q4 2023?").run()
        at.button[2].click().run()
        
        assert len(at.warning) > 0
        assert "EVIDENCE AVAILABLE" in at.warning[0].value
        
        markdown_text = "\n".join([m.value for m in at.markdown])
        assert "temporarily unavailable" in markdown_text
        
        mock_generate.assert_called_once()
        assert not any("Gemini API failure" in getattr(s, 'value', '') for s in at.error)

def test_permanent_error_no_fallback():
    """TEST 2: Permanent error triggers normal error state, not fallback"""
    from src.gemini_adapter import GenerationError
    at = AppTest.from_file("../app.py", default_timeout=10)
    
    with patch("src.gemini_adapter.generate") as mock_generate:
        mock_generate.side_effect = GenerationError("Gemini API Error", status_code=400)
        at.run()
        at.text_input[0].input("What was Alphabet's revenue in Q4 2023?").run()
        at.button[2].click().run()
        
        assert len(at.error) > 0
        assert "Gemini API failure" in at.error[0].value
        assert len(at.warning) == 0
        mock_generate.assert_called_once()
