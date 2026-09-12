from langchain_huggingface import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL

_embedding = None

def get_embedding_model():
    global _embedding

    if _embedding is None:
        print("Loading embedding model...")
        _embedding = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

    return _embedding