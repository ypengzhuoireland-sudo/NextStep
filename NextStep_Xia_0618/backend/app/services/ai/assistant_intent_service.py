from __future__ import annotations

import json
import re

from pydantic import ValidationError

from app.services.ai.llm_client import (
    LLMGenerationError,
    OpenAIResponsesTransport,
    OpenAITransport,
    _send_json_schema_request,
)
from app.services.ai.prompt_builders import build_assistant_intent_prompt
from app.services.ai.schemas import (
    AssistantIntent,
    AssistantIntentRequest,
    AssistantIntentResult,
    OpenAISettings,
)


ASSISTANT_INTENT_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "kc_code": {
            "anyOf": [
                {"type": "string"},
                {"type": "null"},
            ]
        },
        "difficulty": {
            "anyOf": [
                {"type": "string", "enum": ["easy", "medium", "hard"]},
                {"type": "null"},
            ]
        },
        "use_weakest_kc": {"type": "boolean"},
    },
    "required": ["kc_code", "difficulty", "use_weakest_kc"],
}

KC_ALIASES = {
    "KC001": ("variable", "variables", "expression", "expressions"),
    "KC002": ("condition", "conditions", "conditional", "conditionals", "if", "else"),
    "KC003": ("loop", "loops", "for loop", "while loop", "iteration"),
    "KC004": ("function", "functions", "parameter", "parameters", "return value"),
    "KC005": ("string", "strings", "text"),
    "KC006": ("list", "lists", "array", "arrays"),
    "KC007": ("dictionary", "dictionaries", "dict", "set", "sets"),
    "KC008": ("nested data", "nested list", "nested lists", "nested structure"),
    "KC009": ("recursion", "recursive"),
    "KC010": ("oop", "object oriented", "object-oriented", "class", "classes", "object"),
    "KC011": ("exception", "exceptions", "error handling", "validation", "try except"),
    "KC012": ("algorithm", "algorithms", "problem solving", "problem-solving"),
}

DIFFICULTY_ALIASES = {
    "easy": ("easy", "easier", "beginner", "simple", "basic"),
    "medium": ("medium", "intermediate", "normal"),
    "hard": ("hard", "harder", "advanced", "difficult", "challenging"),
}

WEAKEST_PATTERNS = (
    "weak topic",
    "weakest",
    "weak area",
    "what should i practise",
    "what should i practice",
    "recommend something",
    "choose something",
    "something useful",
)


class OpenAIAssistantIntentService:
    """Use OpenAI structured output to classify one student request."""

    def __init__(
        self,
        settings: OpenAISettings | None = None,
        transport: OpenAITransport | None = None,
    ) -> None:
        self.settings = settings or OpenAISettings.from_env()
        self.transport = transport or OpenAIResponsesTransport(self.settings)

    def parse_intent(self, request: AssistantIntentRequest) -> AssistantIntent:
        """Return a validated intent whose KC belongs to the supplied KC map."""
        if not self.settings.api_key:
            raise LLMGenerationError("OPENAI_API_KEY is not configured")

        response_text = _send_json_schema_request(
            self.transport,
            self.settings.model,
            build_assistant_intent_prompt(request),
            "nextstep_assistant_intent",
            ASSISTANT_INTENT_JSON_SCHEMA,
        )

        try:
            intent = AssistantIntent.model_validate(json.loads(response_text))
        except json.JSONDecodeError as exc:
            raise LLMGenerationError("Model output was not valid JSON") from exc
        except ValidationError as exc:
            raise LLMGenerationError(
                f"Model output failed schema validation: {exc}"
            ) from exc

        if intent.kc_code is not None and intent.kc_code not in request.available_kcs:
            raise LLMGenerationError("Model returned an unknown kc_code")

        return intent


def parse_assistant_intent(
    message: str,
    available_kcs: dict[str, str],
    openai_service: OpenAIAssistantIntentService | None = None,
) -> AssistantIntentResult:
    """Use OpenAI when available and fall back to deterministic keyword parsing."""
    service = openai_service or OpenAIAssistantIntentService()
    request = AssistantIntentRequest(message=message, available_kcs=available_kcs)

    try:
        return AssistantIntentResult(
            intent=service.parse_intent(request),
            source="openai",
        )
    except LLMGenerationError:
        return AssistantIntentResult(
            intent=parse_keyword_intent(message, available_kcs),
            source="fallback",
        )


def parse_keyword_intent(
    message: str,
    available_kcs: dict[str, str],
) -> AssistantIntent:
    """Classify common English topic and difficulty phrases without an API call."""
    normalized = _normalize(message)
    kc_code = next(
        (
            code
            for code, aliases in KC_ALIASES.items()
            if code in available_kcs
            and any(_contains_phrase(normalized, alias) for alias in aliases)
        ),
        None,
    )
    difficulty = next(
        (
            level
            for level, aliases in DIFFICULTY_ALIASES.items()
            if any(_contains_phrase(normalized, alias) for alias in aliases)
        ),
        None,
    )
    use_weakest = kc_code is None or any(
        pattern in normalized for pattern in WEAKEST_PATTERNS
    )

    return AssistantIntent(
        kc_code=kc_code,
        difficulty=difficulty,
        use_weakest_kc=use_weakest,
    )


def _normalize(value: str) -> str:
    """Normalise punctuation and casing for phrase matching."""
    return re.sub(r"[^\w-]+", " ", value.lower()).strip()


def _contains_phrase(value: str, phrase: str) -> bool:
    """Match a complete word or phrase inside normalised text."""
    return f" {phrase} " in f" {value} "
