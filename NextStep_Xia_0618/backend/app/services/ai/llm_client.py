from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Protocol

from pydantic import ValidationError

from app.services.ai.prompt_builders import (
    build_hint_prompt,
    build_learning_advice_prompt,
    build_recommendation_prompt,
)
from app.services.ai.schemas import (
    HintRequest,
    HintResponse,
    LearningAdviceRequest,
    LearningAdviceResponse,
    OpenAISettings,
    RecommendationExplanationRequest,
    RecommendationExplanationResponse,
)


class LLMGenerationError(Exception):
    pass


class OpenAITransport(Protocol):
    def create_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...


HINT_RESPONSE_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "level": {"type": "integer", "enum": [1, 2, 3]},
        "title": {"type": "string", "minLength": 1},
        "hint_text": {"type": "string", "minLength": 1},
        "next_step": {"type": "string", "minLength": 1},
        "kc_code": {"type": "string", "minLength": 1},
        "avoid_full_solution": {"type": "boolean", "const": True},
    },
    "required": [
        "level",
        "title",
        "hint_text",
        "next_step",
        "kc_code",
        "avoid_full_solution",
    ],
}

RECOMMENDATION_EXPLANATION_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "reason": {"type": "string", "minLength": 1},
        "student_friendly_reason": {"type": "string", "minLength": 1},
        "focus_kc": {"type": "string", "minLength": 1},
        "expected_benefit": {"type": "string", "minLength": 1},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "required": [
        "reason",
        "student_friendly_reason",
        "focus_kc",
        "expected_benefit",
        "confidence",
    ],
}

LEARNING_ADVICE_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "summary": {"type": "string", "minLength": 1},
        "strengths": {"type": "array", "items": {"type": "string"}, "maxItems": 5},
        "weaknesses": {"type": "array", "items": {"type": "string"}, "maxItems": 5},
        "next_steps": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "minItems": 1,
            "maxItems": 3,
        },
        "warning": {"type": "string"},
    },
    "required": ["summary", "strengths", "weaknesses", "next_steps", "warning"],
}


class OpenAIResponsesTransport:
    def __init__(self, settings: OpenAISettings) -> None:
        self.settings = settings

    def create_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url=f"{self.settings.base_url.rstrip('/')}/responses",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self.settings.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise LLMGenerationError(f"OpenAI API error {exc.code}: {error_body}") from exc
        except urllib.error.URLError as exc:
            raise LLMGenerationError(f"OpenAI connection error: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise LLMGenerationError("OpenAI response was not valid JSON") from exc


class OpenAIHintService:
    def __init__(
        self,
        settings: OpenAISettings | None = None,
        transport: OpenAITransport | None = None,
    ) -> None:
        self.settings = settings or OpenAISettings.from_env()
        self.transport = transport or OpenAIResponsesTransport(self.settings)

    def generate_hint(self, request: HintRequest) -> HintResponse:
        if not self.settings.api_key:
            raise LLMGenerationError("OPENAI_API_KEY is not configured")

        response_text = _send_json_schema_request(
            self.transport,
            self.settings.model,
            build_hint_prompt(request),
            "nextstep_practice_hint",
            HINT_RESPONSE_JSON_SCHEMA,
        )

        try:
            hint = HintResponse.model_validate(json.loads(response_text))
        except json.JSONDecodeError as exc:
            raise LLMGenerationError("Model output was not valid JSON") from exc
        except ValidationError as exc:
            raise LLMGenerationError(f"Model output failed schema validation: {exc}") from exc

        validate_hint_response(hint, request)
        return hint


class OpenAIRecommendationExplanationService:
    def __init__(
        self,
        settings: OpenAISettings | None = None,
        transport: OpenAITransport | None = None,
    ) -> None:
        self.settings = settings or OpenAISettings.from_env()
        self.transport = transport or OpenAIResponsesTransport(self.settings)

    def generate_explanation(
        self,
        request: RecommendationExplanationRequest,
    ) -> RecommendationExplanationResponse:
        if not self.settings.api_key:
            raise LLMGenerationError("OPENAI_API_KEY is not configured")

        response_text = _send_json_schema_request(
            self.transport,
            self.settings.model,
            build_recommendation_prompt(request),
            "nextstep_recommendation_explanation",
            RECOMMENDATION_EXPLANATION_JSON_SCHEMA,
        )

        try:
            explanation = RecommendationExplanationResponse.model_validate(json.loads(response_text))
        except json.JSONDecodeError as exc:
            raise LLMGenerationError("Model output was not valid JSON") from exc
        except ValidationError as exc:
            raise LLMGenerationError(f"Model output failed schema validation: {exc}") from exc

        validate_explanation_response(explanation, request)
        return explanation


class OpenAILearningAdviceService:
    def __init__(
        self,
        settings: OpenAISettings | None = None,
        transport: OpenAITransport | None = None,
    ) -> None:
        self.settings = settings or OpenAISettings.from_env()
        self.transport = transport or OpenAIResponsesTransport(self.settings)

    def generate_advice(self, request: LearningAdviceRequest) -> LearningAdviceResponse:
        if not self.settings.api_key:
            raise LLMGenerationError("OPENAI_API_KEY is not configured")

        response_text = _send_json_schema_request(
            self.transport,
            self.settings.model,
            build_learning_advice_prompt(request),
            "nextstep_learning_advice",
            LEARNING_ADVICE_JSON_SCHEMA,
        )

        try:
            advice = LearningAdviceResponse.model_validate(json.loads(response_text))
        except json.JSONDecodeError as exc:
            raise LLMGenerationError("Model output was not valid JSON") from exc
        except ValidationError as exc:
            raise LLMGenerationError(f"Model output failed schema validation: {exc}") from exc

        validate_learning_advice(advice)
        return advice


def _send_json_schema_request(
    transport: OpenAITransport,
    model: str,
    prompt: str,
    schema_name: str,
    schema: dict[str, Any],
) -> str:
    payload = {
        "model": model,
        "input": prompt,
        "text": {
            "verbosity": "low",
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "schema": schema,
                "strict": True,
            },
        },
    }
    return extract_response_text(transport.create_response(payload))


