from rag.gemini_client import get_gemini_model


class CodeLoader:

    def __init__(self):
        self.model = get_gemini_model()

    def extract(self, image):

        prompt = """
You are extracting source code from an image.

Instructions:

- Extract the code exactly.
- Preserve indentation.
- Preserve line breaks.
- Preserve symbols.
- Do not explain.
- Do not add markdown.
- Return only the code.
"""

        try:

            response = self.model.generate_content(
                [prompt, image]
            )

            if response.text:
                return response.text.strip()

            return ""

        except Exception as e:
            print(f"Code extraction failed: {e}")
            return ""