from paddleocr import PaddleOCR
import numpy as np

# Load PaddleOCR only once
_ocr_instance = None


def get_ocr():
    global _ocr_instance

    if _ocr_instance is None:
        print("Loading PaddleOCR Model (This only happens once!)...")

        _ocr_instance = PaddleOCR(
            use_angle_cls=True,
            lang="en",
        )

    return _ocr_instance


class OCRLoader:

    def __init__(self):
        self.ocr = get_ocr()

    def extract_text(self, images):
        page_texts = []

        for image in images:

            try:
                # Convert PIL image to NumPy array
                image_np = np.asarray(image)

                result = self.ocr.ocr(
                    image_np,
                    cls=True,
                )

                page = []

                if result:
                    # PaddleOCR normally returns one result
                    # per input image.
                    lines = result[0] if result[0] else []

                    for line in lines:

                        try:
                            # Expected structure:
                            # [box, [text, confidence]]
                            if (
                                isinstance(line, (list, tuple))
                                and len(line) >= 2
                            ):
                                recognition = line[1]

                                if (
                                    isinstance(
                                        recognition,
                                        (list, tuple),
                                    )
                                    and len(recognition) >= 1
                                ):
                                    text = recognition[0]

                                    # Always convert to string
                                    if text is not None:
                                        text = str(text).strip()

                                        if text:
                                            page.append(text)

                        except Exception as line_error:
                            print(
                                f"OCR line skipped: {line_error}"
                            )
                            continue

                page_texts.append(
                    "\n".join(page)
                )

            except Exception as page_error:
                print(
                    f"OCR page failed: {page_error}"
                )

                # Keep the page aligned with its index
                page_texts.append("")

            finally:
                # Release image resources
                try:
                    image.close()
                except Exception:
                    pass

                # Release NumPy reference
                try:
                    del image_np
                except Exception:
                    pass

        return page_texts