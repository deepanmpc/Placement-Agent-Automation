from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config.settings import settings
from app.vector_store.qdrant_client import vector_store
from app.api.fitment import router as fitment_router
from app.api.indexing import router as indexing_router

# Optionally import services here to trigger lazy loading if desired
# from app.services.embedding_service import embedding_service
# from app.services.reranking_service import reranking_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Placement RAG Service...")
    # Ensure Qdrant collections exist
    try:
        vector_store.ensure_collections()
        logger.info("Qdrant collections ready.")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant collections: {e}")
        
    yield
    logger.info("Shutting down Placement RAG Service.")

app = FastAPI(
    title="Placement RAG Service",
    description="Semantic Fitment Engine for JD-Student Matching",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fitment_router)
app.include_router(indexing_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
