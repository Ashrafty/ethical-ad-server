import logging
import os

from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from textacy import preprocessing

from ...models import Topic
from .base import BaseAnalyzerBackend

log = logging.getLogger(__name__)  # noqa


class SentenceTransformerAnalyzerBackend(BaseAnalyzerBackend):
    """
    Quick and dirty analyzer that uses the SentenceTransformer library
    """

    MODEL_NAME = "multi-qa-MiniLM-L6-cos-v1"
    MODEL_HOME = os.getenv("SENTENCE_TRANSFORMERS_HOME", "/tmp/sentence_transformers")

    def preprocess_text(self, text):
        self.preprocessor = preprocessing.make_pipeline(
            preprocessing.normalize.unicode,
            preprocessing.remove.punctuation,
            preprocessing.normalize.whitespace,
        )
        return self.preprocessor(text).lower()[: self.MAX_INPUT_LENGTH]

    def analyze_response(self, resp):
        return []

    def embed_response(self, resp) -> list:
        """Analyze an HTTP response and return a list of keywords/topics for the URL."""
        model = SentenceTransformer(self.MODEL_NAME, cache_folder=self.MODEL_HOME)
        text = self.get_content(resp)
        if text:
            log.info("Embedding text: %s", text[:100])
            embedding = model.encode(text)
            return embedding.tolist()

        return None
