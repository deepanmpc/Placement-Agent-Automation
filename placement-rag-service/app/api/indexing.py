from fastapi import APIRouter, HTTPException
from app.models.fitment_models import IndexStudentRequest, IndexResponse, IndexAllResponse
from app.workers.profile_indexer import profile_indexer

router = APIRouter(prefix="", tags=["indexing"])

@router.post("/index-student", response_model=IndexResponse)
async def index_student(req: IndexStudentRequest):
    try:
        return await profile_indexer.index_student(req.student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reindex-student", response_model=IndexResponse)
async def reindex_student(req: IndexStudentRequest):
    try:
        return await profile_indexer.reindex_student(req.student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index-all", response_model=IndexAllResponse)
async def index_all():
    try:
        return await profile_indexer.index_all_students()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
