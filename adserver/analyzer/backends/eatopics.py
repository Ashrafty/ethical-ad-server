"""Spacy-based topic classifier that uses our trained model and gives a likelihood that text is about our topics."""
from .textacynlp import TextacyAnalyzerBackend


class EthicalAdsTopicsBackend(TextacyAnalyzerBackend):

    """A model that uses our own custom dataset behind the scenes."""

    # Name of the model package
    # A Python package of this name will be imported and IOError thrown if not present
    MODEL_NAME = "en_ethicalads_topics"

    # Below this body/text length, the model is unreliable
    # Return blank results lower than this length (~100 words)
    MIN_TEXT_LENGTH = 500

    # Threshold on the model
    MODEL_THRESHOLD = 0.4

    def analyze_text(self, text):
        """Analyze text and return major topics (topics we are interested in) that the text is about."""
        if len(text) < self.MIN_TEXT_LENGTH:
            return []

        output = self.pretrained_model(text)
        return [k for k, v in output.cats.items() if v > self.MODEL_THRESHOLD]
