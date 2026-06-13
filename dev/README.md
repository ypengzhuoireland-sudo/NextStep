# NextStep LLM Development Bundle

This folder contains the source files used by the frontend and backend LLM features.

Actual `.env` files with secrets were not copied. Use `LLM_ENV.example` for the required OpenAI variable names.

## LLM Features

1. AI Hint
   - Backend endpoint: `POST /api/hints`
   - Backend files:
     - `NextStep-backend/NextStep-backend/backend/app/api/practice.py`
     - `NextStep-backend/NextStep-backend/backend/app/services/practice_service.py`
     - `NextStep-backend/NextStep-backend/backend/app/services/ai/*`
   - Frontend files:
     - `NextStep-frontend/NextStep-frontend/frontend/src/api/hints.ts`
     - `NextStep-frontend/NextStep-frontend/frontend/src/components/exercise/HintPanel.tsx`

2. AI Recommendation
   - Backend endpoint: `POST /api/recommendations/next`
   - Backend files:
     - `NextStep-backend/NextStep-backend/backend/app/api/recommendations.py`
     - `NextStep-backend/NextStep-backend/backend/app/services/recommendation_api_service.py`
     - `NextStep-backend/NextStep-backend/backend/app/services/ai/*`
   - Frontend files:
     - `NextStep-frontend/NextStep-frontend/frontend/src/api/recommendations.ts`
     - `NextStep-frontend/NextStep-frontend/frontend/src/components/exercise/NextExerciseButton.tsx`

3. AI Learning Advice
   - Backend endpoint: `GET /api/learning-advice/student`
   - Backend files:
     - `NextStep-backend/NextStep-backend/backend/app/api/learning_advice.py`
     - `NextStep-backend/NextStep-backend/backend/app/services/learning_advice_service.py`
     - `NextStep-backend/NextStep-backend/backend/app/services/ai/*`
   - Frontend files:
     - `NextStep-frontend/NextStep-frontend/frontend/src/api/learningAdvice.ts`
     - `NextStep-frontend/NextStep-frontend/frontend/src/components/mastery/LearningAdviceCard.tsx`

## Shared Wiring

- Backend router registration: `NextStep-backend/NextStep-backend/backend/app/main.py`
- Backend OpenAI request/prompt logic:
  - `NextStep-backend/NextStep-backend/backend/app/services/ai/llm_client.py`
  - `NextStep-backend/NextStep-backend/backend/app/services/ai/prompt_builders.py`
  - `NextStep-backend/NextStep-backend/backend/app/services/ai/schemas.py`
- Frontend page/hook wiring:
  - `NextStep-frontend/NextStep-frontend/frontend/src/pages/PracticePage.tsx`
  - `NextStep-frontend/NextStep-frontend/frontend/src/hooks/usePracticeSession.ts`
  - `NextStep-frontend/NextStep-frontend/frontend/src/api/tutor.ts`

## Tests And Assertions

- Backend:
  - `NextStep-backend/NextStep-backend/backend/tests/test_ai_integration.py`
  - `NextStep-backend/NextStep-backend/backend/tests/test_ai_services.py`
  - `NextStep-backend/NextStep-backend/backend/tests/test_learning_advice_service.py`
- Frontend:
  - `NextStep-frontend/NextStep-frontend/frontend/scripts/assert-learning-advice-card.mjs`
