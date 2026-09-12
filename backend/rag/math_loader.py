from pix2text import Pix2Text

_model = None


def get_math_model():
    global _model

    if _model is None:
        print("Loading Pix2Text...")
        _model = Pix2Text()

    return _model


class MathLoader:

    def __init__(self):
        self.model = get_math_model()

    def extract(self, image):
        """
        Extract mathematical equations from an image.
        Returns plain text / LaTeX depending on Pix2Text output.
        """

        try:
            result = self.model.recognize(image)

            if result:
                return str(result)

            return ""

        except Exception as e:
            print(f"Math extraction failed: {e}")
            return ""