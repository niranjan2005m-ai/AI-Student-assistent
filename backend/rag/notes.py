from langchain_core.messages import HumanMessage

from rag.document_service import get_document_text
from rag.llm import get_llm


def generate_notes(pdf_path):

    llm = get_llm()

    text = get_document_text(pdf_path)

    text = text[:15000]

    prompt = f"""
You are an expert professor.

Read the document and create detailed study notes.

Structure exactly like this:

# Study Notes

## Overview

## Key Concepts

## Important Definitions

## Important Points

## Exam Tips

Use markdown.

Document:

{text}
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return response.content