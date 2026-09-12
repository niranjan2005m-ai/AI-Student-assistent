from fastapi import APIRouter, UploadFile, File
from services.upload_service import upload_pdf
from schemas.upload import UploadResponse

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    return upload_pdf(file)