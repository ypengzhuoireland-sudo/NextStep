from __future__ import annotations

import json

from app.services.ai.schemas import (
    AssistantIntentRequest,
    HintRequest,
    LearningAdviceRequest,
    RecommendationExplanationRequest,
    dump_jsonable,
)


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


STATIC_RECOMMENDATION_RULES = """You are the recommendation explanation engine for NextStep AI Tutor.

Goal:
Explain why the already-selected next exercise was recommended. The backend owns the recommendation decision; you only explain it in clear student-friendly language.

Rules:
- Return only the structured JSON requested by the API schema.
- Do not change the selected exercise.
- Do not invent mastery values, exercise facts, or recommendation strategies.
- Tie the explanation to the strategy and the recommended exercise.
- Keep student_friendly_reason to one or two short sentences.
- Do not claim the student will master the topic after one exercise.
- Use one focus_kc when possible.
- focus_kc should appear in recommended_exercise.kc_tags or mastery_profile when possible.
- confidence must equal the provided confidence value.
"""


STATIC_LEARNING_ADVICE_RULES = """You are the learning advice engine for NextStep AI Tutor.

Goal:
Generate a dashboard learning summary using only the backend-provided mastery, recent submission, and progress trend data.

Rules:
- Return only the structured JSON requested by the API schema.
- Do not invent submissions, errors, or mastery changes.
- Base every claim on the provided data.
- Mention the weakest KC when one is clearly below 0.6.
- If there is no severe issue, set warning to an empty string.
- next_steps must be specific actions the student or teacher can take.
- Give 2 or 3 concise next_steps when enough activity exists.
- Use student-friendly wording for audience=student.
- Use teacher-facing wording for audience=teacher.
- Avoid harsh labels such as weak student or poor performance.
"""


STATIC_ASSISTANT_INTENT_RULES = """You classify a student's practice request for NextStep AI Tutor.

Rules:
- Return only the structured JSON requested by the API schema.
- Choose kc_code only from the provided knowledge components.
- Set kc_code to null when no specific topic is requested.
- difficulty must be easy, medium, hard, or null.
- Set use_weakest_kc to true when the student asks for a recommendation or does not name a topic.
- Do not select or invent an exercise ID.
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


def build_recommendation_prompt(request: RecommendationExplanationRequest) -> str:
    current_exercise_json = json.dumps(
        dump_jsonable(request.current_exercise),
        ensure_ascii=False,
        indent=2,
    )
    recommended_exercise_json = json.dumps(
        dump_jsonable(request.recommended_exercise),
        ensure_ascii=False,
        indent=2,
    )
    mastery_json = json.dumps(request.mastery_profile, ensure_ascii=False, indent=2)

    return f"""{STATIC_RECOMMENDATION_RULES}

Current exercise:
{current_exercise_json}

Recommended exercise:
{recommended_exercise_json}

Mastery profile:
{mastery_json}

Strategy:
{request.strategy}

Confidence:
{request.confidence}
"""


def build_learning_advice_prompt(request: LearningAdviceRequest) -> str:
    mastery_json = json.dumps(dump_jsonable(request.mastery_profile), ensure_ascii=False, indent=2)
    submissions_json = json.dumps(
        dump_jsonable(request.recent_submissions),
        ensure_ascii=False,
        indent=2,
    )
    trend_json = json.dumps(dump_jsonable(request.progress_trend), ensure_ascii=False, indent=2)

    return f"""{STATIC_LEARNING_ADVICE_RULES}

Audience:
{request.audience}

Student ID:
{request.student_id}

Mastery profile:
{mastery_json}

Recent submissions:
{submissions_json}

Progress trend:
{trend_json}
"""


def build_assistant_intent_prompt(request: AssistantIntentRequest) -> str:
    """Build the constrained prompt used to classify a practice request."""
    kcs_json = json.dumps(request.available_kcs, ensure_ascii=False, indent=2)

    return f"""{STATIC_ASSISTANT_INTENT_RULES}

Available knowledge components:
{kcs_json}

Student request:
{request.message}
"""
