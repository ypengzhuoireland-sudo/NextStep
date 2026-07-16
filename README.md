# NextStep AI Tutor

NextStep is an adaptive Python programming tutor. It combines authenticated practice, diagnostic assessment, code execution, Bayesian Knowledge Tracing (BKT), exercise recommendation, progressive hints, AI-assisted guidance, and student and teacher dashboards.

## Features

- Student registration, login, logout, and account deletion.
- Teacher login and class-level learning analytics.
- Diagnostic assessment that initializes a student's learning path.
- Monaco-based Python practice workspace with run and submit workflows.
- Exercise-specific test harnesses executed through Judge0.
- KC-level mastery tracking using Bayesian Knowledge Tracing.
- Adaptive next-exercise recommendations based on mastery.
- Three-level progressive hints and a study assistant with deterministic fallbacks.
- Student learning advice, learning paths, and mastery visualizations.

## Architecture

```text
frontend/                 React, TypeScript, Vite, Tailwind CSS, Monaco
backend/                  FastAPI, SQLAlchemy, PostgreSQL
backend/app/services/     Learning, execution, BKT, recommendation, AI logic
backend/seeds/            Demo users, diagnostic questions, and exercise bank
docs/                     API contract and frontend/backend design documents
```

The frontend communicates with the backend through `/api`. Practice, execution, submission, hint, and recommendation endpoints require a valid student Bearer token. The backend always derives the student identity from that token.

## Prerequisites

- Node.js 18 or newer.
- Python 3.11 or newer.
- PostgreSQL.
- A Judge0 API key for real code execution and submissions.
- An OpenAI API key for AI-generated hints and recommendation explanations. The core learning flow falls back to deterministic responses when it is unavailable.

## Quick Start

### 1. Start PostgreSQL

Create a PostgreSQL database named `nextstep`, or update `DATABASE_URL` in `backend/.env` to point to an existing database.

### 2. Start the Backend

```bash
cd backend
cp .env.example .env

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

python3 scripts/init_db.py
python3 -m uvicorn app.main:app --reload
```

The backend is available at `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

Set `JUDGE0_API_KEY` in `backend/.env` before testing code execution or submission. Set `OPENAI_API_KEY` to enable AI-backed assistance.

### 3. Start the Frontend

Open a second terminal:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://127.0.0.1:5173` in a browser.

For full frontend-backend integration, keep the following values in `frontend/.env` and restart Vite after editing the file:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
VITE_USE_MOCK=false
```

## Demo Accounts

The database initialization script creates the following demo accounts:

| Role | Email | Password |
| --- | --- | --- |
| Student | `student@nextstep.test` | `demo1234` |
| Teacher | `teacher@nextstep.test` | `demo1234` |

## Testing

Run backend tests from the backend directory:

```bash
cd backend
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Build the frontend from the frontend directory:

```bash
cd frontend
npm run build
```

## Documentation

- [API Contract](docs/API.md)
- [Frontend Design](docs/FRONTEND_DESIGN.md)
- [Backend Design](docs/BACKEND_DESIGN.md)

## Development Notes

- The backend loads settings from `backend/.env`; do not commit secrets.
- `VITE_USE_MOCK=false` is required for most practice-domain requests to reach the backend.
- Code execution is synchronous and depends on the configured Judge0 service.
- Access-token revocation is currently stored in process memory and is not shared across backend instances.
