from datetime import datetime, timezone
import json
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise, ExerciseKnowledgeComponent
from app.models.knowledge_component import KnowledgeComponent
from app.models.student_mastery import StudentMastery
from app.models.submission import Submission
from app.schemas.mastery import StudentMasteryProfile
from app.schemas.practice import (
    CurrentExerciseResponse,
    DashboardSeriesPoint,
    HintMessage,
    HintRequest,
    LearningPathItem,
    PracticeSessionCreateRequest,
    PracticeSessionCreateResponse,
)
from app.schemas.sessions import UserProfile
from app.services.ai.llm_client import (
    LLMGenerationError,
    OpenAIHintService,
    create_fallback_hint,
)
from app.services.ai.schemas import (
    ExerciseContext,
    FailedTest,
    HintRequest as AIHintRequest,
    HintResponse as AIHintResponse,
    LatestResult,
)
from app.services.exercise_service import get_exercise_by_id
from app.services.mastery_service import get_student_mastery_profile, mastery_state

DEFAULT_EXPERIMENT_GROUP = "adaptive"


def create_practice_session(
    db: Session,
    request: PracticeSessionCreateRequest,
    current_user: UserProfile,
) -> PracticeSessionCreateResponse:
    student_id = resolve_student_id(current_user)
    experiment_group = request.preferred_group or DEFAULT_EXPERIMENT_GROUP

    return PracticeSessionCreateResponse(
        session_id=f"ses_{secrets.token_urlsafe(10)}",
        student_id=student_id,
        experiment_group=experiment_group,
    )


def build_current_exercise_response(
    db: Session,
    session_id: str,
    current_user: UserProfile,
) -> CurrentExerciseResponse:
    student_id = resolve_student_id(current_user)
    mastery_profile = get_student_mastery_profile(db, student_id)

    if mastery_profile is None:
        mastery_profile = StudentMasteryProfile(
            student_id=student_id,
            updated_at=datetime.now(timezone.utc).isoformat(),
            items=[],
        )

    exercise_id = choose_recommended_exercise_id(db, student_id)
    exercise = get_exercise_by_id(db, exercise_id, student_id=student_id) if exercise_id else None

    return CurrentExerciseResponse(
        sessionId=session_id,
        studentId=student_id,
        experimentGroup=DEFAULT_EXPERIMENT_GROUP,
        exercise=exercise,
        masteryProfile=mastery_profile.items,
        learningPath=build_learning_path(db, student_id),
        dashboardSeries=[
            DashboardSeriesPoint(
                label="Current",
                masteryAverage=calculate_mastery_average(mastery_profile),
            )
        ],
        latestResult=None,
        hintMessages=[],
    )


def build_hint_message(
    db: Session,
    request: HintRequest,
    current_user: UserProfile,
) -> HintMessage:
    exercise = db.get(Exercise, request.exercise_id)

    if exercise is None:
        raise ValueError("Exercise not found")

    level = min(3, max(1, request.requested_hint_level))
    student_id = resolve_student_id(current_user)
    session_id = request.session_id or "ses_demo"
    ai_request = build_ai_hint_request(db, request, exercise, student_id, level)

    try:
        ai_hint = OpenAIHintService().generate_hint(ai_request)
    except LLMGenerationError:
        ai_hint = build_static_hint_fallback(exercise, ai_request)

    return build_hint_message_from_ai_response(session_id, student_id, exercise.id, ai_hint)


def build_hint_message_from_ai_response(
    session_id: str,
    student_id: str,
    exercise_id: str,
    hint: AIHintResponse,
) -> HintMessage:
    return HintMessage(
        id=f"hint_{session_id}_{student_id}_{exercise_id}_{hint.level}",
        role="assistant",
        level=hint.level,
        title=hint.title,
        text=hint.hint_text,
        kcCode=hint.kc_code,
        createdAt=datetime.now(timezone.utc).isoformat(),
        avoid_full_solution=hint.avoid_full_solution,
    )


def build_ai_hint_request(
    db: Session,
    request: HintRequest,
    exercise: Exercise,
    student_id: str,
    level: int,
) -> AIHintRequest:
    return AIHintRequest(
        exercise=ExerciseContext(
            id=exercise.id,
            title=exercise.title,
            prompt=exercise.description,
            kc_tags=get_exercise_kc_tags(db, exercise),
            examples=build_exercise_examples(exercise),
        ),
        student_code=get_latest_student_code(db, request, student_id, exercise.id),
        latest_result=get_latest_submission_result(db, request, student_id, exercise.id),
        mastery_context=get_mastery_context(db, student_id, exercise),
        requested_hint_level=level,
    )


def build_static_hint_fallback(exercise: Exercise, request: AIHintRequest) -> AIHintResponse:
    hints = exercise.hints or []

    if hints:
        index = min(request.requested_hint_level - 1, len(hints) - 1)
        hint_text = hints[index]
    else:
        return create_fallback_hint(request)

    kc_code = request.exercise.kc_tags[0] if request.exercise.kc_tags else exercise.kc_id
    return AIHintResponse(
        level=request.requested_hint_level,
        title=f"Hint level {request.requested_hint_level}",
        hint_text=hint_text,
        next_step="Try the hint on one sample input before changing the whole solution.",
        kc_code=kc_code,
        avoid_full_solution=True,
    )


