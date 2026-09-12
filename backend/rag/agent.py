import json
import logging
from pathlib import Path
from typing import Any

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool

from config import UPLOAD_PATH
from rag.chain import get_rag_chain
from rag.llm import get_llm
from rag.summarizer import summarize_pdf
from rag.notes import generate_notes
from rag.quiz import generate_quiz
from rag.flashcards import generate_flashcards
from services.study_session import (
    get_or_create_session,
    session_summary,
    update_from_evaluation,
    set_topic,
    set_question,
)

logger = logging.getLogger(__name__)

MAX_AGENT_STEPS = 3

AGENT_SYSTEM_PROMPT = """
You are an intelligent AI Student Assistant.

You can:
- have normal conversations,
- answer general knowledge questions,
- answer questions using uploaded PDFs,
- teach topics,
- evaluate student answers,
- summarize documents,
- create notes,
- generate quizzes,
- generate flashcards,
- choose the next study topic.

IMPORTANT BEHAVIOR:

1. GENERAL CONVERSATION
   Respond naturally to greetings, casual conversation, thanks,
   clarification, and other normal chat.
   Do not search the PDF for greetings.

2. GENERAL KNOWLEDGE
   If the user asks a general question that does not require the
   uploaded document, answer it normally using your knowledge.

3. DOCUMENT QUESTIONS
   When the user asks about the uploaded document, prioritize the
   uploaded document and use document retrieval.

4. DOCUMENT + GENERAL KNOWLEDGE
   If the user's question is related to the uploaded document but
   the retrieved context does not contain enough information,
   do NOT simply stop with "not found".
   Explain that the requested detail is not present in the uploaded
   document and then provide a general explanation when useful.

5. NEVER HALLUCINATE DOCUMENT CONTENT
   Never claim that information came from the uploaded document
   unless it is actually supported by retrieved document context.

6. ACTIVE DOCUMENT
   When an active document ID is supplied by the application,
   use that document for document-specific operations.

7. INTERNAL IDENTIFIERS
   Never expose, repeat, or mention internal document IDs,
   tool payloads, or implementation details to the user.

8. TOOLS
   Use the appropriate tool when the user asks for:
   - teaching,
   - evaluation,
   - summary,
   - notes,
   - quiz,
   - flashcards,
   - next study topic,
   - document search.

9. TEACHING
   If the user asks to teach a topic, use teach_topic.

10. STUDY SESSION
    The study session is the source of truth for the current topic,
    current question, score, attempts, weak topics, and mastered topics.

11. ANSWER EVALUATION
    If the study session contains a current question and the user's
    message appears to answer it, evaluate the answer using the
    stored question.

12. ADAPTIVE LEARNING
    After evaluation:
    - REVISE → teach the weak topic again.
    - ADVANCE → move to the next appropriate topic.

13. DO NOT PERFORM UNREQUESTED ACTIONS.

14. Keep answers natural, helpful, and focused on the user's request.
"""

GENERAL_CHAT_PROMPT = """
You are a friendly and intelligent AI Student Assistant.

You can have normal conversations and answer general questions.

For casual conversation:
- respond naturally,
- be warm and concise,
- do not mention PDFs unless relevant.

For general questions:
- answer accurately,
- explain clearly,
- use examples when useful,
- do not pretend the answer came from an uploaded document.
"""

def _safe_json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, indent=2)
    except TypeError:
        return str(value)

def extract_llm_text(content) -> str:
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text", "")
                if text:
                    parts.append(str(text))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts).strip()

    if isinstance(content, dict):
        text = content.get("text", "")
        if text:
            return str(text).strip()

    if content is None:
        return ""

    return str(content).strip()

# ============================================================
# HELPER FUNCTIONS & ROUTING DETECTORS
# ============================================================

def _history_to_messages(chat_history: list | None) -> list:
    messages = []
    for message in chat_history or []:
        role = message.get("role", "")
        content = message.get("content", "")
        if not content: continue
        if role == "user": messages.append(HumanMessage(content=content))
        elif role == "assistant": messages.append(AIMessage(content=content))
    return messages

def _build_initial_messages(question: str, chat_history: list | None) -> list:
    return [SystemMessage(content=AGENT_SYSTEM_PROMPT), *_history_to_messages(chat_history), HumanMessage(content=question)]

