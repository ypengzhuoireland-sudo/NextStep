# NextStep Backend Design

## Overview

The NextStep backend is a FastAPI application that manages authentication, diagnostics, practice sessions, code execution, submissions, mastery tracking, recommendations, AI-assisted learning support, and dashboards. It uses SQLAlchemy with PostgreSQL and exposes HTTP endpoints below `/api`.

The application entry point is `backend/app/main.py`. It configures CORS for local frontend development, registers routers, and redirects `/` to FastAPI documentation.

## Architecture

```text
HTTP request
  -> FastAPI router
  -> Authentication and role dependency
  -> Service layer
  -> SQLAlchemy models and external clients
  -> Pydantic response schema
```

| Layer | Responsibility |
| --- | --- |
| `app/api` | Request parsing, authorization, HTTP status mapping, and response selection. |
| `app/services` | Domain behavior for learning, execution, recommendations, dashboards, and authentication. |
| `app/models` | SQLAlchemy persistence models. |
| `app/schemas` | Pydantic request and response contracts. |
| `app/db` | Database engine, session lifecycle, schema initialization, and seed loading. |
| `app/core` | Environment-backed configuration. |

## Domain Modules

| Module | Responsibilities |
| --- | --- |
| Authentication | Student registration, student login, teacher login, access-token validation, logout, and student account deletion. |
| Diagnostic | Question delivery, answer validation, per-KC scoring, initial mastery assignment, and initial exercise recommendations. |
| Practice | Practice-session creation, current exercise assembly, hint context, and learning-path data. |
| Execution | Python-only Judge0 submission, normalization of runtime and compiler errors, and execution result formatting. |
| Submission | Exercise test harness generation, persistence of attempts, scoring, and mastery updates. |
| Mastery | KC-level profile generation and Bayesian Knowledge Tracing updates. |
| Recommendation | Selection of the next exercise from the student's weakest KC and generation of a learner-facing rationale. |
| AI support | Hint generation, assistant intent parsing, and recommendation explanations with deterministic fallbacks. |
| Dashboard | Student progress summaries and teacher class-level analytics. |

## Authentication and Authorization

Access tokens are signed HMAC JWTs. They include the user's student identifier, username, role, issue time, expiry, and token type. Revoked access tokens are held in the current process.

`app/api/student_access.py` provides the shared `require_student_user` dependency for practice endpoints. It enforces all of the following:

1. A Bearer token must be present.
2. The token must resolve to an active user.
3. The resolved user must have the `student` role.
4. The student identity is derived from the token, never from request-body ownership fields.

Practice sessions, current exercises, hints, recommendations, execution, and submissions use this dependency. Student and teacher dashboard routes enforce their own role-specific checks. The detailed endpoint contract is maintained in `API.md`.

## Persistence Model

| Model | Purpose |
| --- | --- |
| `User` | Student or teacher identity, role, password hash, account state, and diagnostic completion state. |
| `KnowledgeComponent` | A tracked programming skill or concept. |
| `Exercise` | A coding exercise, starter code, function name, test cases, hints, and metadata. |
| `ExerciseKnowledgeComponent` | Many-to-many exercise-to-KC mapping. |
| `StudentMastery` | Current mastery probability for a student and KC. |
| `KnowledgeComponentBKTParameters` | KC-specific BKT prior, learn, guess, and slip values. |
| `MasteryEvent` | Auditable BKT transition for a submission. |
| `Submission` | Persisted source code, result, score, test results, and timestamp. |
| `DiagnosticAttempt` | Diagnostic answers, KC results, score, and timestamp. |

Database initialization creates tables, applies the current compatibility alterations, seeds users, seeds the Python exercise bank, creates default BKT parameters, and initializes mastery rows.

## Learning and Recommendation Flow

```text
Student submission
  -> Build exercise-specific Python test harness
  -> Execute through Judge0
  -> Parse individual test outcomes
  -> Persist submission
  -> Update every linked KC with BKT
  -> Write mastery events
  -> Rebuild mastery profile and learning advice
  -> Recommend the next exercise from the weakest KC
```

The default BKT parameters are `prior=0.2`, `learn=0.15`, `guess=0.2`, and `slip=0.1`. New students begin at `0.0` mastery. An incorrect result is constrained so that it does not increase mastery above the previous value.

The recommendation service first considers the student's weakest tracked KC, excludes the current exercise when possible, and falls back to another published exercise if a more specific match is unavailable. AI services can explain a recommendation, but deterministic fallback text preserves the learning flow when the AI provider is unavailable.

## Code Execution

The backend supports Python through Judge0. For a practice exercise, the submission service wraps the student's function in a generated test harness so a single remote execution returns the results of visible and hidden tests. The execution service normalizes external status data into the application response format.

Judge0 credentials and endpoint settings are environment-driven. Missing credentials, remote errors, and timeouts are exposed as execution-service failures and translated to `502 Bad Gateway` by the API layer. The current implementation performs a synchronous remote request with a 20-second timeout.

## AI-Assisted Support

The AI layer has three functions:

- Progressive hints use exercise context, recent student code, failed tests, and relevant mastery values.
- The study assistant parses a student request for KC, difficulty, or general practice intent and selects a suitable exercise.
- Recommendation explanations turn the selected exercise and mastery context into learner-facing text.

OpenAI-backed services are optional. If a configured AI call fails, the backend returns a deterministic fallback hint, intent interpretation, or explanation instead of failing the learning workflow.

## Configuration and Local Operation

`backend/.env.example` documents the supported configuration values:

- `AUTH_SECRET`, access-token lifetime, password-hash iterations, and database URL.
- Judge0 base URL, host, API key, and Python language identifier.
- OpenAI API key, model, base URL, and timeout.

The local database must be initialized before use:

```bash
cd backend
python3 scripts/init_db.py
python3 -m uvicorn app.main:app --reload
```

The frontend is allowed from local Vite origins on ports `3000` and `5173`.

## Testing and Operational Limits

Backend tests live in `backend/tests` and cover BKT calculations, diagnostic behavior, assistant behavior, execution normalization, recommendations, dashboards, submissions, and student-access rules. Run them with:

```bash
cd backend
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Current limits that should be considered before production deployment:

- Access-token revocation is in-process and is not shared across multiple backend instances.
- Judge0 execution is synchronous and depends on a configured third-party service.
- `GET /learning-advice/student/{student_id}` and `GET /evaluation/export` are not yet protected by the same role policy as practice endpoints.
- Production deployment still requires rate limiting, centralized logging, persistent token revocation, and environment-specific secret management.
