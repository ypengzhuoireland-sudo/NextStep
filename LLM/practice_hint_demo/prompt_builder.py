from __future__ import annotations

import json

from schemas import HintRequest, dump_jsonable


STATIC_HINT_RULES = """You are the hint engine for NextStep AI Tutor.

Goal:
Generate one short layered hint that helps the student make progress without giving away the full solution.

Rules:
- Return only the structured JSON requested by the API schema.
- Do not give the complete final code.
- Do not invent errors, tests, mastery values, or exercise facts.
- Use the requested level exactly.
- L1: conceptual direction only; no exact code changes or pseudocode.
- L2: identify the likely mistake and where to inspect.
- L3: give a general pattern or pseudocode, but not the exact completed function.
- Pick one kc_code from the exercise kc_tags when possible.
- Keep the tone supportive and concise.
"""


def build_hint_prompt(request: HintRequest) -> str:
    exercise_json = json.dumps(dump_jsonable(request.exercise), ensure_ascii=False, indent=2)
    latest_result_json = json.dumps(
        dump_jsonable(request.latest_result) if request.latest_result else None,
        ensure_ascii=False,
        indent=2,
    )
    mastery_json = json.dumps(request.mastery_context, ensure_ascii=False, indent=2)

    return f"""{STATIC_HINT_RULES}

Requested hint level: {request.requested_hint_level}

Student task:
{exercise_json}

Student code:
{request.student_code or "(no code provided)"}

Latest result:
{latest_result_json}

Mastery context:
{mastery_json}
"""