def _recent_history(chat_history: list | None, limit: int = 6) -> list:
    return (chat_history or [])[-limit:]

def _is_document_action(question: str) -> str | None:
    text = question.strip().lower()
    if "generate notes" in text or text == "notes": return "notes"
    if "summary" in text or "summarize" in text: return "summary"
    if "flashcards" in text or "flash cards" in text: return "flashcards"
    if "generate quiz" in text or "make a quiz" in text or text == "quiz": return "quiz"
    return None

def _is_greeting(question: str) -> bool:
    text = question.strip().lower()
    text = text.strip(" \t\n!?.,:")

    greetings = {
        "hi", "hello", "hey", "hii", "hiii", 
        "good morning", "good afternoon", "good evening", "good night", 
        "yo", "hey there",
    }
    return text in greetings

def _is_casual_conversation(question: str) -> bool:
    text = question.strip().lower()
    casual_patterns = (
        "how are you", "how are u", "what's up", "whats up", 
        "who are you", "what can you do", "thank you", "thanks", 
        "thank u", "good job", "nice", "okay", "ok",
    )
    return _is_greeting(question) or text in casual_patterns

def _is_new_request(question: str) -> bool:
    text = question.strip().lower()
    new_request_prefixes = (
        "teach me", "teach ", "explain ", "summarize", "make notes",
        "generate quiz", "make a quiz", "generate flashcards",
        "make flashcards", "list documents", "upload ",
    )
    exact_requests = {
        "explain", "summary", "summarize", "notes", "quiz", "flashcards",
    }
    return text in exact_requests or text.startswith(new_request_prefixes)

def answer_general_question(question: str, chat_history: list | None = None) -> str:
    messages = [
        SystemMessage(content=GENERAL_CHAT_PROMPT),
        *_history_to_messages(_recent_history(chat_history, 6)),
        HumanMessage(content=question),
    ]
    response = get_llm().invoke(messages)
    return extract_llm_text(response.content)

# ============================================================
# TOOLS
# ============================================================

@tool
def list_documents() -> str:
    """List all PDF documents currently available in the uploads directory."""
    UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
    documents = sorted([p.name for p in UPLOAD_PATH.glob("*.pdf") if p.is_file()])
    if not documents:
        return "No PDF documents are currently uploaded."
    return "Available PDF documents:\n" + "\n".join(f"- {name}" for name in documents)

@tool
def search_documents(question: str, document_id: str | None = None) -> str:
    """Search the indexed PDFs using the existing RAG retrieval pipeline."""
    if not question.strip():
        return "The search question is empty."
    result = get_rag_chain().ask(
        question=question,
        chat_history=[],
        document_id=document_id
    )
    payload = {
        "answer": result.get("answer", ""),
        "sources": [
            {
                "source": doc.metadata.get("source", "Unknown"),
                "page": (doc.metadata.get("page", 0) + 1 if isinstance(doc.metadata.get("page", 0), int) else doc.metadata.get("page", "Unknown"))
            }
            for doc in result.get("sources", [])
        ]
    }
    return _safe_json(payload)

