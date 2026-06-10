from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import KnowledgeComponent, User
from app.models.exercise import Exercise, ExerciseKnowledgeComponent
from app.models.student_mastery import StudentMastery
from app.models.submission import Submission
from app.schemas.executions import ExecutionRunRequest
from app.schemas.submissions import (
    SubmissionCreateRequest,
    SubmissionResponse,
    SubmissionTestResult,
)
from app.services.execution_service import run_code_with_judge0

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

    runner_code = build_submission_runner_code(
        student_code=request.code,
        function_name=exercise.function_name,
        test_cases=exercise.test_cases,
    )
    execution_result = run_code_with_judge0(
        ExecutionRunRequest(code=runner_code, language=request.language),
    )
    test_results = parse_runner_stdout(execution_result.stdout)
    score = calculate_score(test_results)
    passed = bool(test_results) and score == 1.0 and execution_result.passed
    updated_mastery = update_mastery_for_submission(db, student_id, exercise.id, passed)

    submission = Submission(
        student_id=student_id,
        exercise_id=exercise.id,
        code=request.code,
        language=request.language,
        status=execution_result.status_description,
        passed=passed,
        score=score,
        stdout=execution_result.stdout,
        stderr=execution_result.stderr or execution_result.compile_output or execution_result.message,
        test_results=[result.model_dump() for result in test_results],
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return SubmissionResponse(
        submission_id=submission.id,
        exercise_id=exercise.id,
        passed=passed,
        score=score,
        stdout=execution_result.stdout,
        stderr=submission.stderr,
        status_description=execution_result.status_description,
        test_results=test_results,
        updated_mastery=updated_mastery,
        recommended_exercise_id=choose_next_exercise_id(db, student_id),
    )


# Wrap the student's function with a test harness so one Judge0 request runs every case.
def build_submission_runner_code(
    student_code: str,
    function_name: str,
    test_cases: list[dict[str, Any]],
) -> str:
    test_cases_json = json.dumps(test_cases, ensure_ascii=False)

    return (
        f"{student_code}\n\n"
        "import json\n"
        "import traceback\n\n"
        "def __nextstep_run_tests():\n"
        f"    test_cases = {test_cases_json}\n"
        "    results = []\n"
        "    for index, test_case in enumerate(test_cases, start=1):\n"
        "        test_input = test_case.get('input')\n"
        "        expected = test_case.get('expected_output')\n"
        "        actual = None\n"
        "        error = ''\n"
        "        passed = False\n"
        "        try:\n"
        "            if isinstance(test_input, dict):\n"
        f"                actual = {function_name}(**test_input)\n"
        "            elif isinstance(test_input, list):\n"
        f"                actual = {function_name}(*test_input)\n"
        "            else:\n"
        f"                actual = {function_name}(test_input)\n"
        "            passed = actual == expected\n"
        "        except Exception:\n"
        "            error = traceback.format_exc()\n"
        "        results.append({\n"
        "            'name': f'case {index}',\n"
        "            'passed': passed,\n"
        "            'input': test_input,\n"
        "            'expected_output': expected,\n"
        "            'actual_output': actual,\n"
        "            'error': error,\n"
        "        })\n"
        "    print(json.dumps({'results': results}, ensure_ascii=False))\n\n"
        "__nextstep_run_tests()\n"
    )


# Convert the JSON printed by the generated test harness into typed test results.
def parse_runner_stdout(stdout: str) -> list[SubmissionTestResult]:
    try:
        payload = json.loads(stdout.strip())
    except json.JSONDecodeError:
        return []

    return [
        SubmissionTestResult(
            name=item.get("name", ""),
            passed=bool(item.get("passed")),
            input=item.get("input"),
            expected_output=item.get("expected_output"),
            actual_output=item.get("actual_output"),
            error=item.get("error") or "",
        )
        for item in payload.get("results", [])
    ]


# Calculate a score between 0 and 1 from the number of passed test cases.
def calculate_score(test_results: list[SubmissionTestResult]) -> float:
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
) -> dict[str, float]:
    kc_ids = db.scalars(
        select(ExerciseKnowledgeComponent.kc_id).where(
            ExerciseKnowledgeComponent.exercise_id == exercise_id,
        )
    ).all()
    updated_mastery: dict[str, float] = {}

    for kc_id in kc_ids:
        mastery = db.get(StudentMastery, (student_id, kc_id))

        if mastery is None:
            mastery = StudentMastery(student_id=student_id, kc_id=kc_id, mastery=0.0)
            db.add(mastery)

        delta = 0.08 if passed else -0.04
        mastery.mastery = max(0.0, min(1.0, round(mastery.mastery + delta, 2)))
        updated_mastery[kc_id] = mastery.mastery

    return updated_mastery


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
