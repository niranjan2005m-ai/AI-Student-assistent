from pathlib import Path

from langchain_chroma import Chroma

from config import CHROMA_PATH
from rag.embeddings import get_embedding_model


_vectorstore_instance = None


def create_vectorstore(chunks):
    """
    Create or update the Chroma database.

    If the database already exists, new chunks are added.
    Otherwise, a new database is created.
    """
    global _vectorstore_instance

    embeddings = get_embedding_model()
    db_path = Path(CHROMA_PATH)

    if db_path.exists():
        vectorstore = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings,
        )
        vectorstore.add_documents(chunks)
    else:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_PATH,
        )

    _vectorstore_instance = vectorstore
    return vectorstore


def load_vectorstore():
    """
    Load the Chroma vectorstore using a cached instance.
    """
    global _vectorstore_instance

    if _vectorstore_instance is not None:
        return _vectorstore_instance

    embeddings = get_embedding_model()

    _vectorstore_instance = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
    )

    return _vectorstore_instance


def get_retriever(document_id=None, k=6):
    """
    Return a Chroma retriever.

    When document_id is supplied, retrieval is restricted
    to chunks belonging to that document.
    """
    vs = load_vectorstore()

    search_kwargs = {
        "k": k,
    }

    if document_id:
        search_kwargs["filter"] = {
            "document_id": document_id,
        }

    return vs.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs,
    )


def vectorstore_exists():
    return Path(CHROMA_PATH).exists()