# NextStep API Contract

## Purpose

This document is the canonical HTTP contract for the NextStep AI Tutor frontend and backend. The backend exposes a FastAPI application under the `/api` prefix. The interactive OpenAPI specification is available at `/docs` when the backend is running.

## Conventions

- Base URL: `http://127.0.0.1:8000/api` in local development.
- Requests and responses use JSON unless stated otherwise.
- Bearer-authenticated requests include `Authorization: Bearer <token>`.
- Timestamps are ISO 8601 strings in UTC.
- Mastery values are decimal probabilities in the inclusive range `0.0` to `1.0`.
- Validation errors return `422`; missing or invalid credentials return `401`; insufficient roles return `403`.

## Authentication

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `POST` | `/auth/student/login` | Public | Authenticate a student. |
| `POST` | `/auth/student/register` | Public | Create and authenticate a student account. |
| `POST` | `/auth/teacher/login` | Public | Authenticate a teacher. |
| `GET` | `/auth/student/me` | Authenticated | Return the current user profile. |
| `POST` | `/auth/student/logout` | Authenticated | Revoke the current access token. |
| `DELETE` | `/auth/student/me` | Student | Delete the current student account and related learning data. |

Student and teacher login requests use the same payload:

```json
{
  "email": "student@nextstep.test",
  "password": "demo1234"
}
```

Student registration adds a required `name` field. Successful authentication returns:

```json
{
  "token": "<access-token>",
  "user": {
    "id": "stu_python_beginner_01",
    "name": "Python Beginner",
    "email": "student@nextstep.test",
    "avatarInitials": "PB",
    "needsDiagnostic": false,
    "role": "student"
  }
}
```

## Access Rules

| Access level | Meaning |
| --- | --- |
| Public | No token is required. |
| Authenticated | A valid access token is required. |
| Student | A valid token for a user with the `student` role is required. |
| Teacher | A valid token for a user with the `teacher` role is required. |

For student-only practice endpoints, the backend derives the student identity from the token. Any `student_id` supplied in a request body is ignored for authorization and data ownership.

## Endpoint Summary

| Area | Method | Path | Access | Description |
| --- | --- | --- | --- | --- |
| Diagnostic | `GET` | `/diagnostic/questions` | Authenticated | Return diagnostic questions without answers. |
| Diagnostic | `POST` | `/diagnostic/submit` | Authenticated | Score answers, save diagnostic results, and return recommendations. |
| Practice | `POST` | `/sessions` | Student | Create a practice session. |
| Practice | `GET` | `/session/current-exercise` | Student | Return the current exercise and learning context. |
| Practice | `POST` | `/hints` | Student | Request a progressive hint. |
| Exercises | `GET` | `/exercises` | Public | List exercises with optional filters. |
| Exercises | `GET` | `/exercises/{exercise_id}` | Public | Return one exercise with KC tags and recommendation metadata. |
| Knowledge components | `GET` | `/kcs` | Public | List knowledge components. |
| Knowledge components | `GET` | `/kcs/{code}` | Public | Return one knowledge component. |
| Execution | `POST` | `/executions/run` | Student | Run Python code through the configured Judge0 service. |
| Submission | `POST` | `/submissions` | Student | Test, persist, score, and update mastery for a submission. |
| Recommendation | `POST` | `/recommendations/next` | Student | Select the next exercise for the current student. |
| Mastery | `GET` | `/mastery/me` | Authenticated | Return the caller's mastery profile. |
| Mastery | `GET` | `/students/{student_id}/mastery` | Owner or admin | Return a specific student's mastery profile. |
| Learning advice | `GET` | `/learning-advice/student` | Authenticated | Return the current student's learning advice. |
| Learning advice | `GET` | `/learning-advice/student/{student_id}` | Public | Return advice for a specific student. |
| Dashboard | `GET` | `/dashboard/student` | Student | Return the student dashboard. |
| Dashboard | `GET` | `/dashboard/class-summary` | Teacher | Return a class summary. |
| Study assistant | `POST` | `/assistant/chat` | Authenticated | Interpret a request and recommend an exercise. |
| Evaluation | `GET` | `/evaluation/export` | Public | Return the current evaluation export payload. |

