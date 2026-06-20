from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "mysql+aiomysql://root:15713007@127.0.0.1:3306/placement_agent"
    
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    reranker_model: str = "BAAI/bge-reranker-base"
    embedding_dim: int = 384
    
    collection_prefix: str = "rag_"
    top_k_retrieval: int = 10
    top_k_rerank: int = 5
    
    host: str = "0.0.0.0"
    port: int = 8001
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="RAG_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()

def get_settings():
    return settings
