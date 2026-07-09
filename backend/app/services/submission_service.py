from __future__ import annotations

import json
from typing import Any

from datetime import timezone

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import KnowledgeComponent, User
from app.models.exercise import Exercise, ExerciseKnowledgeComponent
from app.models.mastery_event import MasteryEvent
from app.models.student_mastery import StudentMastery
from app.models.submission import Submission
from app.schemas.executions import ExecutionRunRequest, MasteryDelta
from app.schemas.submissions import (
    SubmissionCreateRequest,
    SubmissionResponse,
    SubmissionRecord,
)
from app.services.execution_service import (
    build_execution_response_from_test_cases,
    build_judge0_payload,
    submit_to_judge0,
)
from app.services.mastery_service import get_student_mastery_profile
from app.services.bkt_service import (
    INITIAL_STUDENT_MASTERY,
    get_bkt_parameters_for_kc,
    update_knowledge_state,
)
from app.services.test_harness import (
    build_python_test_runner_code,
    calculate_score as calculate_runner_score,
    parse_runner_stdout as parse_contract_runner_stdout,
)

_MODEL_IMPORTS = (KnowledgeComponent, User)


# Coordinate the complete submission flow from exercise lookup to recommendation.
def create_submission(
    db: Session,
    student_id: str,
    request: SubmissionCreateRequest,
) -> SubmissionResponse:
    exercise = db.get(Exercise, request.exercise_id)

    if exercise is None:
        raise ValueError("Exercise not found")

    runner_code = build_python_test_runner_code(
        student_code=request.code,
        function_name=exercise.function_name,
        test_cases=exercise.test_cases,
    )
    runner_request = ExecutionRunRequest(code=runner_code, language=request.language)
    response_data = submit_to_judge0(build_judge0_payload(runner_request))
    test_results = parse_contract_runner_stdout(response_data.get("stdout") or "")
    score = calculate_runner_score(test_results)
    result = build_execution_response_from_test_cases(response_data, test_results)
    passed = bool(test_results) and score == 1.0 and result.status == "passed"
    mastery_delta = update_mastery_for_submission(db, student_id, exercise.id, passed)
    result.masteryDelta = mastery_delta

    submission = Submission(
        student_id=student_id,
        exercise_id=exercise.id,
        code=request.code,
        language=request.language,
        status=result.status,
        passed=passed,
        score=score,
        stdout=result.stdout,
        stderr=result.stderr,
        test_results=[item.model_dump() for item in result.testCases],
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    attempt_count = count_attempts(db, student_id, exercise.id)
    mastery_profile = get_student_mastery_profile(db, student_id)

    return SubmissionResponse(
        submission=SubmissionRecord(
            id=f"sub_{submission.id}",
            status=result.status,
            correct=passed,
            attempt_count=attempt_count,
            created_at=submission.created_at.astimezone(timezone.utc).isoformat(),
        ),
        result=result,
        masteryProfile=[] if mastery_profile is None else mastery_profile.items,
    )


# Wrap the student's function with a test harness so one Judge0 request runs every case.
def build_submission_runner_code(
    student_code: str,
    function_name: str,
    test_cases: list[dict[str, Any]],
) -> str:
    return build_python_test_runner_code(student_code, function_name, test_cases)


# Convert the JSON printed by the generated test harness into typed test results.
class LegacySubmissionTestResult(BaseModel):
    name: str
    passed: bool
    input: Any
    expected_output: Any
    actual_output: Any = None
    error: str = ""


def parse_runner_stdout(stdout: str) -> list[LegacySubmissionTestResult]:
    return [
        LegacySubmissionTestResult(
            name=str(item.get("label") or item.get("name") or ""),
            passed=bool(item.get("passed")),
            input=item.get("input"),
            expected_output=item.get("expected", item.get("expected_output")),
            actual_output=item.get("actual", item.get("actual_output")),
            error=item.get("error") or "",
        )
        for item in parse_contract_runner_stdout(stdout)
    ]


# Calculate a score between 0 and 1 from the number of passed test cases.
def calculate_score(test_results: list[LegacySubmissionTestResult]) -> float:
    if not test_results:
        return 0.0

    passed_count = sum(1 for result in test_results if result.passed)
    return round(passed_count / len(test_results), 2)


# Increase or decrease mastery for every KC associated with the submitted exercise.
def update_mastery_for_submission(
    db: Session,
    student_id: str,
    exercise_id: str,
    passed: bool,
) -> list[MasteryDelta]:
    kc_ids = db.scalars(
        select(ExerciseKnowledgeComponent.kc_id).where(
            ExerciseKnowledgeComponent.exercise_id == exercise_id,
        )
    ).all()
    mastery_delta: list[MasteryDelta] = []
    attempt_no = count_attempts(db, student_id, exercise_id) + 1

    for kc_id in kc_ids:
        params = get_bkt_parameters_for_kc(db, kc_id)
        mastery = db.get(StudentMastery, (student_id, kc_id))

        if mastery is None:
            mastery = StudentMastery(
                student_id=student_id,
                kc_id=kc_id,
                mastery=INITIAL_STUDENT_MASTERY,
            )
            db.add(mastery)

        before = mastery.mastery
        mastery.mastery = update_knowledge_state(before, correct=passed, params=params)
        db.add(
            MasteryEvent(
                student_id=student_id,
                exercise_id=exercise_id,
                kc_id=kc_id,
                old_mastery=before,
                new_mastery=mastery.mastery,
                correct=passed,
                attempt_no=attempt_no,
                bkt_prior=params.prior,
                bkt_learn=params.learn,
                bkt_guess=params.guess,
                bkt_slip=params.slip,
            )
        )
        mastery_delta.append(
            MasteryDelta(
                kcCode=kc_id,
                before=before,
                after=mastery.mastery,
            )
        )

    return mastery_delta


# Recommend the first exercise linked to the student's current weakest KC.
def choose_next_exercise_id(db: Session, student_id: str) -> str | None:
    weakest = db.scalars(
        select(StudentMastery).where(StudentMastery.student_id == student_id).order_by(
            StudentMastery.mastery,
            StudentMastery.kc_id,
        )
    ).first()

    if weakest is None:
        return None

    return db.scalars(
        select(Exercise.id)
        .join(ExerciseKnowledgeComponent, ExerciseKnowledgeComponent.exercise_id == Exercise.id)
        .where(ExerciseKnowledgeComponent.kc_id == weakest.kc_id)
        .order_by(Exercise.id)
    ).first()


def count_attempts(db: Session, student_id: str, exercise_id: str) -> int:
    return int(
        db.scalar(
            select(func.count(Submission.id)).where(
                Submission.student_id == student_id,
                Submission.exercise_id == exercise_id,
            )
        )
        or 0
    )
