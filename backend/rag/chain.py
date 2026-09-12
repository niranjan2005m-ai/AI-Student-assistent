from rag.vectorstore import load_vectorstore
from rag.retriever import get_retriever
from rag.llm import get_llm
from rag.reranker import rerank


class RAGChain:

    def __init__(self):
        self.llm = get_llm()

    def _build_prompt(self, question, context, history):
        return f"""You are an expert AI Student Assistant with access to
retrieved information from an uploaded document.

Your job is to answer the user's question intelligently.

IMPORTANT RULES:

1. If the retrieved document context clearly contains the answer,
   prioritize that information and explain it accurately.

2. If the question is about the uploaded document but the retrieved
   context does not contain enough information:
   - do not pretend the document contains the answer;
   - clearly state that the requested detail was not found in the
     uploaded document;
   - then provide a useful general explanation when appropriate.

3. If the question is a general question and the retrieved document
   does not contain relevant information, answer using your normal
   knowledge instead of refusing to answer.

4. Never claim that general knowledge came from the uploaded document.

5. Do not invent facts from the document.

6. Use conversation history when it helps understand the question.

7. Use Markdown for readability.

8. For code, preserve code in fenced code blocks.

9. For mathematical expressions, preserve the mathematical notation.

10. For tables, use Markdown tables where useful.

Conversation history:
{history}

Retrieved document context:
{context}

Current question:
{question}

Answer naturally and directly:
"""

    def _prepare_prompt_and_docs(
        self,
        question: str,
        chat_history: list | None,
        document_id: str | None = None,
    ):
        if chat_history is None:
            chat_history = []

        # Keep only recent conversation context.
        recent_history = chat_history[-6:]

        # Retrieve only a small candidate set.
        retriever = get_retriever(
            document_id=document_id,
            k=6,
        )

        docs = retriever.invoke(question)

        # Rerank only retrieved candidates.
        if docs:
            docs = rerank(
                question,
                docs,
                top_k=3,
            )

        # Build retrieved context.
        context_parts = []

        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            page_val = doc.metadata.get("page", 0)

            page = (
                page_val + 1
                if isinstance(page_val, int)
                else page_val
            )

            context_parts.append(
                f"[Document {i}]\n"
                f"Source: {source}\n"
                f"Page: {page}\n"
                f"{doc.page_content}"
            )

        context = "\n\n".join(context_parts)

        # Build conversation history.
        history_parts = []

        for message in recent_history:
            content = message.get("content", "").strip()

            if not content:
                continue

            role = message.get("role", "user").capitalize()
            history_parts.append(f"{role}: {content}")

        history = "\n".join(history_parts)

        prompt = self._build_prompt(
            question,
            context,
            history,
        )

        return prompt, docs

    def ask(
        self,
        question: str,
        chat_history=None,
        document_id=None,
    ):
        prompt, docs = self._prepare_prompt_and_docs(
            question,
            chat_history,
            document_id,
        )

        response = self.llm.invoke(prompt)

        return {
            "answer": response.content,
            "sources": docs,
        }

    def stream(
        self,
        question: str,
        chat_history=None,
        document_id=None,
    ):
        prompt, docs = self._prepare_prompt_and_docs(
            question,
            chat_history,
            document_id,
        )

        return self.llm.stream(prompt), docs


_chain = None


def get_rag_chain():
    global _chain

    if _chain is None:
        print("Loading RAG Chain...")
        _chain = RAGChain()

    return _chain


def refresh_rag_chain():
    global _chain
    _chain = None