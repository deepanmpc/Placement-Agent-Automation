import os
from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._model = None
        return cls._instance

    def _load_model(self):
        if self._model is None:
            # Disable tokenizers parallelism warning
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            import logging
            logger = logging.getLogger(__name__)
            logger.info("Loading sentence-transformers/all-MiniLM-L6-v2 embedding model...")
            self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Embedding model loaded.")

    def get_embedding(self, text: str) -> List[float]:
        self._load_model()
        # returns a float list
        return self._model.encode(text, convert_to_tensor=False).tolist()

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        return self._model.encode(texts, convert_to_tensor=False).tolist()

# Singleton instance
embedding_service = EmbeddingService()
