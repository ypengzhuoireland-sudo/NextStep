# Practice Hint Demo Design

## Scope

This implementation is a standalone LLM-team deliverable. It lives entirely under `LLM/practice_hint_demo` and does not change the existing backend.

## Architecture

The demo exposes a small FastAPI route, `POST /api/hints`, that accepts the same conceptual context described in `LLM/hint_prompt.md`: exercise data, current student code, latest result, mastery context, and requested hint level.

The route delegates generation to `OpenAIHintService`. The service builds a stable prompt, calls the OpenAI Responses API, requests Structured Outputs with a JSON schema, validates the returned JSON with Pydantic, and returns `HintResponse`.

If OpenAI is not configured or the model returns an invalid response, the route returns a safe fallback hint. This keeps the UI/API usable during local demos without an API key.

## File Responsibilities

- `main.py`: FastAPI app and `/api/hints` endpoint.
- `schemas.py`: Pydantic request, response, and OpenAI settings models.
- `prompt_builder.py`: Stable hint prompt rules plus dynamic student context.
- `openai_hint_service.py`: Responses API payload, HTTP transport, response extraction, validation, fallback.

## Integration Path

When the backend team is ready to integrate:

1. Keep the existing backend endpoint path `/api/hints`.
2. Collect current editor code from the frontend, not only the latest saved submission.
3. Convert backend exercise/submission/mastery models into `HintRequest`.
4. Call `OpenAIHintService.generate_hint`.
5. Map `hint_text` to the frontend's current `text` field if the existing frontend type is unchanged.
6. Save both successful and failed LLM calls in the backend-owned `LLMInteractionLog`.
