# Practice Hint LLM Demo

This folder is an independent reference implementation for the Practice page layered AI Hint feature. It does not modify or depend on the existing backend app.

## What It Builds

- `POST /api/hints`
- OpenAI Responses API call with Structured Outputs
- L1/L2/L3 hint generation
- Safe fallback when the API key is missing or the model response is invalid

## Run Locally

```powershell
cd D:\PRACTICAL\Summer\LLM\practice_hint_demo
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY`.

```powershell
uvicorn main:app --reload --port 8010
```

Send a JSON request to:

```text
http://127.0.0.1:8010/api/hints
```

## Integration Notes

The existing backend can later copy the service boundary:

1. Collect exercise, current student code, latest result, mastery context, and requested level.
2. Call `OpenAIHintService.generate_hint(...)`.
3. Convert `HintResponse.hint_text` to the frontend field named `text` if the existing frontend contract is kept.
4. Log successful and failed LLM calls in the backend-owned `LLMInteractionLog`.
