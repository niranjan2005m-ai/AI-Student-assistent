from rag.gemini_client import get_gemini_model


class TableLoader:

    def __init__(self):
        self.model = get_gemini_model()

    def extract(self, image):

        prompt = """
You are extracting a table from an image.

Instructions:

1. Preserve rows.
2. Preserve columns.
3. Keep headers.
4. Return the table as plain text.
5. Do not explain.
6. Do not summarize.

Example:

Name | Marks | Grade
John | 92    | A
Alice| 88    | B

Return ONLY the table.
"""

        try:

            response = self.model.generate_content(
                [prompt, image]
            )

            if response.text:
                return response.text.strip()

            return ""

        except Exception as e:
            print(f"Table extraction failed: {e}")
            return ""