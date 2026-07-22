# NextStep Frontend Design

## Overview

NextStep is a React single-page application for adaptive Python practice. It supports student registration and login, diagnostic assessment, coding practice, progressive hints, mastery tracking, learning advice, a study assistant, and role-specific dashboards.

The application uses React 18, TypeScript, Vite, Tailwind CSS, Monaco Editor, Recharts, Framer Motion, and local shadcn-style UI primitives.

## Application Flow

```text
Application start
  -> Validate stored access token
  -> Login or registration when no valid user exists
  -> Diagnostic assessment when a student still requires it
  -> Practice workspace for students
  -> Student dashboard on demand
  -> Teacher dashboard for teacher accounts
```

The root `App` component owns the authenticated user, active view, logout flow, and optional initial exercise selected after a diagnostic assessment.

## Screens

| Screen | Primary user | Responsibilities |
| --- | --- | --- |
| `StudentLoginPage` | Student or teacher | Student login, student registration, and teacher login. |
| `DiagnosticTestPage` | New student | Loads questions, submits answers, and passes the recommended initial exercise to practice. |
| `PracticePage` | Student | Hosts the practice workspace, navigation to the dashboard, and logout. |
| `StudentDashboardPage` | Student | Displays mastery, learning path, and recommended work. |
| `TeacherDashboardPage` | Teacher | Displays class totals, mastery heatmaps, risk indicators, weak KCs, recent submissions, student search, and a student detail drawer. |

## Practice Workspace

The practice workspace is a task-focused three-column layout on larger screens and a stacked layout on smaller screens.

- The header identifies the current session, learner, experiment group, and available dashboard navigation.
- The exercise panel shows the prompt, examples, constraints, difficulty, KC tags, and recommendation reason.
- The editor panel uses Monaco for Python source code, with run, submit, reset, and next-exercise actions.
- The side panel provides progressive hints, mastery visualization, learning advice, and the recommended learning path.
- The result panel displays test cases, runtime metrics, standard output, errors, and mastery changes after execution or submission.

## Component Structure

```text
src/
├── api/                         # HTTP client, domain APIs, mock adapters
├── components/
│   ├── assistant/               # Study assistant dialog
│   ├── common/                  # Loading and empty states
│   ├── dashboard/               # Session header and analytics
│   ├── exercise/                # Editor, exercise, hints, results, navigation
│   ├── mastery/                 # Mastery, advice, heatmap, and learning path
│   └── ui/                      # Reusable presentational primitives
├── features/studyAssistant/     # Assistant request and response protocol
├── hooks/                       # Practice session and exercise-history state
├── pages/                       # Application screens
├── types/                       # Authentication and tutor domain types
└── data/mockTutorData.ts        # Explicit mock-mode data only
```

## State and Data Flow

`usePracticeSession` is the practice-state boundary. It loads the current exercise, owns the editable source code, tracks loading states, appends hints, applies mastery deltas, records local exercise history, requests the next recommendation, and refreshes learning advice after submission.

The API client reads the access token from `localStorage` and attaches it as a Bearer token. Domain API modules translate between frontend camelCase types and backend response shapes where necessary. API failures are propagated to page-level error states.

The teacher dashboard keeps the class view in place while opening selected student details in a right-side drawer. Teachers can search by student name or ID, filter for at-risk students, sort the directory, or use `Cmd/Ctrl + K` to focus the search input. Detail data is loaded only after a teacher selects a student.

## Authentication and Roles

The access token is stored under `nextstep_student_token`. At application start, `getStudentMe` validates it against the backend. The frontend then applies the following routing rules:

- Unauthenticated visitors see the login page.
- Students with `needsDiagnostic=true` see the diagnostic assessment before practice.
- Authenticated students begin in practice and can open their dashboard.
- Authenticated teachers begin in the teacher dashboard.

The backend is responsible for enforcing permissions. The frontend does not treat identifiers supplied by the browser as proof of student ownership.

## API Modes

Mock data remains available for isolated UI demonstrations. The current switch is:

```env
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

Real backend integration requires `VITE_USE_MOCK=false`. With any other value or no value, the current implementation uses mock adapters for most tutor-domain requests. Authentication and diagnostic requests use the backend client.

## Interaction Principles

- Keep the coding task visible while providing contextual help and feedback.
- Present hints progressively and avoid displaying a complete solution.
- Preserve code while loading results or moving between learning views.
- Use explicit loading, disabled, empty, and error states for asynchronous actions.
- Prefer compact operational controls over decorative page sections.
- Maintain accessible labels, keyboard-friendly editor controls, and responsive layouts.

## Validation

Frontend build validation uses:

```bash
cd frontend
npm run build
```

The lightweight deployment package does not include a dedicated frontend test directory. Validate the frontend with `npm run build`, then open the deployed Static Web Apps URL and complete the login and practice submission flow against the backend API described in `API.md`.
