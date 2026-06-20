from typing import Dict, List
import numpy as np
from sentence_transformers import CrossEncoder
from app.config.settings import settings
from app.models.fitment_models import RetrievedChunk

class RerankingService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RerankingService, cls).__new__(cls)
            cls._instance._model = None
        return cls._instance

    def _load_model(self):
        if self._model is None:
            self._model = CrossEncoder(settings.reranker_model)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def rerank(self, job_description: str, retrieved: Dict[str, List[RetrievedChunk]], top_k: int = 5) -> Dict[str, List[RetrievedChunk]]:
        self._load_model()
        reranked = {}
        
        for section, chunks in retrieved.items():
            if not chunks:
                reranked[section] = []
                continue
                
            pairs = [[job_description, chunk.content] for chunk in chunks]
            scores = self._model.predict(pairs)
            
            # Apply sigmoid to raw logits to get 0-1 range
            normalized_scores = [float(self._sigmoid(s)) for s in scores]
            
            for chunk, score in zip(chunks, normalized_scores):
                chunk.score = score
                
            # Sort descending and take top_k
            sorted_chunks = sorted(chunks, key=lambda x: x.score, reverse=True)[:top_k]
            reranked[section] = sorted_chunks
            
        return reranked

reranking_service = RerankingService()
