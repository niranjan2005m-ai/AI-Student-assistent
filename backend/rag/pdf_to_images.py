import fitz
import logging
from PIL import Image
from typing import Iterator, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def pdf_to_images(
    pdf_path: str | Path,
    pages: Optional[List[int]] = None,
    zoom: int = 2,
) -> Iterator[tuple[int, Image.Image | None]]:

    matrix = fitz.Matrix(zoom, zoom)

    try:
        with fitz.open(str(pdf_path)) as doc:

            if pages is None:
                pages = range(len(doc))

            for page_num in pages:

                try:
                    page = doc.load_page(page_num)

                    pix = page.get_pixmap(
                        matrix=matrix,
                    )

                    image = Image.frombytes(
                        "RGB",
                        [pix.width, pix.height],
                        pix.samples,
                    )

                    yield page_num, image

                except Exception as page_e:

                    logger.error(
                        f"Failed to process page "
                        f"{page_num}: {page_e}"
                    )

                    # Preserve page position
                    yield page_num, None

    except Exception as doc_e:

        logger.error(
            f"Failed to open PDF "
            f"{pdf_path}: {doc_e}"
        )


def pdf_page_to_image(
    pdf_path: str | Path,
    page_num: int,
    zoom: int = 2,
) -> Optional[Image.Image]:
    """
    Extracts a single page from a PDF and returns it as a PIL Image.
    Used for on-demand lazy loading of pages that lack native text.
    """
    matrix = fitz.Matrix(zoom, zoom)
    
    try:
        with fitz.open(str(pdf_path)) as doc:
            page = doc.load_page(page_num)
            
            pix = page.get_pixmap(
                matrix=matrix,
            )
            
            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples,
            )
            
            return image
            
    except Exception as e:
        logger.error(
            f"Failed to extract image for page {page_num} "
            f"from {pdf_path}: {e}"
        )
        return None