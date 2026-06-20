from loguru import logger
from app.db.reader import get_profile, get_all_profile_uuids
from app.services.chunking_service import chunking_service
from app.services.embedding_service import embedding_service
from app.vector_store.qdrant_client import vector_store
from app.models.fitment_models import IndexResponse, IndexAllResponse

class ProfileIndexer:
    async def index_student(self, student_id: str) -> IndexResponse:
        profile_data = await get_profile(student_id)
        if not profile_data:
            raise ValueError(f"Student profile not found for UUID: {student_id}")
            
        chunks = chunking_service.chunk_profile(profile_data)
        if not chunks:
            return IndexResponse(student_id=student_id, chunks_indexed=0, status="No valid chunks found")
            
        # Group by section
        sections = {"skills": [], "projects": [], "experience": [], "achievements": []}
        for chunk in chunks:
            if chunk.section in sections:
                sections[chunk.section].append(chunk)
                
        total_indexed = 0
        for section, section_chunks in sections.items():
            if section_chunks:
                texts = [c.content for c in section_chunks]
                embeddings = embedding_service.encode_batch(texts)
                vector_store.upsert_chunks(section, section_chunks, embeddings)
                total_indexed += len(section_chunks)
                
        return IndexResponse(student_id=student_id, chunks_indexed=total_indexed, status="success")

    async def reindex_student(self, student_id: str) -> IndexResponse:
        vector_store.delete_student(student_id)
        return await self.index_student(student_id)

    async def index_all_students(self) -> IndexAllResponse:
        uuids = await get_all_profile_uuids()
        total_chunks = 0
        errors = []
        
        for uuid in uuids:
            try:
                res = await self.index_student(uuid)
                total_chunks += res.chunks_indexed
                logger.info(f"Indexed student {uuid}: {res.chunks_indexed} chunks")
            except Exception as e:
                logger.error(f"Failed to index student {uuid}: {e}")
                errors.append(f"{uuid}: {str(e)}")
                
        return IndexAllResponse(
            total_students=len(uuids),
            total_chunks=total_chunks,
            status="completed" if not errors else "completed_with_errors",
            errors=errors
        )

profile_indexer = ProfileIndexer()
