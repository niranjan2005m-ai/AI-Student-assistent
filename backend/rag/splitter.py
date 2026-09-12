from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):
    print(f"[SPLITTER] Documents received: {len(documents)}")

    non_empty = [
        doc for doc in documents
        if doc.page_content and doc.page_content.strip()
    ]

    print(
        f"[SPLITTER] Non-empty documents: "
        f"{len(non_empty)}"
    )

    for i, doc in enumerate(non_empty[:5]):
        print(
            f"[SPLITTER] Doc {i}: "
            f"{len(doc.page_content)} chars"
        )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = text_splitter.split_documents(
        non_empty
    )

    print(
        f"[SPLITTER] Chunks created: "
        f"{len(chunks)}"
    )

    return chunks