import os
from typing import List
from sentence_transformers import SentenceTransformer
from app.config.settings import settings

class EmbeddingService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._model = None
        return cls._instance

    def _load_model(self):
        if self._model is None:
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            self._model = SentenceTransformer(settings.embedding_model)

    def _prepare_text(self, text: str) -> str:
        if "bge" in settings.embedding_model.lower():
            return f"Represent this sentence for searching relevant passages: {text}"
        return text

    def encode(self, text: str) -> List[float]:
        self._load_model()
        prepared_text = self._prepare_text(text)
        return self._model.encode(prepared_text, convert_to_numpy=True).tolist()

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        prepared_texts = [self._prepare_text(t) for t in texts]
        return self._model.encode(prepared_texts, convert_to_numpy=True).tolist()

embedding_service = EmbeddingService()