@tool
def teach_topic(topic: str, document_id: str | None = None) -> str:
    """Teach a topic and generate a follow-up question using uploaded PDFs."""
    if not topic or not topic.strip():
        return _safe_json({"found": False, "message": "The topic is empty."})
    
    rag_chain = get_rag_chain()
    _, docs = rag_chain._prepare_prompt_and_docs(
        question=f"Find the information about '{topic}' that is present in the uploaded documents.",
        chat_history=[],
        document_id=document_id
    )
    
    if not docs:
        return _safe_json({
            "topic": topic,
            "found": False,
            "message": "I couldn't find information about this topic in the uploaded documents."
        })

    context_parts = []
    for i, doc in enumerate(docs, 1):
        page_value = doc.metadata.get("page", 0)
        page = page_value + 1 if isinstance(page_value, int) else page_value
        context_parts.append(f"[Source {i}]\nDocument: {doc.metadata.get('source', 'Unknown')}\nPage: {page}\nContent:\n{doc.page_content}")

    context = "\n\n".join(context_parts)
    
    teaching_prompt = f"""
You are a patient teacher.
Teach the topic below using ONLY the provided document context.

Topic:
{topic}

Document Context:
{context}

Teaching requirements:
1. Start with a simple definition.
2. Explain the concept step by step.
3. Use examples only when supported by the document.
4. Highlight important points.
5. Explain difficult terminology simply.
6. Do not add outside information.
7. Generate exactly ONE follow-up study question about this topic based on the context.

Return ONLY a valid JSON object with this exact structure:
{{
    "lesson": "Your full Markdown-formatted lesson here. Use proper newlines (\\n).",
    "question": "The follow-up study question.",
    "expected_points": ["Point 1", "Point 2"],
    "difficulty": "medium"
}}
"""
    response = get_llm().invoke(teaching_prompt)
    raw_response = extract_llm_text(response.content).strip()
    
    try:
        start = raw_response.find("{")
        end = raw_response.rfind("}") + 1
        if start == -1 or end <= start: raise ValueError("No JSON object found.")
        parsed_result = json.loads(raw_response[start:end])
    except Exception:
        parsed_result = {
            "lesson": "I had trouble generating the lesson in the correct format.",
            "question": None,
            "expected_points": [],
            "difficulty": "medium"
        }

    return _safe_json({
        "topic": topic,
        "found": True,
        "lesson": parsed_result.get("lesson", ""),
        "question": parsed_result.get("question"),
        "expected_points": parsed_result.get("expected_points", []),
        "difficulty": parsed_result.get("difficulty", "medium"),
        "sources": [{"source": doc.metadata.get("source", "Unknown"), "page": (doc.metadata.get("page", 0) + 1 if isinstance(doc.metadata.get("page", 0), int) else doc.metadata.get("page", "Unknown"))} for doc in docs]
    })

@tool
def evaluate_answer(question: str, student_answer: str, document_id: str | None = None) -> str:
    """Evaluate a student's answer against the uploaded PDFs."""
    if not question or not question.strip():
        return _safe_json({"found": False, "error": "The question is empty."})
    if not student_answer or not student_answer.strip():
        return _safe_json({"found": False, "error": "The student's answer is empty."})

    rag_chain = get_rag_chain()
    _, docs = rag_chain._prepare_prompt_and_docs(
        question=question, 
        chat_history=[],
        document_id=document_id
    )
    if not docs:
        return _safe_json({"found": False, "question": question, "student_answer": student_answer, "error": "I couldn't find enough information in the uploaded documents to evaluate this answer."})

    context_parts = []
    for i, doc in enumerate(docs, 1):
        page_value = doc.metadata.get("page", 0)
        page = page_value + 1 if isinstance(page_value, int) else page_value
        context_parts.append(f"[Source {i}]\nDocument: {doc.metadata.get('source', 'Unknown')}\nPage: {page}\nContent:\n{doc.page_content}")
    context = "\n\n".join(context_parts)

    evaluation_prompt = f"""
You are an educational answer evaluator. Evaluate the student's answer using ONLY the reference information from the uploaded document. Do NOT use outside knowledge.

QUESTION: {question}
STUDENT ANSWER: {student_answer}
REFERENCE INFORMATION: {context}

Return ONLY valid JSON using exactly this structure:
{{
    "correct": true,
    "score": 0,
    "feedback": "...",
    "mistakes": [],
    "improvement": "...",
    "needs_revision": false,
    "weak_topics": []
}}
"""
    response = get_llm().invoke(evaluation_prompt)
    raw_evaluation = extract_llm_text(response.content).strip()
    
    try:
        start = raw_evaluation.find("{")
        end = raw_evaluation.rfind("}") + 1
        if start == -1 or end <= start: raise ValueError("No JSON object found.")
        evaluation = json.loads(raw_evaluation[start:end])
    except Exception:
        return _safe_json({"found": True, "question": question, "student_answer": student_answer, "evaluation_error": "The evaluator returned an invalid structured response.", "raw_evaluation": raw_evaluation, "sources": []})

    score = max(0, min(int(evaluation.get("score", 0)), 10))
    return _safe_json({
        "found": True,
        "question": question,
        "student_answer": student_answer,
        "correct": bool(evaluation.get("correct", score >= 7)),
        "score": score,
        "feedback": str(evaluation.get("feedback", "")),
        "mistakes": evaluation.get("mistakes", []) if isinstance(evaluation.get("mistakes", []), list) else [str(evaluation.get("mistakes", []))],
        "improvement": str(evaluation.get("improvement", "")),
        "needs_revision": bool(evaluation.get("needs_revision", score < 7)),
        "weak_topics": evaluation.get("weak_topics", []) if isinstance(evaluation.get("weak_topics", []), list) else [str(evaluation.get("weak_topics", []))],
        "sources": [{"source": doc.metadata.get("source", "Unknown"), "page": (doc.metadata.get("page", 0) + 1 if isinstance(doc.metadata.get("page", 0), int) else doc.metadata.get("page", "Unknown"))} for doc in docs]
    })

