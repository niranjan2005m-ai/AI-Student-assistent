from typing import List, Optional
from langchain_core.documents import Document


def merge_documents(
    pdf_docs: List[Document],
    page_indices: List[int],
    ocr_texts: Optional[List[str]] = None,
    vision_texts: Optional[List[str]] = None,
    math_texts: Optional[List[str]] = None,
    code_texts: Optional[List[str]] = None,
    table_texts: Optional[List[str]] = None,
    visual_types: Optional[List[str]] = None,
) -> List[Document]:

    count = len(pdf_docs)

    ocr_texts = ocr_texts or [""] * count
    vision_texts = vision_texts or [""] * count
    math_texts = math_texts or [""] * count
    code_texts = code_texts or [""] * count
    table_texts = table_texts or [""] * count
    visual_types = visual_types or [""] * count

    merged_docs = []

    for i, pdf_doc in enumerate(pdf_docs):

        pdf_text = (
            pdf_doc.page_content or ""
        ).strip()

        ocr_text = (
            str(ocr_texts[i]).strip()
            if i < len(ocr_texts)
            and ocr_texts[i] is not None
            else ""
        )

        vision_text = (
            str(vision_texts[i]).strip()
            if i < len(vision_texts)
            and vision_texts[i] is not None
            else ""
        )

        math_text = (
            str(math_texts[i]).strip()
            if i < len(math_texts)
            and math_texts[i] is not None
            else ""
        )

        code_text = (
            str(code_texts[i]).strip()
            if i < len(code_texts)
            and code_texts[i] is not None
            else ""
        )

        table_text = (
            str(table_texts[i]).strip()
            if i < len(table_texts)
            and table_texts[i] is not None
            else ""
        )

        visual_type = (
            str(visual_types[i]).strip()
            if i < len(visual_types)
            and visual_types[i] is not None
            else ""
        )

        # ------------------------------------------------------
        # Choose strongest base text
        # ------------------------------------------------------

        if pdf_text and ocr_text:

            if (
                len(pdf_text) < 50
                and len(ocr_text) > len(pdf_text) * 2
            ):
                base_text = ocr_text
                source_type = "ocr"
            else:
                base_text = pdf_text
                source_type = "pdf"

        elif pdf_text:

            base_text = pdf_text
            source_type = "pdf"

        elif ocr_text:

            base_text = ocr_text
            source_type = "ocr"

        else:

            base_text = ""
            source_type = "empty"

        # ------------------------------------------------------
        # Merge all extracted modalities
        # ------------------------------------------------------

        final_text_parts = []

        if base_text:
            final_text_parts.append(
                base_text
            )

        if vision_text:

            final_text_parts.append(
                "[VISUAL CONTENT DESCRIPTION]\n"
                + vision_text
            )

            source_type += "+vision"

        if math_text:

            final_text_parts.append(
                "[MATHEMATICS]\n"
                + math_text
            )

            source_type += "+math"

        if code_text:

            final_text_parts.append(
                "[CODE]\n"
                + code_text
            )

            source_type += "+code"

        if table_text:

            final_text_parts.append(
                "[TABLE]\n"
                + table_text
            )

            source_type += "+table"

        final_text = "\n\n".join(
            final_text_parts
        ).strip()

        # ------------------------------------------------------
        # Empty-page fallback
        # ------------------------------------------------------

        if not final_text:

            final_text = (
                f"[Page "
                f"{pdf_doc.metadata.get('page', i) + 1}] "
                "[NO EXTRACTABLE TEXT]"
            )

        # ------------------------------------------------------
        # Final document
        # ------------------------------------------------------

        merged_docs.append(
            Document(
                page_content=final_text,
                metadata={
                    **pdf_doc.metadata,

                    "source_type": source_type,

                    "page": pdf_doc.metadata.get(
                        "page",
                        i,
                    ),

                    "visual_type": visual_type,
                },
            )
        )

    return merged_docs