def extract_response_text(response_payload: dict[str, Any]) -> str:
    if isinstance(response_payload.get("output_text"), str):
        return response_payload["output_text"]

    output = response_payload.get("output", [])
    for item in output:
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                return content["text"]

    raise LLMGenerationError("OpenAI response did not contain output_text")


def validate_hint_response(hint: HintResponse, request: HintRequest) -> None:
    if hint.level != request.requested_hint_level:
        raise LLMGenerationError("Model returned a hint level different from requested_hint_level")

    if hint.avoid_full_solution is not True:
        raise LLMGenerationError("Model must set avoid_full_solution to true")

    allowed_kcs = set(request.exercise.kc_tags)
    if allowed_kcs and hint.kc_code not in allowed_kcs:
        raise LLMGenerationError("Model returned kc_code outside exercise kc_tags")


def validate_explanation_response(
    explanation: RecommendationExplanationResponse,
    request: RecommendationExplanationRequest,
) -> None:
    if explanation.confidence != request.confidence:
        raise LLMGenerationError(
            "Model returned confidence different from backend-provided confidence",
        )

    allowed_focus = set(request.recommended_exercise.kc_tags) | set(request.mastery_profile)
    if allowed_focus and explanation.focus_kc not in allowed_focus:
        raise LLMGenerationError(
            "Model returned focus_kc outside recommended_exercise.kc_tags and mastery_profile",
        )


def validate_learning_advice(advice: LearningAdviceResponse) -> None:
    if not advice.next_steps:
        raise LLMGenerationError("Model output must include at least one next_steps item")


def create_fallback_hint(request: HintRequest) -> HintResponse:
    kc_code = request.exercise.kc_tags[0] if request.exercise.kc_tags else "general_debugging"
    return HintResponse(
        level=request.requested_hint_level,
        title="Review the prompt carefully",
        hint_text=(
            "Compare your code with the required input, output, and constraints before making "
            "a large change."
        ),
        next_step="Run one example by hand and check where your result first differs.",
        kc_code=kc_code,
        avoid_full_solution=True,
    )


def create_fallback_explanation(
    request: RecommendationExplanationRequest,
) -> RecommendationExplanationResponse:
    focus_kc = (
        request.recommended_exercise.kc_tags[0]
        if request.recommended_exercise.kc_tags
        else "general_practice"
    )
    return RecommendationExplanationResponse(
        reason="The selected exercise matches the next available practice target.",
        student_friendly_reason=(
            "This exercise gives you another chance to practise a related skill at the "
            "current difficulty level."
        ),
        focus_kc=focus_kc,
        expected_benefit="You will get more practice with the current topic.",
        confidence=request.confidence,
    )


def create_fallback_advice(request: LearningAdviceRequest) -> LearningAdviceResponse:
    weakest = min(request.mastery_profile, key=lambda item: item.mastery, default=None)
    if weakest is None:
        return LearningAdviceResponse(
            summary="There is not enough recent activity to generate a detailed learning summary yet.",
            strengths=[],
            weaknesses=[],
            next_steps=[
                "Complete one practice exercise.",
                "Submit code so progress and weak areas can be estimated.",
            ],
            warning="",
        )

    return LearningAdviceResponse(
        summary=f"Your current lowest mastery area is {weakest.kc_name}.",
        strengths=[
            item.kc_name for item in request.mastery_profile if item.mastery >= 0.75
        ][:3],
        weaknesses=[
            item.kc_name for item in request.mastery_profile if item.mastery < 0.6
        ][:3],
        next_steps=[
            f"Practise one exercise focused on {weakest.kc_name}.",
            "Review the feedback from your most recent submission.",
        ],
        warning=(
            f"{weakest.kc_name} needs attention."
            if weakest.mastery < 0.4
            else ""
        ),
    )
