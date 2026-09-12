import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data"
CHROMA_PATH = BASE_DIR / "chroma_db"
UPLOAD_PATH = BASE_DIR / "uploads"

# Chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Embeddings
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# Main LLM
LLM_PROVIDER = "gemini"
GEMINI_MODEL = "gemini-3.6-flash"

# Vision
VISION_MODEL = "gemini-3.5-flash-lite"