from fastapi import APIRouter
from pydantic import BaseModel

from services.quiz_service import generate_quiz

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"]
)


class QuizRequest(BaseModel):
    document_id: str


@router.post("/")
def quiz(request: QuizRequest):

    return generate_quiz(request.document_id)