@tool
def adaptive_study_action(session_id: str) -> str:
    """Determine the next learning action from the current study state."""
    session = get_or_create_session(session_id)
    if session.last_score is None:
        return _safe_json({"action": "CONTINUE", "topic": session.current_topic, "reason": "No evaluation has been recorded yet.", "session": session_summary(session)})
    if session.last_score < 7:
        weak_topic = session.weak_topics[0] if session.weak_topics else ""
        topic = f"{session.current_topic}: {weak_topic}" if session.current_topic and weak_topic else (weak_topic or session.current_topic or "")
        return _safe_json({"action": "REVISE", "topic": topic, "weak_topic": weak_topic, "reason": f"The student scored {session.last_score}/10. The concept needs reinforcement.", "session": session_summary(session)})
    return _safe_json({"action": "ADVANCE", "topic": session.current_topic, "reason": f"The student scored {session.last_score}/10. The topic appears sufficiently understood.", "session": session_summary(session)})

@tool
def get_study_session_status(session_id: str) -> str:
    """Get the current learning state of the student."""
    session = get_or_create_session(session_id)
    return _safe_json(session_summary(session))

def _resolve_pdf(document_name: str) -> Path:
    """Resolve a PDF by exact filename or document ID prefix."""
    if not document_name or not document_name.strip(): raise ValueError("document_name is required.")
    requested = document_name.strip()
    UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
    exact_path = UPLOAD_PATH / Path(requested).name
    if exact_path.is_file() and exact_path.suffix.lower() == ".pdf": return exact_path
    matches = list(UPLOAD_PATH.glob(f"{requested}_*.pdf"))
    if len(matches) == 1: return matches[0]
    if len(matches) > 1: raise ValueError(f"Multiple PDFs matched document ID '{requested}'.")
    raise FileNotFoundError(f"Document '{requested}' was not found in the uploads directory.")

@tool
def get_next_topic(session_id: str,document_id: str | None = None,) -> str:
    """Choose the next important topic to study from the uploaded documents."""
    session = get_or_create_session(session_id)
    current_topic = session.current_topic or ""
    _, docs = get_rag_chain()._prepare_prompt_and_docs(question="Identify the major topics and concepts covered in the uploaded documents.", chat_history=[], document_id=document_id)
    if not docs: return _safe_json({"found": False, "message": "No relevant document content found."})
    
    context = "\n\n".join(doc.page_content for doc in docs)
    prompt = f"You are creating the next study step for a student.\nCurrent topic: {current_topic}\nMastered topics: {session.mastered_topics}\nWeak topics: {session.weak_topics}\nBased ONLY on the document context below, choose ONE important topic that the student should study next. Return ONLY valid JSON: {{\"topic\": \"...\", \"reason\": \"...\"}}\nDOCUMENT CONTEXT:\n{context}"
    
    response = get_llm().invoke(prompt)
    raw = extract_llm_text(response.content).strip()
    
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        result = json.loads(raw[start:end])
    except Exception:
        return _safe_json({"found": False, "message": "Could not determine the next topic.", "raw": raw})
    return _safe_json({"found": True, **result})

@tool
def generate_document_summary(document_name: str) -> str:
    """Generate a concise summary of the specified PDF document."""
    pdf_path = _resolve_pdf(document_name)
    return extract_llm_text(summarize_pdf(str(pdf_path)))

