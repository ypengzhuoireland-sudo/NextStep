from datetime import datetime, timezone
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise, ExerciseKnowledgeComponent
from app.models.knowledge_component import KnowledgeComponent
from app.models.student_mastery import StudentMastery
from app.models.user import User
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
from app.services.exercise_service import get_exercise_by_id
from app.services.mastery_service import get_student_mastery_profile, mastery_state

DEFAULT_STUDENT_ID = "s1"
DEFAULT_EXPERIMENT_GROUP = "adaptive"


def create_practice_session(
    db: Session,
    request: PracticeSessionCreateRequest,
    current_user: UserProfile | None = None,
) -> PracticeSessionCreateResponse:
    student_id = resolve_student_id(db, current_user)
    experiment_group = request.preferred_group or DEFAULT_EXPERIMENT_GROUP

    return PracticeSessionCreateResponse(
        session_id=f"ses_{secrets.token_urlsafe(10)}",
        student_id=student_id,
        experiment_group=experiment_group,
    )


def build_current_exercise_response(
    db: Session,
    session_id: str,
    current_user: UserProfile | None = None,
) -> CurrentExerciseResponse:
    student_id = resolve_student_id(db, current_user)
    mastery_profile = get_student_mastery_profile(db, student_id)

    if mastery_profile is None:
        mastery_profile = StudentMasteryProfile(
            studentId=student_id,
            updatedAt=datetime.now(timezone.utc).isoformat(),
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
    current_user: UserProfile | None = None,
) -> HintMessage:
    exercise = db.get(Exercise, request.exercise_id)

    if exercise is None:
        raise ValueError("Exercise not found")

    level = max(1, request.requested_hint_level)
    hints = exercise.hints or []

    if hints:
        index = min(level - 1, len(hints) - 1)
        text = hints[index]
    else:
        text = (
            f"Focus on the function `{exercise.function_name}` and compare your return value "
            "with the examples before changing the whole solution."
        )

    student_id = request.student_id or resolve_student_id(db, current_user)
    session_id = request.session_id or "ses_demo"

    return HintMessage(
        id=f"hint_{session_id}_{student_id}_{exercise.id}_{level}",
        role="assistant",
        level=level,
        title=f"Hint level {level}",
        text=text,
        kcCode=exercise.kc_id,
        createdAt=datetime.now(timezone.utc).isoformat(),
        avoid_full_solution=True,
    )


def resolve_student_id(db: Session, current_user: UserProfile | None = None) -> str:
    if current_user is not None:
        return current_user.student_id

    default_user = db.scalar(select(User).where(User.student_id == DEFAULT_STUDENT_ID))

    if default_user is not None:
        return DEFAULT_STUDENT_ID

    first_user = db.scalar(select(User).where(User.is_active.is_(True)).order_by(User.student_id))

    return first_user.student_id if first_user is not None else DEFAULT_STUDENT_ID


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
