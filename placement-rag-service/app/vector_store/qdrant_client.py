import uuid
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from loguru import logger

from app.config.settings import settings
from app.models.fitment_models import DocumentChunk, RetrievedChunk

class QdrantVectorStore:
    def __init__(self):
        self.client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        self.collections = [
            f"{settings.collection_prefix}skills",
            f"{settings.collection_prefix}projects",
            f"{settings.collection_prefix}experience",
            f"{settings.collection_prefix}achievements"
        ]

    def ensure_collections(self):
        existing = [c.name for c in self.client.get_collections().collections]
        for col_name in self.collections:
            if col_name not in existing:
                self.client.create_collection(
                    collection_name=col_name,
                    vectors_config=VectorParams(size=settings.embedding_dim, distance=Distance.COSINE)
                )
                logger.info(f"Created Qdrant collection: {col_name}")

    def get_collection_names(self) -> List[str]:
        return self.collections

    def upsert_chunks(self, section: str, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        if not chunks:
            return
            
        col_name = f"{settings.collection_prefix}{section}"
        points = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{chunk.student_id}:{section}:{i}"))
            points.append(PointStruct(
                id=point_id,
                vector=emb,
                payload={
                    "student_id": chunk.student_id,
                    "section": chunk.section,
                    "batch": chunk.batch,
                    "branch": chunk.branch,
                    "eligible": chunk.eligible,
                    "content": chunk.content
                }
            ))
        self.client.upsert(collection_name=col_name, points=points)

    def search(self, section: str, query_vector: List[float], top_k: int = 10, batch_filter: Optional[int] = None, branch_filter: Optional[str] = None, eligible_filter: Optional[bool] = None) -> List[RetrievedChunk]:
        col_name = f"{settings.collection_prefix}{section}"
        
        must_conditions = []
        if batch_filter is not None:
            must_conditions.append(FieldCondition(key="batch", match=MatchValue(value=batch_filter)))
        if branch_filter is not None:
            must_conditions.append(FieldCondition(key="branch", match=MatchValue(value=branch_filter)))
        if eligible_filter is not None:
            must_conditions.append(FieldCondition(key="eligible", match=MatchValue(value=eligible_filter)))
            
        query_filter = Filter(must=must_conditions) if must_conditions else None

        results = self.client.search(
            collection_name=col_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True
        )

        retrieved = []
        for res in results:
            retrieved.append(RetrievedChunk(
                student_id=res.payload["student_id"],
                section=res.payload["section"],
                content=res.payload["content"],
                score=res.score,
                batch=res.payload.get("batch"),
                branch=res.payload.get("branch"),
                eligible=res.payload.get("eligible")
            ))
        return retrieved

    def delete_student(self, student_id: str):
        for col_name in self.collections:
            try:
                self.client.delete(
                    collection_name=col_name,
                    points_selector=Filter(
                        must=[FieldCondition(key="student_id", match=MatchValue(value=student_id))]
                    )
                )
            except Exception as e:
                logger.error(f"Error deleting {student_id} from {col_name}: {e}")

vector_store = QdrantVectorStore()
