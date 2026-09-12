from rag.loader import load_pdf


def get_document_text(pdf_path: str) -> str:
    """
    Load a PDF and return its complete text.
    """

    documents = load_pdf(pdf_path)

    text = "\n\n".join(
        doc.page_content
        for doc in documents
        if doc.page_content.strip()
    )

    return text


def get_documents(pdf_path: str):
    """
    Return LangChain Document objects.
    """

    return load_pdf(pdf_path)