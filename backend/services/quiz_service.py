from langchain_core.messages import HumanMessage
import json

from rag.llm import get_llm
from services.document_store import load_document


def generate_quiz(document_id: str):

    llm = get_llm()

    document = load_document(document_id)

    prompt = f"""
You are an expert university professor.

Generate exactly 10 multiple-choice questions from the document.

Rules:

- Cover different topics from the document.
- Don't repeat questions.
- Four options only.
- One correct answer.
- Add a short explanation.
- Return ONLY valid JSON.

Format:

{{
    "questions":[
        {{
            "question":"...",
            "options":[
                "...",
                "...",
                "...",
                "..."
            ],
            "correctAnswerIndex":0,
            "explanation":"..."
        }}
    ]
}}

Document:

{document}
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    # Safely extract content to prevent the 'list' object strip() error
    content = response.content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
            elif isinstance(item, str):
                parts.append(item)
        content = "\n".join(parts)
    elif not isinstance(content, str):
        content = str(content)
        
    content = content.strip()

    # Remove markdown if model returns ```json
    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    return json.loads(content)