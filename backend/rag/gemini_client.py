import google.generativeai as genai
from config import GEMINI_API_KEY, VISION_MODEL

_model = None

def get_gemini_model():
    """
    Loads and configures the Gemini model instance once across the app.
    """
    global _model
    if _model is None:
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel(VISION_MODEL)
    return _model