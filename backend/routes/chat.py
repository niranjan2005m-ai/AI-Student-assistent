from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from services.chat_service import (
    ask_question,
    stream_question,
    ask_agent,
    stream_agent_question,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    question: str
    chat_history: list = []
    session_id: str = "default"
    document_id: str | None = None


# ============================================================
# EXISTING RAG CHAT
# ============================================================

@router.post("/")
def chat(request: ChatRequest):

    result = ask_question(
        request.question,
        request.chat_history,
    )

    return {
        "success": True,
        "answer": result["answer"],
        "sources": [
            {
                "source": doc.metadata.get(
                    "source",
                    "Unknown",
                ),
                "page": (
                    doc.metadata.get(
                        "page",
                        0,
                    ) + 1
                    if isinstance(
                        doc.metadata.get(
                            "page",
                            0,
                        ),
                        int,
                    )
                    else doc.metadata.get(
                        "page",
                        "Unknown",
                    )
                ),
            }
            for doc in result.get(
                "sources",
                [],
            )
        ],
    }


# ============================================================
# EXISTING RAG STREAMING
# ============================================================

@router.post("/stream")
def stream_chat(request: ChatRequest):

    stream, _ = stream_question(
        request.question,
        request.chat_history,
    )

    def generate():

        for chunk in stream:

            if getattr(
                chunk,
                "content",
                "",
            ):
                yield chunk.content

    return StreamingResponse(
        generate(),
        media_type="text/plain",
    )


# ============================================================
# AGENT
# ============================================================

@router.post("/agent")
def agent_chat(request: ChatRequest):

    result = ask_agent(
        request.question,
        request.chat_history,
        request.session_id,
        request.document_id,
    )

    return {
        "success": True,
        "answer": result["answer"],
        "steps": result.get(
            "steps",
            [],
        ),
        "session": result.get(
            "session",
            {},
        ),
    }


# ============================================================
# AGENT STREAMING
# ============================================================

@router.post("/agent/stream")
def stream_agent_chat(request: ChatRequest):

    stream, steps = stream_agent_question(
        request.question,
        request.chat_history,
        request.session_id,
        request.document_id,
    )

    def generate():

        for chunk in stream:

            if chunk:
                yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/plain",
    )