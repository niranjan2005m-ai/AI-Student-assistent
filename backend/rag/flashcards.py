import json
import random
from langchain_core.messages import HumanMessage
from rag.document_service import get_document_text
from rag.llm import get_llm

def generate_flashcards(pdf_path, num_cards=15):
    llm = get_llm()
    text = get_document_text(pdf_path)
    
    # Prevent extremely large prompts, but randomize the chunk 
    # so you get DIFFERENT flashcards every time you generate!
    if len(text) > 15000:
        start = random.randint(0, len(text) - 15000)
        text = text[start : start + 15000]

    prompt = f"""
You are an expert professor.

Generate exactly {num_cards} flashcards based ONLY on the document.

Return ONLY valid JSON.

Format:
[
  {{
    "front": "Question",
    "back": "Answer"
  }}
]

Rules:
- EXACTLY {num_cards} flashcards
- Every flashcard MUST have both "front" and "back"
- NEVER leave "back" empty
- Keep each answer to ONE sentence (maximum 20 words)
- No markdown formatting (do not wrap in ```json)
- No explanations outside JSON
- Cover different topics from the document

Document: {text}
"""
    
    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    try:
        # 1. Safely extract content to prevent the 'list' object strip() error
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
        
        # Parse the JSON
        flashcards = json.loads(content)
        
        # 2. Validate them (Filters out any cards where front or back are missing/empty)
        valid_flashcards = [
            card for card in flashcards 
            if card.get("front") and card.get("back") and str(card.get("back")).strip() != ""
        ]
        
        # 3. Fallback if the strict validation removes all of them
        if not valid_flashcards:
            return [{"front": "Error", "back": "The AI generated incomplete flashcards. Please click generate again."}]
            
        return valid_flashcards
        
    except json.JSONDecodeError:
        # Fallback if the LLM completely fails to return valid JSON syntax
        return [{"front": "Error generating flashcards", "back": "The AI did not return valid JSON. Please try again."}]