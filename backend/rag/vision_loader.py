from rag.gemini_client import get_gemini_model

class VisionLoader:
    def __init__(self):
        self.model = get_gemini_model()

    def describe_image(self, image) -> str:
        """
        Returns a detailed description of charts, graphs, diagrams, flowcharts, and figures.
        """
        prompt = """
You are analyzing an educational document.

Describe ONLY the visual information.

If it is a chart:
- Explain chart type.
- Mention axes.
- Mention values if visible.
- Mention trends.
- Mention important conclusions.

If it is a diagram:
- Explain all components.
- Explain relationships.
- Explain arrows and flow.

If it is a flowchart:
- Explain every step in order.

If it is an architecture diagram:
- Explain every component.
- Explain data flow.

Return clean text only.
"""
        response = self.model.generate_content([prompt, image])

        if response.text:
            return response.text.strip()

        return ""