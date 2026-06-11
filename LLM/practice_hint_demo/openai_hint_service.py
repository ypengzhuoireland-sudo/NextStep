from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Protocol

from pydantic import ValidationError

from prompt_builder import build_hint_prompt
from schemas import HintRequest, HintResponse, OpenAISettings


class HintGenerationError(Exception):
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
            raise HintGenerationError(f"OpenAI API error {exc.code}: {error_body}") from exc
        except urllib.error.URLError as exc:
            raise HintGenerationError(f"OpenAI connection error: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise HintGenerationError("OpenAI response was not valid JSON") from exc


class OpenAIHintService:
    def __init__(
        self,
        settings: OpenAISettings,
        transport: OpenAITransport | None = None,
    ) -> None:
        self.settings = settings
        self.transport = transport or OpenAIResponsesTransport(settings)

    def generate_hint(self, request: HintRequest) -> HintResponse:
        if not self.settings.api_key:
            raise HintGenerationError("OPENAI_API_KEY is not configured")

        payload = build_openai_payload(self.settings, request)
        response_payload = self.transport.create_response(payload)
        response_text = extract_response_text(response_payload)

        try:
            response_json = json.loads(response_text)
            hint = HintResponse.model_validate(response_json)
        except json.JSONDecodeError as exc:
            raise HintGenerationError("Model output was not valid JSON") from exc
        except ValidationError as exc:
            raise HintGenerationError(f"Model output failed schema validation: {exc}") from exc

        validate_hint_response(hint, request)
        return hint


def build_openai_payload(settings: OpenAISettings, request: HintRequest) -> dict[str, Any]:
    return {
        "model": settings.model,
        "input": build_hint_prompt(request),
        "text": {
            "verbosity": "low",
            "format": {
                "type": "json_schema",
                "name": "nextstep_practice_hint",
                "schema": HINT_RESPONSE_JSON_SCHEMA,
                "strict": True,
            },
        },
    }


def extract_response_text(response_payload: dict[str, Any]) -> str:
    if isinstance(response_payload.get("output_text"), str):
        return response_payload["output_text"]

    output = response_payload.get("output", [])
    for item in output:
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                return content["text"]

    raise HintGenerationError("OpenAI response did not contain output_text")


def validate_hint_response(hint: HintResponse, request: HintRequest) -> None:
    if hint.level != request.requested_hint_level:
        raise HintGenerationError("Model returned a hint level different from requested_hint_level")

    if hint.avoid_full_solution is not True:
        raise HintGenerationError("Model must set avoid_full_solution to true")

    allowed_kcs = set(request.exercise.kc_tags)
    if allowed_kcs and hint.kc_code not in allowed_kcs:
        raise HintGenerationError("Model returned kc_code outside exercise kc_tags")


def create_fallback_hint(request: HintRequest) -> HintResponse:
    return HintResponse(
        level=request.requested_hint_level,
        title="Review the prompt carefully",
        hint_text=(
            "Compare your code with the required input, output, and constraints before making "
            "a large change."
        ),
        next_step="Run one example by hand and check where your result first differs.",
        kc_code="general_debugging",
        avoid_full_solution=True,
    )
