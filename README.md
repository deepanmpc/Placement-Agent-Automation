# Placement Agent Automation

A robust placement dashboard and extraction system that aggregates student profiles across various coding platforms like GitHub, LeetCode, Codeforces, and CodeChef.

## ⚠️ Important Prerequisites

To use the extraction and syncing features of this application, you **MUST** provide a GitHub Personal Access Token. Without it, GitHub's API limits unauthenticated requests to 60 per hour, which will cause extractions to fail and take up to 20 seconds per student due to rate-limit retries.

### How to set up your environment

1. Create a Personal Access Token on your GitHub account (no specific scopes are required, just public access is fine).
2. Create a file named `.env` in the root directory of this project.
3. Add your token to the file like this:
   ```env
   PA_GITHUB_API_TOKEN=ghp_your_token_here
   ```

## Getting Started

### 1. Database & Services
Ensure your PostgreSQL/MySQL database and Qdrant instances are running.

### 2. Backend
Navigate to the root directory and start the Uvicorn server:
```bash
PYTHONPATH=. .venv/bin/python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

### 3. Frontend
Navigate to the `frontend` folder, install dependencies, and start the React application:
```bash
cd frontend
npm install
npm start
```