@tool
def generate_document_notes(document_name: str) -> str:
    """Generate structured study notes from the specified PDF document."""
    pdf_path = _resolve_pdf(document_name)
    return extract_llm_text(generate_notes(str(pdf_path)))

@tool
def generate_document_quiz(document_name: str, num_questions: int = 10) -> str:
    """Generate a quiz from the specified PDF document."""
    pdf_path = _resolve_pdf(document_name)
    return _safe_json(generate_quiz(pdf_path, max(5, min(int(num_questions), 20))))

@tool
def generate_document_flashcards(document_name: str, num_cards: int = 10) -> str:
    """Generate study flashcards from the specified PDF document."""
    pdf_path = _resolve_pdf(document_name)
    return _safe_json(generate_flashcards(str(pdf_path), max(5, min(int(num_cards), 20))))

@tool
def generate_study_question(topic: str, difficulty: str = "medium", document_id: str | None = None) -> str:
    """Generate one document-grounded study question for a topic."""
    if not topic or not topic.strip(): return _safe_json({"found": False, "error": "Topic is empty."})
    _, docs = get_rag_chain()._prepare_prompt_and_docs(question=f"Find the important information about {topic}.", chat_history=[], document_id=document_id)
    if not docs: return _safe_json({"found": False, "error": "I couldn't find enough information about this topic."})
    
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"Generate exactly ONE question about:\nTOPIC: {topic}\nDIFFICULTY: {difficulty}\nUse ONLY the following document context:\n{context}\nReturn ONLY JSON: {{\"question\": \"...\", \"expected_points\": [\"...\"], \"difficulty\": \"{difficulty}\"}}"
    
    response = get_llm().invoke(prompt)
    raw = extract_llm_text(response.content).strip()
    
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        result = json.loads(raw[start:end])
    except Exception:
        return _safe_json({"found": False, "error": "Could not parse generated question.", "raw": raw})
    return _safe_json({"found": True, **result})

TOOLS = [
    list_documents, search_documents, teach_topic, generate_study_question,
    evaluate_answer, adaptive_study_action, get_next_topic, get_study_session_status,
    generate_document_summary, generate_document_notes, generate_document_quiz, generate_document_flashcards,
]
TOOL_MAP = {tool.name: tool for tool in TOOLS}

# ============================================================
# AGENT
# ============================================================

