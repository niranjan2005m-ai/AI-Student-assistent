from sentence_transformers import CrossEncoder

_reranker = None


def get_reranker():
    global _reranker

    if _reranker is None:
        print("Loading reranker...")
        _reranker = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    return _reranker


def rerank(question, docs, top_k=3):
    """
    Rerank retrieved LangChain Documents.
    """
    if not docs:
        return []

    # No need to rerank when there are already only a few documents.
    if len(docs) <= top_k:
        return docs

    model = get_reranker()

    pairs = [
        (question, doc.page_content)
        for doc in docs
    ]

    scores = model.predict(
        pairs,
        batch_size=8,
        show_progress_bar=False,
    )

    ranked = sorted(
        zip(scores, docs),
        key=lambda x: x[0],
        reverse=True,
    )

    return [
        doc
        for _, doc in ranked[:top_k]
    ]