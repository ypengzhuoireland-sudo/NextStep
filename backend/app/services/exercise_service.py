import json
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise as ExerciseModel
from app.models.exercise import ExerciseKnowledgeComponent
from app.models.knowledge_component import KnowledgeComponent
from app.models.student_mastery import StudentMastery
from app.schemas.exercises import (
    ExerciseDetail,
    ExerciseExample,
    ExerciseListItem,
    ExerciseListResponse,
    ExerciseRecommendation,
    KnowledgeComponentTag,
)

DEFAULT_STUDENT_ID = "s1"


def list_exercises(
    db: Session,
    kc: str | None = None,
    difficulty: str | None = None,
    status: str | None = None,
) -> ExerciseListResponse:
    statement = select(ExerciseModel).order_by(ExerciseModel.id)

    if kc is not None:
        statement = (
            statement.join(
                ExerciseKnowledgeComponent,
                ExerciseKnowledgeComponent.exercise_id == ExerciseModel.id,
            )
            .where(ExerciseKnowledgeComponent.kc_id == kc)
        )

    if difficulty is not None:
        statement = statement.where(ExerciseModel.difficulty == difficulty)

    exercises = db.scalars(statement).all()
    items = [
        to_exercise_list_item(exercise)
        for exercise in exercises
        if status is None or to_frontend_status(exercise.status) == status
    ]

    return ExerciseListResponse(items=items, total=len(items))


def get_exercise_by_id(
    db: Session,
    exercise_id: str,
    student_id: str = DEFAULT_STUDENT_ID,
) -> ExerciseDetail | None:
    exercise = db.get(ExerciseModel, exercise_id)

    if exercise is None:
        return None

    kc_tags = list_knowledge_component_tags(db, exercise.id, student_id)

    return ExerciseDetail(
        id=exercise.id,
        title=exercise.title,
        slug=slugify(exercise.title),
        difficulty=exercise.difficulty,
        estimatedMinutes=exercise.estimated_minutes,
        prompt=exercise.description,
        goal=build_goal(kc_tags),
        constraints=build_constraints(exercise),
        examples=build_examples(exercise),
        starterCode=exercise.starter_code,
        kcTags=kc_tags,
        recommendation=build_recommendation(exercise, kc_tags),
    )


def to_exercise_list_item(exercise: ExerciseModel) -> ExerciseListItem:
    return ExerciseListItem(
        id=exercise.id,
        title=exercise.title,
        difficulty=exercise.difficulty,
        primary_kc=exercise.kc_id,
        estimated_minutes=exercise.estimated_minutes,
    )


def list_knowledge_component_tags(
    db: Session,
    exercise_id: str,
    student_id: str = DEFAULT_STUDENT_ID,
) -> list[KnowledgeComponentTag]:
    statement = (
        select(KnowledgeComponent, StudentMastery.mastery)
        .join(ExerciseKnowledgeComponent, ExerciseKnowledgeComponent.kc_id == KnowledgeComponent.id)
        .outerjoin(
            StudentMastery,
            (StudentMastery.kc_id == KnowledgeComponent.id)
            & (StudentMastery.student_id == student_id),
        )
        .where(ExerciseKnowledgeComponent.exercise_id == exercise_id)
        .order_by(KnowledgeComponent.id)
    )

    rows = db.execute(statement).all()

    return [
        KnowledgeComponentTag(
            code=kc.id,
            name=kc.name,
            description=kc.description or "",
            mastery=mastery or 0.0,
            trend=0.0,
            state=mastery_state(mastery or 0.0),
        )
        for kc, mastery in rows
    ]


def build_goal(kc_tags: list[KnowledgeComponentTag]) -> str:
    if not kc_tags:
        return "Practice a focused Python programming concept."

    names = ", ".join(kc.name for kc in kc_tags[:3])
    return f"Practice {names} with a focused Python function."


def build_constraints(exercise: ExerciseModel) -> list[str]:
    constraints = [
        "Use Python 3 syntax.",
        f"Implement the function `{exercise.function_name}`.",
        "Return the result instead of printing it.",
    ]

    if exercise.hidden_tests:
        constraints.append("Hidden tests include additional edge cases.")

    return constraints


def build_examples(exercise: ExerciseModel) -> list[ExerciseExample]:
    return [
        ExerciseExample(
            input=format_function_call(exercise.function_name, test_case.get("input")),
            output=format_value(test_case.get("expected_output")),
            explanation="This sample shows one expected input/output pair.",
        )
        for test_case in exercise.test_cases[:2]
    ]


def build_recommendation(
    exercise: ExerciseModel,
    kc_tags: list[KnowledgeComponentTag],
) -> ExerciseRecommendation:
    weakest_kc = min(kc_tags, key=lambda kc: kc.mastery, default=None)

    if weakest_kc is None:
        reason = "This exercise is available for general Python practice."
    else:
        reason = (
            f"{weakest_kc.name} mastery is {weakest_kc.mastery:.2f}. "
            f"This exercise targets {weakest_kc.code} at {exercise.difficulty} difficulty."
        )

    return ExerciseRecommendation(
        strategy="lowest_mastery_with_difficulty_match",
        reason=reason,
        confidence=0.76,
    )


def to_frontend_status(status: str) -> str:
    return "draft" if status == "draft" else "published"


def mastery_state(mastery: float) -> str:
    if mastery >= 0.75:
        return "mastered"
    if mastery >= 0.6:
        return "almost_there"
    return "needs_practice"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "exercise"


def format_function_call(function_name: str, value: Any) -> str:
    if isinstance(value, dict):
        args = ", ".join(format_value(item) for item in value.values())
        return f"{function_name}({args})"

    return f"{function_name}({format_value(value)})"


def format_value(value: Any) -> str:
    if isinstance(value, str):
        return repr(value)

    return json.dumps(value, ensure_ascii=False)
