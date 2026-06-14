from __future__ import annotations

from datetime import timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.submission import Submission
from app.schemas.learning_advice import LearningAdviceResponse
from app.services.ai.llm_client import (
    LLMGenerationError,
    OpenAILearningAdviceService,
    create_fallback_advice,
)
from app.services.ai.schemas import (
    LearningAdviceRequest as AILearningAdviceRequest,
    LearningAdviceResponse as AILearningAdviceResponse,
    MasteryProfileItem,
    ProgressTrend,
    RecentSubmission as AIRecentSubmission,
)
from app.services.mastery_service import get_student_mastery_profile


def build_student_learning_advice(db: Session, student_id: str) -> LearningAdviceResponse:
    return build_learning_advice_from_ai_request(
        build_ai_learning_advice_request(db, student_id),
    )


def build_learning_advice_from_ai_request(
    request: AILearningAdviceRequest,
) -> LearningAdviceResponse:
    try:
        advice = OpenAILearningAdviceService().generate_advice(request)
    except LLMGenerationError:
        advice = create_fallback_advice(request)

    return map_learning_advice_response(advice)


def build_ai_learning_advice_request(
    db: Session,
    student_id: str,
) -> AILearningAdviceRequest:
    mastery_items = build_mastery_profile_items(db, student_id)
    overall_mastery = calculate_overall_mastery(mastery_items)

    return AILearningAdviceRequest(
        student_id=student_id,
        mastery_profile=mastery_items,
        recent_submissions=build_recent_submission_items(db, student_id),
        progress_trend=ProgressTrend(
            overall_mastery=overall_mastery,
            overall_delta=0.0,
        ),
    )


def build_mastery_profile_items(db: Session, student_id: str) -> list[MasteryProfileItem]:
    profile = get_student_mastery_profile(db, student_id)
    if profile is None:
        return []

    return [
        MasteryProfileItem(
            kc_code=item.code,
            kc_name=item.name,
            mastery=item.mastery,
            trend=item.trend,
        )
        for item in profile.items
    ]


def build_recent_submission_items(db: Session, student_id: str) -> list[AIRecentSubmission]:
    rows = db.execute(
        select(Submission, Exercise.title, Exercise.kc_id)
        .join(Exercise, Exercise.id == Submission.exercise_id)
        .where(Submission.student_id == student_id)
        .order_by(Submission.created_at.desc(), Submission.id.desc())
        .limit(5)
    ).all()

    return [
        AIRecentSubmission(
            exercise_title=title,
            status="passed" if submission.passed else "failed",
            kc_code=kc_id,
            error_type="" if submission.passed else submission.status,
            created_at=submission.created_at.astimezone(timezone.utc).isoformat(),
        )
        for submission, title, kc_id in rows
    ]


def calculate_overall_mastery(items: list[MasteryProfileItem]) -> float:
    if not items:
        return 0.0

    return round(sum(item.mastery for item in items) / len(items), 2)


def map_learning_advice_response(
    advice: AILearningAdviceResponse,
) -> LearningAdviceResponse:
    return LearningAdviceResponse(
        summary=advice.summary,
        strengths=advice.strengths,
        weaknesses=advice.weaknesses,
        next_steps=advice.next_steps,
        warning=advice.warning,
    )
