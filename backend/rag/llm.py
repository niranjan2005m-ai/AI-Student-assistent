from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY, GEMINI_MODEL

_llm = None


def get_llm():
    global _llm

    if _llm is None:
        print("Loading Gemini LLM...")

        _llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0,
        )

    return _llm