def run_agent(
    question: str,
    chat_history: list | None = None,
    session_id: str = "default",
    active_document_id: str | None = None,
) -> dict:

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    session = get_or_create_session(session_id)
    document_action = _is_document_action(question)

    # 0. NORMAL CONVERSATION / CASUAL CHAT
    if _is_casual_conversation(question):
        answer = answer_general_question(question, chat_history)
        return {
            "answer": answer,
            "steps": [],
            "session": session_summary(session),
        }

    # 1. DIRECT ACTIVE-DOCUMENT ACTION
    if document_action and active_document_id:
        try:
            if document_action == "notes": result = generate_document_notes.invoke({"document_name": active_document_id})
            elif document_action == "summary": result = generate_document_summary.invoke({"document_name": active_document_id})
            elif document_action == "quiz": result = generate_document_quiz.invoke({"document_name": active_document_id})
            elif document_action == "flashcards": result = generate_document_flashcards.invoke({"document_name": active_document_id})
            else: result = None

            if result is not None:
                return {
                    "answer": extract_llm_text(result),
                    "steps": [],
                    "session": session_summary(session),
                }
        except Exception as exc:
            logger.exception("Active document action failed: %s", exc)
            return {"answer": f"Failed to process the active document: {exc}", "steps": [], "session": session_summary(session)}
    
    # 2. FAST RAG PATH
    if (
        active_document_id
        and not session.current_question
        and not document_action
        and not _is_new_request(question)
        and not _is_casual_conversation(question)
    ):
        try:
            recent_history = _recent_history(chat_history, limit=6)
            rag_result = get_rag_chain().ask(
                question=question,
                chat_history=recent_history,
                document_id=active_document_id
            )
            return {
                "answer": extract_llm_text(rag_result.get("answer", "")),
                "steps": [{"tool": "fast_rag", "args": {}}],
                "session": session_summary(session)
            }
        except Exception as exc:
            logger.exception("Fast RAG path failed: %s", exc)

    # 3. GENERAL KNOWLEDGE / NORMAL QUESTION
    if (
        not session.current_question
        and not document_action
        and not _is_new_request(question)
    ):
        answer = answer_general_question(
            question,
            chat_history,
        )
        return {
            "answer": answer,
            "steps": [],
            "session": session_summary(session),
        }

    # 4. AUTOMATIC ANSWER DETECTION
    if session.current_question and not _is_new_request(question):
        evaluation_result = evaluate_answer.invoke({
            "question": session.current_question, 
            "student_answer": question,
            "document_id": active_document_id
        })
        
        try: evaluation = json.loads(str(evaluation_result))
        except Exception: evaluation = {"found": False}

        steps = [{"tool": "evaluate_answer", "args": {"question": session.current_question, "student_answer": question, "document_id": active_document_id}}]

        if evaluation.get("found") is True:
            update_from_evaluation(session, evaluation)
            adaptive_result = adaptive_study_action.invoke({"session_id": session_id})
            steps.append({"tool": "adaptive_study_action", "args": {"session_id": session_id}})

            try: adaptive_data = json.loads(str(adaptive_result))
            except Exception: adaptive_data = {}

            action = adaptive_data.get("action")
            response_text = f"### Evaluation \n\n**Score:** {evaluation.get('score', 0)}/10 \n\n{evaluation.get('feedback', '')} \n\n**Improvement:** {evaluation.get('improvement', '')}"

            if action == "REVISE":
                weak_topic = adaptive_data.get("topic")
                if weak_topic:
                    teach_result = teach_topic.invoke({
                        "topic": weak_topic,
                        "document_id": active_document_id
                    })
                    steps.append({"tool": "teach_topic", "args": {"topic": weak_topic, "document_id": active_document_id}})
                    
                    try: teach_data = json.loads(str(teach_result))
                    except Exception: teach_data = {}
                    
                    if teach_data.get("found") is True:
                        session.current_question = teach_data.get("question")
                        response_text += "\n\n### Let's Review This \n\n" + teach_data.get("lesson", "")
                        if session.current_question: response_text += "\n\n### Next Question \n\n" + session.current_question

            elif action == "ADVANCE":
                next_topic_result = get_next_topic.invoke({"session_id": session_id, "document_id": active_document_id})
                steps.append({"tool": "get_next_topic", "args": {"session_id": session_id}})
                
                try: next_topic_data = json.loads(str(next_topic_result))
                except Exception: next_topic_data = {"found": False}

                if next_topic_data.get("found") is True:
                    next_topic = next_topic_data.get("topic")
                    if next_topic:
                        teach_result = teach_topic.invoke({
                            "topic": next_topic,
                            "document_id": active_document_id
                        })
                        steps.append({"tool": "teach_topic", "args": {"topic": next_topic, "document_id": active_document_id}})
                        
                        try: teach_data = json.loads(str(teach_result))
                        except Exception: teach_data = {}
                        
                        set_topic(session, next_topic)
                        new_question = teach_data.get("question")
                        if new_question: set_question(session, new_question)
                        
                        response_text += "\n\n### ✅ Topic Mastered\n\n**Next Topic: " + str(next_topic) + "**\n\n" + teach_data.get("lesson", "")
                        if new_question: response_text += "\n\n### Quick Check\n\n" + new_question
                else:
                    response_text += "\n\n### ✅ Topic Mastered\n\nYou have completed the current topic. There were no additional topics I could reliably identify from the uploaded material."

            return {"answer": response_text, "steps": steps, "session": session_summary(session)}

    # 5. NEW REQUEST HANDLING (Standard Agent Loop)
    llm = get_llm().bind_tools(TOOLS)
    messages = _build_initial_messages(question, chat_history)
    steps = []
    executed_tool_calls = set()

    for step in range(MAX_AGENT_STEPS):
        response = llm.invoke(messages)
        messages.append(response)
        tool_calls = getattr(response, "tool_calls", None) or []

        if not tool_calls:
            return {"answer": extract_llm_text(response.content), "steps": steps, "session": session_summary(session)}

        for tool_call in tool_calls:
            name = tool_call["name"]
            args = tool_call.get("args", {}) or {}
            
            # Inject active_document_id dynamically for tools that need it but LLM missed it
            if name in ["teach_topic", "evaluate_answer"] and "document_id" not in args:
                args["document_id"] = active_document_id
                
            tool_signature = (name, json.dumps(args, sort_keys=True, ensure_ascii=False))

            if tool_signature in executed_tool_calls:
                tool_result = "This exact tool call has already been executed. Use the result already provided."
            else:
                executed_tool_calls.add(tool_signature)
                tool_fn = TOOL_MAP.get(name)
                
                if tool_fn is None: 
                    tool_result = f"Unknown tool requested: {name}"
                else:
                    try: 
                        tool_result = tool_fn.invoke(args)
                    except Exception as exc: 
                        tool_result = f"Tool execution failed: {type(exc).__name__}: {exc}"
                    
                    if name == "teach_topic":
                        try:
                            teach_result = json.loads(str(tool_result))
                            if teach_result.get("found") is True:
                                topic = teach_result.get("topic", args.get("topic", ""))
                                if topic and (not session.current_topic or session.current_topic.strip().lower() == topic.strip().lower()):
                                    set_topic(session, topic)
                                
                                generated_question = teach_result.get("question")
                                if generated_question: set_question(session, generated_question)
                                
                                return {
                                    "answer": teach_result.get("lesson", "") + ("\n\n### Quick Check\n\n" + generated_question if generated_question else ""),
                                    "steps": steps + [{"tool": name, "args": args}],
                                    "session": session_summary(session)
                                }
                            return {"answer": teach_result.get("message", "I couldn't find that topic."), "steps": steps + [{"tool": name, "args": args}], "session": session_summary(session)}
                        except Exception:
                            return {"answer": str(tool_result), "steps": steps + [{"tool": name, "args": args}], "session": session_summary(session)}

            steps.append({"tool": name, "args": args})
            messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))

    return {"answer": "I reached the maximum number of reasoning steps.", "steps": steps, "session": session_summary(session)}


