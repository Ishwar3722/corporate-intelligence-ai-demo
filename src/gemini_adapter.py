import os
from google import genai
from google.genai import errors

class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""
    pass

class GenerationError(Exception):
    """Raised when the model fails to generate a response."""
    pass

def generate(prompt: str) -> str:
    """
    Sends a prompt to the Gemini model and returns the response.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ConfigurationError("GEMINI_API_KEY is not set in the environment.")

    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        if not response.text:
             raise GenerationError("Model returned an empty or invalid response.")
        return response.text
    except errors.APIError as e:
        raise GenerationError(f"Gemini API Error: {e.message}")
    except Exception as e:
        raise GenerationError(f"An unexpected error occurred during generation: {str(e)}")
