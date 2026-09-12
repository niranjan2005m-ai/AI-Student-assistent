from rag.pdf_to_images import pdf_to_images
from rag.ocr_loader import OCRLoader

pdf = "data/Document 20.docx.pdf"

images = pdf_to_images(pdf)

print(f"Loaded {len(images)} pages")

ocr = OCRLoader()

texts = ocr.extract_text(images)

print("\n===== OCR Output =====\n")
print(texts[0])