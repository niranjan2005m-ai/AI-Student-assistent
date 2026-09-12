import gc
import logging
import time
from pathlib import Path

from langchain_core.documents import Document

from rag.loader import load_pdf
from rag.splitter import split_documents
from rag.pdf_to_images import pdf_page_to_image # IMPORT UPDATED HERE
from rag.ocr_loader import OCRLoader
from rag.vision_loader import VisionLoader
from rag.math_loader import MathLoader
from rag.code_loader import CodeLoader
from rag.table_loader import TableLoader
from rag.content_detector import ContentDetector
from rag.merge_loader import merge_documents

logger = logging.getLogger(__name__)


def ingest_pdf(
    pdf_path: str | Path,
    use_ocr: bool = True,
) -> list[Document]:

    pdf_path = Path(pdf_path)

    # ==========================================================
    # 1. LOAD PDF TEXT
    # ==========================================================

    start_time = time.time()

    try:
        documents = load_pdf(
            str(pdf_path)
        )

        logger.info(
            f"Load PDF Time: "
            f"{time.time() - start_time:.2f}s"
        )

    except Exception as e:
        logger.exception(
            f"Failed to load PDF {pdf_path}: {e}"
        )
        return []

    if not documents:
        logger.error(
            "PDF loader returned no documents."
        )
        return []

    logger.info(
        f"Total Pages Loaded: {len(documents)}"
    )

    # ==========================================================
    # 2. LOAD MODELS ONCE (LAZY INITIALIZATION)
    # ==========================================================
    # We initialize these as None so they only consume memory
    # if the specific content type is actually found on a page.

    detector = None
    vision = None
    math = None
    code = None
    table = None
    ocr = None

    # ==========================================================
    # 3. PAGE-LEVEL STORAGE
    # ==========================================================

    page_count = len(documents)

    ocr_texts = [""] * page_count
    vision_texts = [""] * page_count
    math_texts = [""] * page_count
    code_texts = [""] * page_count
    table_texts = [""] * page_count
    visual_types = [""] * page_count

    # ==========================================================
    # 4. PROCESS PAGES
    # ==========================================================

    start_time = time.time()

    for i, doc in enumerate(documents):

        page_num = doc.metadata.get(
            "page",
            i,
        )

        pdf_text = (
            doc.page_content or ""
        ).strip()

        img = None

        try:

            # ======================================================
            # FAST PATH: NORMAL TEXT PDF PAGE
            # ======================================================
            if pdf_text:
                logger.info(f"Page {page_num}: using native PDF text")
                continue # Skip the rest of the loop, no AI needed!

            # ======================================================
            # SLOW PATH: SCANNED / IMAGE PAGE
            # ======================================================
            # Only render the image if there is no native text
            try:
                img = pdf_page_to_image(str(pdf_path), page_num)
            except Exception as e:
                logger.warning(f"Failed to render image for page {page_num}: {e}")
                img = None

            if img is None:
                logger.warning(f"Page {page_num}: no text and no image")
                continue

            # ==================================================
            # CONTENT DETECTION
            # ==================================================

            try:
                if detector is None:
                    detector = ContentDetector()

                labels = detector.detect(img)
                logger.info(
                    f"Page {page_num} Labels: {labels}"
                )
                
                if "CHART" in labels:
                        visual_types[i] = "chart"
                elif "FLOWCHART" in labels:
                        visual_types[i] = "flowchart"
                elif "DIAGRAM" in labels:
                        visual_types[i] = "diagram"

                elif "TABLE" in labels:
                        visual_types[i] = "table"

                elif "FORMULA" in labels:
                        visual_types[i] = "formula"

                elif "CODE" in labels:
                        visual_types[i] = "code"

                else:
                        visual_types[i] = "text"
                        
            except Exception as e:
                logger.error(
                    f"Content detection failed "
                    f"for Page {page_num}: {e}"
                )
                labels = ["TEXT"] # Safe fallback

            # ==================================================
            # VISION
            # ==================================================

            if any(
                label in labels
                for label in (
                    "CHART",
                    "DIAGRAM",
                    "FLOWCHART",
                )
            ):
                try:
                    if vision is None:
                        vision = VisionLoader()
                    vision_texts[i] = (
                        vision.describe_image(img) or ""
                    )
                except Exception as e:
                    logger.error(
                        f"Vision processing failed "
                        f"on Page {page_num}: {e}"
                    )

            # ==================================================
            # FORMULA
            # ==================================================

            if "FORMULA" in labels:
                try:
                    if math is None:
                        math = MathLoader()
                    math_texts[i] = (
                        math.extract(img) or ""
                    )
                except Exception as e:
                    logger.error(
                        f"Math processing failed "
                        f"on Page {page_num}: {e}"
                    )

            # ==================================================
            # CODE
            # ==================================================

            if "CODE" in labels:
                try:
                    if code is None:
                        code = CodeLoader()
                    code_texts[i] = (
                        code.extract(img) or ""
                    )
                except Exception as e:
                    logger.error(
                        f"Code extraction failed "
                        f"on Page {page_num}: {e}"
                    )

            # ==================================================
            # TABLE
            # ==================================================

            if "TABLE" in labels:
                try:
                    if table is None:
                        table = TableLoader()
                    table_texts[i] = (
                        table.extract(img) or ""
                    )
                except Exception as e:
                    logger.error(
                        f"Table extraction failed "
                        f"on Page {page_num}: {e}"
                    )

            # ==================================================
            # OCR
            # ==================================================

            if (
                not pdf_text
                and use_ocr
            ):
                try:
                    if ocr is None:
                        ocr = OCRLoader()
                    
                    extracted = ocr.extract_text([img])

                    # Handle both string returns and list returns safely
                    if isinstance(extracted, list) and extracted:
                        ocr_texts[i] = str(extracted[0] or "")
                    elif isinstance(extracted, str):
                        ocr_texts[i] = extracted
                    else:
                        ocr_texts[i] = ""

                    logger.info(
                        f"OCR text extracted "
                        f"for Page {page_num}"
                    )

                except Exception as e:
                    logger.error(
                        f"OCR failed on "
                        f"Page {page_num}: {e}"
                    )

        except Exception as e:
            logger.exception(
                f"Unexpected processing error "
                f"on Page {page_num}: {e}"
            )

        finally:
            # Release current page image
            if img is not None:
                try:
                    img.close()
                except Exception:
                    pass

            del img
            gc.collect()


    logger.info(
        f"AI Routing & Processing Time: "
        f"{time.time() - start_time:.2f}s"
    )

    # ==========================================================
    # 5. MERGE ALL MODALITIES
    # ==========================================================

    page_indices = list(
        range(len(documents))
    )

    try:
        documents = merge_documents(
            documents,
            page_indices,
            ocr_texts,
            vision_texts,
            math_texts,
            code_texts,
            table_texts,
            visual_types,
        )

    except Exception as e:
        logger.exception(
            f"Document merge failed: {e}"
        )
        return []

    # ==========================================================
    # 6. SPLIT INTO CHUNKS
    # ==========================================================

    try:
        start_time = time.time()

        chunks = split_documents(
            documents
        )

        logger.info(
            f"Split Time: "
            f"{time.time() - start_time:.2f}s"
        )

    except Exception as e:
        logger.exception(
            f"Document splitting failed: {e}"
        )
        return []

    # ==========================================================
    # 7. CLEANUP
    # ==========================================================

    del documents
    del ocr_texts
    del vision_texts
    del math_texts
    del code_texts
    del table_texts

    gc.collect()

    # ==========================================================
    # 8. FINAL VALIDATION
    # ==========================================================

    if not chunks:
        logger.error(
            "No chunks were created. "
            "The PDF may contain no extractable text."
        )
        return []

    logger.info(
        f"Successfully created "
        f"{len(chunks)} chunks."
    )

    return chunks