def get_exercise_kc_tags(db: Session, exercise: Exercise) -> list[str]:
    kc_tags = db.scalars(
        select(ExerciseKnowledgeComponent.kc_id)
        .where(ExerciseKnowledgeComponent.exercise_id == exercise.id)
        .order_by(ExerciseKnowledgeComponent.kc_id)
    ).all()

    return list(kc_tags) or [exercise.kc_id]


def build_exercise_examples(exercise: Exercise) -> list[dict[str, str]]:
    examples: list[dict[str, str]] = []
    for case in (exercise.test_cases or [])[:3]:
        examples.append(
            {
                "input": json.dumps(case.get("input", ""), ensure_ascii=False),
                "output": json.dumps(
                    case.get("expected_output", case.get("expected", "")),
                    ensure_ascii=False,
                ),
            }
        )
    return examples


def get_latest_student_code(
    db: Session,
    request: HintRequest,
    student_id: str,
    exercise_id: str,
) -> str:
    submission = find_submission_for_hint(db, request, student_id, exercise_id)
    return "" if submission is None else submission.code


def get_latest_submission_result(
    db: Session,
    request: HintRequest,
    student_id: str,
    exercise_id: str,
) -> LatestResult | None:
    submission = find_submission_for_hint(db, request, student_id, exercise_id)
    if submission is None:
        return None

    return LatestResult(
        passed=submission.passed,
        stderr=submission.stderr,
        failed_tests=[
            FailedTest(
                input=json.dumps(item.get("input", ""), ensure_ascii=False),
                expected=json.dumps(
                    item.get("expected", item.get("expected_output", "")),
                    ensure_ascii=False,
                ),
                actual=json.dumps(
                    item.get("actual", item.get("actual_output", "")),
                    ensure_ascii=False,
                ),
            )
            for item in submission.test_results
            if not item.get("passed", False)
        ][:3],
    )


def find_submission_for_hint(
    db: Session,
    request: HintRequest,
    student_id: str,
    exercise_id: str,
) -> Submission | None:
    submission_id = parse_submission_id(request.latest_submission_id)
    if submission_id is not None:
        return db.get(Submission, submission_id)

    return db.scalars(
        select(Submission)
        .where(
            Submission.student_id == student_id,
            Submission.exercise_id == exercise_id,
        )
        .order_by(Submission.created_at.desc(), Submission.id.desc())
    ).first()


def parse_submission_id(value: str | None) -> int | None:
    if not value:
        return None

    raw_value = value.removeprefix("sub_")
    return int(raw_value) if raw_value.isdigit() else None


def get_mastery_context(db: Session, student_id: str, exercise: Exercise) -> dict[str, float]:
    kc_tags = get_exercise_kc_tags(db, exercise)
    rows = db.execute(
        select(StudentMastery.kc_id, StudentMastery.mastery).where(
            StudentMastery.student_id == student_id,
            StudentMastery.kc_id.in_(kc_tags),
        )
    ).all()

    return {kc_id: round(mastery, 2) for kc_id, mastery in rows}


def resolve_student_id(current_user: UserProfile) -> str:
    return current_user.student_id


def choose_recommended_exercise_id(db: Session, student_id: str) -> str | None:
    weakest_mastery = db.scalar(
        select(StudentMastery)
        .where(StudentMastery.student_id == student_id)
        .order_by(StudentMastery.mastery, StudentMastery.kc_id)
    )

    if weakest_mastery is not None:
        exercise_id = db.scalar(
            select(Exercise.id)
            .join(ExerciseKnowledgeComponent, ExerciseKnowledgeComponent.exercise_id == Exercise.id)
            .where(ExerciseKnowledgeComponent.kc_id == weakest_mastery.kc_id)
            .order_by(Exercise.id)
        )

        if exercise_id is not None:
            return exercise_id

    return db.scalar(select(Exercise.id).order_by(Exercise.id))


def build_learning_path(db: Session, student_id: str) -> list[LearningPathItem]:
    rows = db.execute(
        select(
            StudentMastery.kc_id,
            KnowledgeComponent.name,
            StudentMastery.mastery,
        )
        .join(KnowledgeComponent, KnowledgeComponent.id == StudentMastery.kc_id)
        .where(StudentMastery.student_id == student_id)
        .order_by(StudentMastery.mastery, StudentMastery.kc_id)
    ).all()

    return [
        LearningPathItem(
            kcCode=kc_id,
            kcName=kc_name,
            mastery=round(mastery, 2),
            state=mastery_state(mastery),
            recommendedExerciseId=find_first_exercise_for_kc(db, kc_id),
        )
        for kc_id, kc_name, mastery in rows[:5]
    ]


def find_first_exercise_for_kc(db: Session, kc_id: str) -> str | None:
    return db.scalar(
        select(Exercise.id)
        .join(ExerciseKnowledgeComponent, ExerciseKnowledgeComponent.exercise_id == Exercise.id)
        .where(ExerciseKnowledgeComponent.kc_id == kc_id)
        .order_by(Exercise.id)
    )


def calculate_mastery_average(profile: StudentMasteryProfile) -> float:
    if not profile.items:
        return 0.0

    return round(sum(item.mastery for item in profile.items) / len(profile.items), 2)
