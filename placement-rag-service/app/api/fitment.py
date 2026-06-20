import time
from fastapi import APIRouter, HTTPException
from app.models.fitment_models import MatchJDRequest, MatchJDResponse, StudentFitmentResult
from app.services.retrieval_service import retrieval_service
from app.services.reranking_service import reranking_service
from app.services.scoring_service import scoring_service
from app.services.explanation_service import explanation_service
from app.services.jd_parsing_service import jd_parsing_service

router = APIRouter(prefix="", tags=["fitment"])

@router.get("/health")
async def health():
    return {"status": "ok", "service": "placement-rag-service"}

@router.post("/match-jd", response_model=MatchJDResponse)
async def match_jd(req: MatchJDRequest):
    start_time = time.time()
    try:
        # Parse JD
        parsed_jd_data = jd_parsing_service.parse_jd(req.job_description)
        from app.models.fitment_models import ParsedJD
        parsed_jd = ParsedJD(**parsed_jd_data)

        # Retrieve candidates
        retrieved = retrieval_service.retrieve(req, parsed_jd)
        
        # Rerank candidates
        from app.config.settings import settings
        reranked = reranking_service.rerank(req.job_description, retrieved, top_k=settings.top_k_rerank)
        
        # Calculate scores
        student_scores = scoring_service.calculate_scores(req, parsed_jd, reranked)
        
        # Build results
        results = []
        for student_id, data in student_scores.items():
            explanations = explanation_service.generate_explanations(data)
            
            results.append(StudentFitmentResult(
                student_id=student_id,
                semantic_score=data["semantic_score"],
                skill_score=data["skill_score"],
                project_score=data["project_score"],
                experience_score=data["experience_score"],
                achievement_score=data["achievement_score"],
                explanation=explanations,
                evidence=data["evidence"]
            ))
            
        # Sort by semantic_score descending
        results.sort(key=lambda x: x.semantic_score, reverse=True)
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return MatchJDResponse(
            results=results,
            total_students_evaluated=len(results),
            processing_time_ms=processing_time_ms
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/candidate-match-details/{student_id}")
async def candidate_match_details(student_id: str, req: MatchJDRequest):
    try:
        # We only want to evaluate ONE student. We can do this by retrieving only chunks for this student.
        # But our vector store search is global. We could retrieve all chunks for this student directly
        # from Qdrant, rerank them, and score them.
        from app.vector_store.qdrant_client import vector_store
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        parsed_jd_data = jd_parsing_service.parse_jd(req.job_description)
        from app.models.fitment_models import ParsedJD
        parsed_jd = ParsedJD(**parsed_jd_data)

        # Retrieve chunks directly for this student
        retrieved = {}
        for section in ["skills", "projects", "experience", "achievements"]:
            col_name = f"rag_{section}"
            try:
                res = vector_store.client.scroll(
                    collection_name=col_name,
                    scroll_filter=Filter(must=[FieldCondition(key="student_id", match=MatchValue(value=student_id))]),
                    limit=50,
                    with_payload=True
                )[0]
                from app.models.fitment_models import RetrievedChunk
                chunks = []
                for point in res:
                    chunks.append(RetrievedChunk(
                        student_id=point.payload["student_id"],
                        section=point.payload["section"],
                        content=point.payload["content"],
                        score=0.0
                    ))
                retrieved[section] = chunks
            except Exception:
                retrieved[section] = []
                
        from app.config.settings import settings
        reranked = reranking_service.rerank(req.job_description, retrieved, top_k=settings.top_k_rerank)
        
        student_scores = scoring_service.calculate_scores(req, parsed_jd, reranked)
        if student_id not in student_scores:
            raise HTTPException(status_code=404, detail="Student not found or no indexed chunks.")
            
        data = student_scores[student_id]
        
        return {
            "semantic_score": data["semantic_score"],
            "skill_score": data["skill_score"],
            "project_score": data["project_score"],
            "experience_score": data["experience_score"],
            "achievement_score": data["achievement_score"],
            "explanation": explanation_service.generate_explanations(data),
            "evidence": [e.model_dump() for e in data["evidence"]]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
