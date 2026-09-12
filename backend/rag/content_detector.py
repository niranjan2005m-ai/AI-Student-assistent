from rag.gemini_client import get_gemini_model


class ContentDetector:

    def __init__(self):
        self.model = get_gemini_model()

    def detect(self, image) -> list[str]:

        prompt = """
Classify this document page.

Return ONLY labels separated by commas.

Allowed labels:
TEXT
TABLE
CHART
DIAGRAM
FLOWCHART
FORMULA
CODE

Rules:
- TEXT = normal written content
- TABLE = table
- CHART = graph, plot, bar chart, pie chart, etc.
- DIAGRAM = diagram or architecture figure
- FLOWCHART = process flowchart
- FORMULA = mathematical equations
- CODE = programming code

Multiple labels are allowed.

Examples:
TEXT
TEXT, TABLE
TEXT, DIAGRAM
TEXT, CODE
"""

        try:
            response = self.model.generate_content(
                [prompt, image]
            )

            if not response.text:
                return ["TEXT"]

            labels = [
                label.strip().upper()
                for label in response.text.split(",")
                if label.strip()
            ]

            valid_labels = {
                "TEXT",
                "TABLE",
                "CHART",
                "DIAGRAM",
                "FLOWCHART",
                "FORMULA",
                "CODE",
            }

            labels = [
                label
                for label in labels
                if label in valid_labels
            ]

            return labels or ["TEXT"]

        except Exception as exc:
            print(
                f"Content detection failed: {exc}"
            )
            return ["TEXT"]