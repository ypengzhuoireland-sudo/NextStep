from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from sqlalchemy import case, select
from sqlalchemy.orm import Session

from app.models.diagnostic_attempt import DiagnosticAttempt
from app.models.exercise import Exercise, ExerciseKnowledgeComponent
from app.models.knowledge_component import KnowledgeComponent
from app.models.student_mastery import StudentMastery
from app.models.user import User
from app.schemas.diagnostic import (
    DiagnosticAnswer,
    DiagnosticExerciseRecommendation,
    DiagnosticKcResult,
    DiagnosticOption,
    DiagnosticQuestion,
    DiagnosticQuestionResponse,
    DiagnosticResultResponse,
)

QUESTION_BANK_PATH = Path(__file__).resolve().parents[2] / "seeds" / "diagnostic_question_bank.json"
QUESTIONS_PER_KC = 2
MAX_DIAGNOSTIC_MASTERY = 0.60


class DiagnosticValidationError(ValueError):
    pass


class DiagnosticAlreadyCompletedError(ValueError):
    pass


@lru_cache(maxsize=1)
def load_question_bank() -> tuple[dict[str, Any], ...]:
    with open(QUESTION_BANK_PATH, "r", encoding="utf-8") as file:
        questions = json.load(file)

    ids = [question["id"] for question in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("Diagnostic question ids must be unique")

    counts: dict[str, int] = defaultdict(int)
    for question in questions:
        counts[question["kc_id"]] += 1
        option_ids = {option["id"] for option in question["options"]}
        if question["correct_option_id"] not in option_ids:
            raise ValueError(f"Question {question['id']} has an invalid correct option")

    if len(counts) != 12 or any(count != QUESTIONS_PER_KC for count in counts.values()):
        raise ValueError("Diagnostic bank must contain two questions for each of the 12 KCs")

    return tuple(questions)


def get_diagnostic_questions() -> DiagnosticQuestionResponse:
    questions = [
        DiagnosticQuestion(
            id=item["id"],
            kcId=item["kc_id"],
            kcName=item["kc_name"],
            prompt=item["prompt"],
            code=item.get("code"),
            options=[DiagnosticOption(**option) for option in item["options"]],
        )
        for item in load_question_bank()
    ]
    return DiagnosticQuestionResponse(
        questions=questions,
        totalQuestions=len(questions),
        estimatedMinutes=18,
    )


def submit_diagnostic(
    db: Session,
    user: User,
    answers: list[DiagnosticAnswer],
) -> DiagnosticResultResponse:
    if user.diagnostic_completed:
        raise DiagnosticAlreadyCompletedError("Diagnostic test has already been completed")

    questions = load_question_bank()
    answer_map = {answer.questionId: answer.selectedOptionId for answer in answers}
    expected_ids = {question["id"] for question in questions}

    if len(answers) != len(answer_map):
        raise DiagnosticValidationError("Each diagnostic question can only be answered once")
    if set(answer_map) != expected_ids:
        raise DiagnosticValidationError("Every diagnostic question must be answered")

    correct_by_kc: dict[str, int] = defaultdict(int)
    total_by_kc: dict[str, int] = defaultdict(int)
    total_correct = 0

    for question in questions:
        selected_option = answer_map[question["id"]]
        valid_options = {option["id"] for option in question["options"]}
        if selected_option not in valid_options:
            raise DiagnosticValidationError(f"Invalid option for question {question['id']}")

        kc_id = question["kc_id"]
        total_by_kc[kc_id] += 1
        if selected_option == question["correct_option_id"]:
            correct_by_kc[kc_id] += 1
            total_correct += 1

    kc_names = {question["kc_id"]: question["kc_name"] for question in questions}
    kc_order = list(dict.fromkeys(question["kc_id"] for question in questions))
    kc_results: list[DiagnosticKcResult] = []

    for kc_id in kc_order:
        correct = correct_by_kc[kc_id]
        total = total_by_kc[kc_id]
        accuracy = correct / total
        mastery = round(accuracy * MAX_DIAGNOSTIC_MASTERY, 4)
        result = DiagnosticKcResult(
            kcId=kc_id,
            kcName=kc_names[kc_id],
            correct=correct,
            total=total,
            accuracy=round(accuracy, 4),
            mastery=mastery,
            level=diagnostic_level(mastery),
        )
        kc_results.append(result)
        mastery_row = db.get(StudentMastery, (user.student_id, kc_id))
        if mastery_row is None:
            db.add(StudentMastery(student_id=user.student_id, kc_id=kc_id, mastery=mastery))
        else:
            mastery_row.mastery = mastery

    ranked_results = sorted(kc_results, key=lambda item: (item.mastery, item.kcId))
    recommendations = build_recommendations(db, ranked_results[:3])
    overall_score = round(total_correct / len(questions), 4)

    db.add(
        DiagnosticAttempt(
            student_id=user.student_id,
            answers=[answer.model_dump() for answer in answers],
            kc_results=[result.model_dump() for result in kc_results],
            overall_score=overall_score,
        )
    )
    user.diagnostic_completed = True
    user.diagnostic_completed_at = datetime.now(timezone.utc)
    db.commit()

    return DiagnosticResultResponse(
        totalQuestions=len(questions),
        correctAnswers=total_correct,
        overallScore=overall_score,
        kcResults=kc_results,
        strengths=[item.kcName for item in kc_results if item.level == "strength"],
        weaknesses=[item.kcName for item in kc_results if item.level == "weakness"],
        recommendations=recommendations,
    )


def diagnostic_level(mastery: float) -> str:
    if mastery >= 0.60:
        return "strength"
    if mastery <= 0.15:
        return "weakness"
    return "developing"


def build_recommendations(
    db: Session,
    results: list[DiagnosticKcResult],
) -> list[DiagnosticExerciseRecommendation]:
    difficulty_order = case(
        (Exercise.difficulty == "easy", 0),
        (Exercise.difficulty == "medium", 1),
        else_=2,
    )
    recommendations: list[DiagnosticExerciseRecommendation] = []

    for result in results:
        exercise = db.scalars(
            select(Exercise)
            .join(
                ExerciseKnowledgeComponent,
                ExerciseKnowledgeComponent.exercise_id == Exercise.id,
            )
            .where(
                ExerciseKnowledgeComponent.kc_id == result.kcId,
                Exercise.status.in_(("ready", "published", "recommended")),
            )
            .order_by(difficulty_order, Exercise.id)
        ).first()
        if exercise is None:
            continue

        recommendations.append(
            DiagnosticExerciseRecommendation(
                kcId=result.kcId,
                kcName=result.kcName,
                exerciseId=exercise.id,
                exerciseTitle=exercise.title,
                difficulty=exercise.difficulty,
                reason=(
                    f"Your diagnostic mastery for {result.kcName} is "
                    f"{round(result.mastery * 100)}%, so this is a focused starting exercise."
                ),
            )
        )

    return recommendations
