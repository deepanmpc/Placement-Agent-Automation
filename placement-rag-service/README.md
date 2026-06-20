# Placement RAG Service

Semantic Fitment Microservice for Placement-Agent-Automation. Matches Job Descriptions (JD) against Student Profiles using Vector Search (Qdrant) and Reranking.

## Architecture
- **Embeddings:** `BAAI/bge-small-en-v1.5`
- **Reranker:** `BAAI/bge-reranker-base` 
- **Vector DB:** Qdrant (4 collections: skills, projects, experience, achievements)
- **API:** FastAPI

## Setup

1. **Install dependencies:**
   `pip install -r requirements.txt`

2. **Environment Variables:**
   Copy `.env.example` to `.env` and fill in DB credentials.

3. **Start Qdrant (Docker):**
   `docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant`

4. **Run Server:**
   `uvicorn main:app --host 0.0.0.0 --port 8001 --reload`

## API Endpoints

- `POST /index-student` - Index a specific student
- `POST /reindex-student` - Reindex a student
- `POST /index-all` - Index all students
- `POST /match-jd` - Get scored candidates for a JD

## Scoring Formula
- 40% Skills
- 30% Projects
- 20% Experience (GitHub Repos)
- 10% Achievements (Competitive Coding)
