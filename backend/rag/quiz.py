import json
from langchain_core.messages import HumanMessage

from rag.document_service import get_document_text
from rag.llm import get_llm


def generate_quiz(pdf_path: str, num_questions: int = 10):

    llm = get_llm()

    text = get_document_text(pdf_path)

    # Prevent extremely large prompts
    text = text[:15000]

    prompt = f"""
You are an experienced university professor.

Based ONLY on the document below, generate exactly {num_questions} multiple-choice questions.

Return ONLY valid JSON.

Format:

[
  {{
    "question": "...",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": 1,
    "explanation": "..."
  }}
]

Rules:
- Exactly 4 options.
- answer must be the index of the correct option.
- Index starts at 0.
- No markdown formatting (do not wrap in ```json).
- No explanation outside JSON.

Document:

{text}
"""
    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    try:
        # Parse the JSON string returned by the LLM into a Python object
        return json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback just in case the LLM messes up the formatting
        return [{"question": "Error generating quiz. LLM did not return valid JSON.", "options": ["A", "B", "C", "D"], "answer": 0, "explanation": "Please try again."}]