from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# -----------------------------
# Load Embedding Model
# -----------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# Load ChromaDB
# -----------------------------
vector_db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding_model
)

print(f"Documents in DB : {vector_db._collection.count()}")

# -----------------------------
# Create Retriever
# -----------------------------
retriever = vector_db.as_retriever(
    search_kwargs={"k": 3}
)

# -----------------------------
# Load Gemini
# -----------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0
)

print("\n========================================")
print("        RAG CHATBOT STARTED")
print("Type 'exit' to quit")
print("========================================")

while True:

    question = input("\nYou : ")

    if question.lower() == "exit":
        break

    # Retrieve documents
    docs = retriever.invoke(question)

    print(f"\nRetrieved {len(docs)} document(s)\n")

    if len(docs) == 0:
        print("No relevant documents found.")
        continue

    print("========== Retrieved Chunks ==========\n")

    context = ""

    for i, doc in enumerate(docs, start=1):

        print(f"Chunk {i}")
        print("-" * 50)
        print(doc.page_content[:500])
        print()

        context += doc.page_content + "\n\n"

    prompt = f"""
You are an AI assistant.

Answer ONLY from the given context.

If the answer is not found in the context, reply:

"I couldn't find the answer in the provided document."

Context:
{context}

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    print("\n==============================")
    print("Bot:\n")
    print(response.content)
    print("==============================")