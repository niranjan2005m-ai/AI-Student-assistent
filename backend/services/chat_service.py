from rag.chain import get_rag_chain
from rag.agent import run_agent, stream_agent


# ============================================================
# EXISTING RAG
# ============================================================

def ask_question(
    question: str,
    chat_history=None
):

    if chat_history is None:
        chat_history = []

    rag_chain = get_rag_chain()

    return rag_chain.ask(
        question=question,
        chat_history=chat_history
    )


def stream_question(
    question: str,
    chat_history=None
):

    if chat_history is None:
        chat_history = []

    rag_chain = get_rag_chain()

    return rag_chain.stream(
        question=question,
        chat_history=chat_history
    )


# ============================================================
# NEW AGENT
# ============================================================

def ask_agent(
    question,
    chat_history=None,
    session_id="default",
    document_id=None,
):
    return run_agent(
        question=question,
        chat_history=chat_history,
        session_id=session_id,
        active_document_id=document_id,
    )


def stream_agent_question(
    question,
    chat_history=None,
    session_id="default",
    document_id=None,
):
    return stream_agent(
        question=question,
        chat_history=chat_history,
        session_id=session_id,
        active_document_id=document_id,
    )