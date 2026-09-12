from functools import lru_cache

from langchain_core.messages import HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.loader import load_pdf
from rag.llm import get_llm


@lru_cache(maxsize=10)
def summarize_pdf(pdf_path):
    """
    Generate an executive summary of a PDF.
    Optimized for Groq's free-tier token limits.
    """

    documents = load_pdf(pdf_path)

    text = "\n\n".join(
        doc.page_content
        for doc in documents
        if doc.page_content.strip()
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=12000,
        chunk_overlap=500,
    )

    chunks = splitter.split_text(text)

    # Limit API usage
    chunks = chunks[:3]

    prompt = f"""
You are an expert professor.

Below are sections extracted from a PDF.

Create a detailed Executive Summary.

Structure exactly as:

# Executive Summary

## Overview

## Key Concepts

## Important Topics

## Key Takeaways

## Conclusion

PDF Content:

{' '.join(chunks)}
"""

    llm = get_llm()

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return response.content