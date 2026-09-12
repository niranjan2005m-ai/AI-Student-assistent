from pathlib import Path

DATA_DIR = Path("data/documents")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_document(document_id: str, text: str):
    path = DATA_DIR / f"{document_id}.txt"
    path.write_text(text, encoding="utf-8")


def load_document(document_id: str) -> str:
    path = DATA_DIR / f"{document_id}.txt"

    if not path.exists():
        raise FileNotFoundError("Document not found.")

    return path.read_text(encoding="utf-8")