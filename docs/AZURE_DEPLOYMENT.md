# Azure Deployment Guide

This project deploys cleanly as three Azure resources:

- Frontend: Azure Static Web Apps
- Backend: Azure App Service for Linux, Python 3.11 or 3.12
- Database: Azure Database for PostgreSQL Flexible Server

## Secret Safety

Never commit real `.env` files. This repository should only contain `.env.example` templates.

Store real values in Azure environment variables:

- `AUTH_SECRET`
- `DATABASE_URL`
- `JUDGE0_API_KEY`
- `OPENAI_API_KEY`
- `ALLOWED_ORIGINS`

Frontend Vite variables are visible in the browser. Do not put secret keys in `frontend/.env`.

## Backend

Deploy the `backend` directory to Azure App Service.

Runtime:

```text
Python 3.11 or 3.12
Linux
```

Startup command:

```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app
```

Required App Service environment variables:

```env
AUTH_SECRET=<strong-random-secret>
DATABASE_URL=postgresql+psycopg://<user>:<password>@<server>.postgres.database.azure.com:5432/nextstep?sslmode=require
CODE_RUNNER_MODE=judge0
JUDGE0_BASE_URL=https://judge0-ce.p.rapidapi.com
JUDGE0_API_HOST=judge0-ce.p.rapidapi.com
JUDGE0_API_KEY=<judge0-key>
JUDGE0_PYTHON_LANGUAGE_ID=71
OPENAI_API_KEY=<openai-key>
OPENAI_MODEL=gpt-5.4-mini
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_TIMEOUT_SECONDS=30
ALLOWED_ORIGINS=https://<your-static-web-app>.azurestaticapps.net
```

After the backend deploys and the database connection works, initialize the cloud database once:

```bash
python scripts/init_db.py
```

## Frontend

Deploy the `frontend` directory to Azure Static Web Apps.

Build settings:

```text
App location: frontend
Api location: leave empty
Output location: dist
Build command: npm run build
```

Static Web Apps environment variables:

```env
VITE_API_BASE_URL=https://<your-backend>.azurewebsites.net/api
VITE_USE_MOCK=false
VITE_ENABLE_AI_ASSISTANT=true
```

## Final Checks

Before pushing to GitHub:

```bash
git status --short
git check-ignore -v backend/.env frontend/.env
```

`backend/.env` and `frontend/.env` must be ignored. If either appears in `git status` as a tracked or staged file, stop and remove it from Git before pushing.
