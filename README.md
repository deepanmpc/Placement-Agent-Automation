# Placement Agent Automation

A comprehensive placement dashboard that aggregates student profiles from popular coding platforms such as GitHub, LeetCode, Codeforces, and CodeChef. The system provides profile extraction, scoring, and a UI for viewing candidate details.

## Prerequisites

- **GitHub Personal Access Token** – Required for extracting data from GitHub. Create a token with no special scopes (public access is sufficient).
- **Environment file** – Add a `.env` file at the project root containing:
  ```
  PA_GITHUB_API_TOKEN=ghp_your_token_here
  ```
- **Database** – PostgreSQL or MySQL instance must be running.
- **Qdrant** – Vector database instance for similarity search.

## Getting Started

### Backend
```bash
# Install dependencies (assumes Python virtualenv is set up)
pip install -r requirements.txt
# Run the API server
PYTHONPATH=. .venv/bin/python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start
```
The frontend will be available at `http://localhost:3000`.

## Project Structure
- `backend/`
  - `api/` – FastAPI endpoints.
  - `database/` – SQLAlchemy models and connection utilities.
  - `ingestion/` – Collectors for GitHub, LeetCode, Codeforces, CodeChef.
  - `ranking/` – Scoring logic.
- `frontend/`
  - React application built with Vite.
- `placement-rag-service/` – Retrieval‑augmented generation service (currently without tests).

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Ensure code follows existing style and passes linting.
4. Submit a pull request.

## License

This project is licensed under the MIT License.