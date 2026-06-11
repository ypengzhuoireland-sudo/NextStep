from __future__ import annotations

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI

from openai_hint_service import HintGenerationError, OpenAIHintService, create_fallback_hint
from schemas import HintRequest, HintResponse, OpenAISettings


app = FastAPI(title="NextStep Practice Hint LLM Demo")


@app.post("/api/hints", response_model=HintResponse)
def request_hint(request: HintRequest) -> HintResponse:
    settings = OpenAISettings.from_env()

    try:
        return OpenAIHintService(settings).generate_hint(request)
    except HintGenerationError:
        return create_fallback_hint(request)
