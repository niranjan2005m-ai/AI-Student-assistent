from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


def load_pdf(pdf_path):
    """
    Load a PDF and attach clean metadata for each page.
    """

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    filename = Path(pdf_path).name

    for doc in documents:
        doc.metadata["source"] = filename
        doc.metadata["filename"] = filename

    return documents