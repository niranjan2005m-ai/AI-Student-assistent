from pydantic import BaseModel


class UploadResponse(BaseModel):
    success: bool
    document_id: str
    filename: str
    status: str
    pages: int | None = None
    chunks: int | None = None
    images: int | None = None
    tables: int | None = None
    ocr: bool
    embedding_model: str
    llm: str