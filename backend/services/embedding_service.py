from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingService:
    """
    Singleton service for the text embedding model.
    Loads 'sentence-transformers/all-MiniLM-L6-v2' once into memory.
    """
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            # Initialize model only once
            print("Loading sentence-transformers/all-MiniLM-L6-v2...")
            cls._model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        return cls._instance

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Computes the embedding for a given text.
        """
        return self._model.encode(text)

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Computes cosine similarity between two texts.
        """
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        
        # Calculate cosine similarity
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(dot_product / (norm1 * norm2))

# Global singleton instance
embedding_service = EmbeddingService()