# ============================================================
# STREAMING AGENT
# ============================================================

def stream_agent(
    question: str,
    chat_history: list | None = None,
    session_id: str = "default",
    active_document_id: str | None = None,
):
    session = get_or_create_session(session_id)

    # 1. NORMAL CHAT / GENERAL QUESTION STREAMING
    if (
        not session.current_question
        and not _is_document_action(question)
        and (
            _is_casual_conversation(question)
            or (not active_document_id and not _is_new_request(question))
        )
    ):
        messages = [
            SystemMessage(content=GENERAL_CHAT_PROMPT),
            *_history_to_messages(_recent_history(chat_history, 6)),
            HumanMessage(content=question),
        ]

        def general_stream():
            for chunk in get_llm().stream(messages):
                content = chunk.content if hasattr(chunk, "content") else chunk
                text = extract_llm_text(content)
                if text:
                    yield text

        return general_stream(), []

    # 2. ACTIVE DOCUMENT FAST RAG STREAMING
    if (
        active_document_id
        and not session.current_question
        and not _is_document_action(question)
        and not _is_new_request(question)
        and not _is_casual_conversation(question)
    ):
        try:
            recent_history = _recent_history(chat_history, limit=6)

            stream_gen, _ = get_rag_chain().stream(
                question=question,
                chat_history=recent_history,
                document_id=active_document_id,
            )

            def generate_stream():
                for chunk in stream_gen:
                    content = chunk.content if hasattr(chunk, "content") else chunk
                    text = extract_llm_text(content)
                    if text:
                        yield text

            return generate_stream(), [{"tool": "fast_rag", "args": {}}]

        except Exception as exc:
            logger.exception("Streaming Fast RAG failed: %s", exc)

    # 3. COMPLEX / STUDY / TOOL AGENT FALLBACK
    result = run_agent(
        question=question,
        chat_history=chat_history,
        session_id=session_id,
        active_document_id=active_document_id,
    )

    answer = result.get("answer", "")
    if not isinstance(answer, str):
        answer = extract_llm_text(answer)

    # Note: Standard tool execution is synchronous in `run_agent`.
    # We yield the final computed string here so it fits the streaming UI pipeline.
    return iter([answer]), result.get("steps", [])