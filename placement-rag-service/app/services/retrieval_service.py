from typing import Dict, List, Optional
from app.config.settings import settings
from app.services.embedding_service import embedding_service
from app.models.fitment_models import RetrievedChunk, MatchJDRequest, ParsedJD
from app.services.skill_normalization_service import skill_normalization_service
from app.vector_store.qdrant_client import vector_store

class RetrievalService:
    def retrieve(self, req: MatchJDRequest, parsed_jd: ParsedJD) -> Dict[str, List[RetrievedChunk]]:
        # Enrich job description with canonical skills for better vector search
        all_skills = parsed_jd.required_skills + parsed_jd.preferred_skills
        canonical_skills = skill_normalization_service.get_canonical_skills(all_skills)
        enriched_query = f"{req.job_description}\nKey Skills: {', '.join(canonical_skills)}"

        jd_vector = embedding_service.encode(enriched_query)
        sections = ["skills", "projects", "experience", "achievements"]
        retrieved = {}
        
        # Searching sequentially since QdrantClient is sync
        for section in sections:
            results = vector_store.search(
                section=section,
                query_vector=jd_vector,
                top_k=settings.top_k_retrieval,
                batch_filter=req.batch_filter,
                branch_filter=req.branch_filter,
                eligible_filter=req.eligible_filter
            )
            retrieved[section] = results
            
        return retrieved

retrieval_service = RetrievalService()