## Core Request and Response Shapes

### Practice Session

`POST /sessions`

```json
{
  "display_name": "Optional display name",
  "preferred_group": "adaptive"
}
```

```json
{
  "session_id": "ses_<random>",
  "student_id": "stu_python_beginner_01",
  "experiment_group": "adaptive"
}
```

`GET /session/current-exercise?session_id=ses_<random>` returns the session identifier, authenticated student identifier, recommended exercise, mastery profile, learning path, dashboard series, latest result, and hint history.

### Exercise and Knowledge Component Queries

`GET /exercises` accepts optional `kc`, `difficulty`, and `status` query parameters. Each list item includes `id`, `title`, `difficulty`, `primary_kc`, and `estimated_minutes`.

`GET /exercises/{exercise_id}` returns an exercise with `starterCode`, examples, constraints, KC tags, and recommendation metadata. `GET /kcs` and `GET /kcs/{code}` expose KC names, descriptions, short names, exercise counts, and associated exercise identifiers.

### Code Execution

`POST /executions/run`

```json
{
  "session_id": "ses_<random>",
  "exercise_id": "EX001",
  "language": "python",
  "code": "def answer(value):\n    return value",
  "stdin": "",
  "expected_output": null
}
```

Only Python is supported. If `exercise_id` is supplied, the backend runs the exercise's test harness. The response contains normalized execution data: `status`, `summary`, `errorType`, runtime and memory metrics, standard output and error, and test-case results. A Judge0 configuration failure is returned as `502`.

### Submission

`POST /submissions`

```json
{
  "session_id": "ses_<random>",
  "exercise_id": "EX001",
  "language": "python",
  "code": "def answer(value):\n    return value"
}
```

The response includes a persisted submission record, the normalized execution result, and the updated mastery profile. A fully correct submission updates every KC associated with the exercise through Bayesian Knowledge Tracing.

### Hints and Recommendations

`POST /hints`

```json
{
  "session_id": "ses_<random>",
  "exercise_id": "EX001",
  "latest_submission_id": "sub_42",
  "requested_hint_level": 2
}
```

Hint levels start at `1` and are capped at `3`. A response contains the hint text, its level, related KC, timestamp, and an `avoid_full_solution` indicator.

`POST /recommendations/next`

```json
{
  "session_id": "ses_<random>",
  "current_exercise_id": "EX001",
  "strategy": "adaptive"
}
```

The response contains the selected exercise, a student-facing reason, the applied strategy, and a confidence score.

### Diagnostic Assessment

`POST /diagnostic/submit`

```json
{
  "answers": [
    { "questionId": "diag_001", "selectedOptionId": "b" }
  ]
}
```

The response reports overall and per-KC results, strengths, weaknesses, and exercise recommendations. A student who has already completed the diagnostic receives `409`.

### Dashboards, Mastery, and Advice

- `GET /dashboard/student` returns the authenticated student's goal, aggregate mastery, recommendation, mastery profile, and learning path.
- `GET /dashboard/class-summary?class_id=demo-python-101` returns class totals, a mastery heatmap, at-risk students, weak KCs, and recent submissions.
- `GET /mastery/me` returns `student_id`, `updated_at`, and KC mastery items.
- `GET /learning-advice/student` returns a summary, strengths, weaknesses, next steps, and warning text.

### Study Assistant

`POST /assistant/chat`

```json
{
  "message": "I need an easy loops exercise.",
  "currentExerciseId": "EX001"
}
```

The response contains a student-facing message, normalized intent (`kcCode`, `difficulty`, `useWeakestKc`, and source), an optional recommended exercise, and an exact-match flag.

## Local Integration

The frontend API base URL is configured with `VITE_API_BASE_URL`. The frontend has a mock-data mode controlled by `VITE_USE_MOCK`; in the current implementation, real backend requests require `VITE_USE_MOCK=false` and a Vite restart.

The backend requires PostgreSQL and uses the environment variables in `backend/.env.example`. Code execution additionally requires a valid Judge0 configuration. AI-assisted hints and recommendation explanations use OpenAI configuration when available and fall back to deterministic responses when the AI service is unavailable.
