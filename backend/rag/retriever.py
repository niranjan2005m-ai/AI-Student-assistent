from rag.vectorstore import load_vectorstore


def get_retriever(document_id=None, k=6):
    """
    Create a lightweight Chroma retriever.

    The vectorstore itself is cached by load_vectorstore(),
    so creating this retriever wrapper is cheap.
    """
    db = load_vectorstore()

    search_kwargs = {
        "k": k
    }

    if document_id:
        search_kwargs["filter"] = {
            "document_id": document_id
        }

    return db.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs,
    )


def refresh_retriever():
    """
    Kept for compatibility.

    The actual Chroma vectorstore is cached separately,
    so there is no retriever singleton to invalidate here.
    """
    pass