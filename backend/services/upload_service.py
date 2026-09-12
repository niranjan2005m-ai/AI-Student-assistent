from pathlib import Path
from uuid import uuid4
import shutil

from rag.indexing import index_pdf
from schemas.upload import UploadResponse
from services.document_store import save_document
from rag.loader import load_pdf

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def upload_pdf(file):
    document_id = str(uuid4())
    filename = f"{document_id}_{file.filename}"
    file_path = UPLOAD_DIR / filename

    # 1. Save the file and close it automatically when exiting the 'with' block
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Now that the file is safely saved on disk, load and process it
    documents = load_pdf(file_path)
    full_text = "\n\n".join(doc.page_content for doc in documents) # Removed the trailing \
    
    save_document(document_id, full_text)
    index_pdf(file_path)
    
    return UploadResponse(
        success=True,
        document_id=document_id,
        filename=file.filename,
        status="ready",
        pages=None,
        chunks=None,
        images=None,
        tables=None,
        ocr=True,
        embedding_model="BAAI/bge-small-en-v1.5",
        llm="llama-3.3-70b-versatile"
    )