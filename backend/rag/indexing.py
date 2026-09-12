from pathlib import Path

from rag.ingest import ingest_pdf
from rag.vectorstore import create_vectorstore



def index_pdf(pdf_path: str | Path):
    """
    Complete indexing pipeline.
    """

    chunks = ingest_pdf(pdf_path)

    if not chunks:
        raise ValueError("No chunks were created.")

    vectorstore = create_vectorstore(chunks)

    return vectorstore