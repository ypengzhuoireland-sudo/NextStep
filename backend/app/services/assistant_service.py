import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.knowledge_component import KnowledgeComponent
from app.models.mastery_event import MasteryEvent
from app.models.student_mastery import StudentMastery
from app.models.submission import Submission
from app.schemas.assistant import (
    AssistantChatIntent,
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantExerciseSummary,
)
from app.services.ai.schemas import AssistantIntentResult


ELIGIBLE_EXERCISE_STATUSES = ("published", "ready")
ANSWER_REQUEST_PHRASES = (
    "answer",
    "full answer",
    "solution",
    "full solution",
    "show me the code",
    "give me the code",
    "reference code",
)
LEARNING_SUMMARY_ENGLISH_PHRASES = (
    "how am i doing",
    "learning summary",
    "my learning summary",
    "my progress",
    "study summary",
    "weak areas",
    "weakest topic",
)
LEARNING_SUMMARY_CHINESE_PHRASES = (
    "学习情况",
    "学习总结",
    "学习进度",
    "薄弱",
)
RECENT_ACTIVITY_LIMIT = 5


def build_assistant_recommendation(
    db: Session,
    student_id: str,
    request: AssistantChatRequest,
    intent_result: AssistantIntentResult,
) -> AssistantChatResponse:
    """Build the assistant response by ranking real exercises from the database."""
    mastery_by_kc = _get_mastery_by_kc(db, student_id)
    target_kc = intent_result.intent.kc_code

    # If the student asks generally, route the request to their weakest known KC.
    if target_kc is None and intent_result.intent.use_weakest_kc:
        target_kc = _get_weakest_kc(mastery_by_kc)

    # Only published or ready exercises should be shown to a learner.
    exercises = list(
        db.scalars(
            select(Exercise)
            .where(Exercise.status.in_(ELIGIBLE_EXERCISE_STATUSES))
            .order_by(Exercise.id)
        ).all()
    )
    intent = AssistantChatIntent(
        kcCode=intent_result.intent.kc_code,
        difficulty=intent_result.intent.difficulty,
        useWeakestKc=intent_result.intent.use_weakest_kc,
        source=intent_result.source,
    )

    if _is_learning_summary_request(request.message):
        return _build_learning_summary_response(db, student_id, intent)

    if _is_answer_request(request.message):
        return _build_answer_policy_response(
            db=db,
            student_id=student_id,
            current_exercise_id=request.currentExerciseId,
            exercises=exercises,
            intent=intent,
        )

    if not exercises:
        return AssistantChatResponse(
            message="I could not find another published exercise.",
            intent=intent,
            recommendedExercise=None,
            exactMatch=False,
        )

    exercises = _exclude_current_when_possible(
        exercises,
        request.currentExerciseId,
    )

    named_match = _find_named_exercise(exercises, request.message)
    if named_match is not None:
        selected = named_match
        exact_match = True
        message = "This exercise matches the specific exercise you requested."
    else:
        selected = min(
            exercises,
            key=lambda exercise: (
                -_score_exercise(
                    exercise,
                    target_kc,
                    intent_result.intent.difficulty,
                    mastery_by_kc,
                ),
                exercise.id,
            ),
        )
        exact_match = (
            (target_kc is None or selected.kc_id == target_kc)
            and (
                intent_result.intent.difficulty is None
                or selected.difficulty == intent_result.intent.difficulty
            )
        )
        message = _build_message(
            selected,
            target_kc,
            intent_result.intent.difficulty,
            exact_match,
        )

    return AssistantChatResponse(
        message=message,
        intent=intent,
        recommendedExercise=AssistantExerciseSummary(
            id=selected.id,
            title=selected.title,
            difficulty=selected.difficulty,
            primaryKc=selected.kc_id,
            estimatedMinutes=selected.estimated_minutes,
            status="published",
        ),
        exactMatch=exact_match,
    )


def _is_answer_request(message: str) -> bool:
    """Detect requests where the learner is asking for code or a solution."""
    normalized_message = _normalize_lookup_text(message)
    return any(
        _contains_lookup_phrase(normalized_message, phrase)
        for phrase in ANSWER_REQUEST_PHRASES
    )


def _is_learning_summary_request(message: str) -> bool:
    """Detect requests where the learner asks about their overall progress."""
    lowered_message = message.lower()
    if any(phrase in lowered_message for phrase in LEARNING_SUMMARY_CHINESE_PHRASES):
        return True

    normalized_message = _normalize_lookup_text(message)
    return any(
        _contains_lookup_phrase(normalized_message, phrase)
        for phrase in LEARNING_SUMMARY_ENGLISH_PHRASES
    )


def _build_learning_summary_response(
    db: Session,
    student_id: str,
    intent: AssistantChatIntent,
) -> AssistantChatResponse:
    """Build a deterministic learning summary from mastery and submission data."""
    mastery_rows = _get_mastery_summary_rows(db, student_id)
    recent_submissions = _get_recent_submission_rows(db, student_id)
    recent_events = _get_recent_mastery_event_rows(db, student_id)

    if not mastery_rows and not recent_submissions:
        message = (
            "Learning Summary\n\n"
            "I do not have enough practice data yet. Run or submit a few "
            "exercises first, then I can summarise your strengths, weak areas, "
            "and next focus."
        )
    else:
        message = _format_learning_summary(
            mastery_rows,
            recent_submissions,
            recent_events,
        )

    return AssistantChatResponse(
        message=message,
        intent=intent,
        recommendedExercise=None,
        exactMatch=True,
    )


def _get_mastery_summary_rows(
    db: Session,
    student_id: str,
) -> list[tuple[str, str, float]]:
    """Load KC names and mastery values for the student's summary."""
    rows = db.execute(
        select(StudentMastery.kc_id, KnowledgeComponent.name, StudentMastery.mastery)
        .join(KnowledgeComponent, KnowledgeComponent.id == StudentMastery.kc_id)
        .where(StudentMastery.student_id == student_id)
        .order_by(StudentMastery.mastery.desc(), StudentMastery.kc_id)
    ).all()
    return [(kc_id, name, mastery) for kc_id, name, mastery in rows]


def _get_recent_submission_rows(
    db: Session,
    student_id: str,
) -> list[tuple[Submission, str]]:
    """Load the latest submissions with exercise titles for progress text."""
    rows = db.execute(
        select(Submission, Exercise.title)
        .join(Exercise, Exercise.id == Submission.exercise_id)
        .where(Submission.student_id == student_id)
        .order_by(Submission.id.desc())
        .limit(RECENT_ACTIVITY_LIMIT)
    ).all()
    return [(submission, title) for submission, title in rows]


def _get_recent_mastery_event_rows(
    db: Session,
    student_id: str,
) -> list[tuple[str, float, float]]:
    """Load recent mastery changes so the summary can mention improvement."""
    rows = db.execute(
        select(
            KnowledgeComponent.name,
            MasteryEvent.old_mastery,
            MasteryEvent.new_mastery,
        )
        .join(KnowledgeComponent, KnowledgeComponent.id == MasteryEvent.kc_id)
        .where(MasteryEvent.student_id == student_id)
        .order_by(MasteryEvent.id.desc())
        .limit(RECENT_ACTIVITY_LIMIT)
    ).all()
    return [(name, old_mastery, new_mastery) for name, old_mastery, new_mastery in rows]


def _format_learning_summary(
    mastery_rows: list[tuple[str, str, float]],
    recent_submissions: list[tuple[Submission, str]],
    recent_events: list[tuple[str, float, float]],
) -> str:
    """Format the learning summary into stable sections for the chat panel."""
    strong_rows = mastery_rows[:2]
    weak_rows = sorted(mastery_rows, key=lambda row: (row[2], row[0]))[:3]
    passed_count = sum(1 for submission, _ in recent_submissions if submission.passed)
    recent_titles = [title for _, title in recent_submissions[:3]]
    improved_rows = [
        (name, new_mastery - old_mastery)
        for name, old_mastery, new_mastery in recent_events
        if new_mastery > old_mastery
    ]
    next_focus = weak_rows[0][1] if weak_rows else "the next recommended exercise"

    return "\n".join(
        [
            "Learning Summary",
            "",
            "Strong areas:",
            *_format_mastery_bullets(strong_rows, "No strong area yet."),
            "",
            "Weak areas:",
            *_format_mastery_bullets(weak_rows, "No weak area detected yet."),
            "",
            "Recent progress:",
            _format_recent_submission_line(recent_submissions, passed_count),
            _format_recent_titles_line(recent_titles),
            _format_recent_improvement_line(improved_rows),
            "",
            "Next focus:",
            f"- Practise {next_focus} next.",
        ]
    )


def _format_mastery_bullets(
    rows: list[tuple[str, str, float]],
    empty_message: str,
) -> list[str]:
    """Convert mastery rows into percent bullets."""
    if not rows:
        return [f"- {empty_message}"]
    return [f"- {name}: {_format_percent(mastery)}" for _, name, mastery in rows]


def _format_recent_submission_line(
    recent_submissions: list[tuple[Submission, str]],
    passed_count: int,
) -> str:
    """Summarise recent pass rate from stored submissions."""
    total = len(recent_submissions)
    if total == 0:
        return "- No recent submissions yet."
    return f"- {passed_count}/{total} recent submissions passed."


def _format_recent_titles_line(recent_titles: list[str]) -> str:
    """Mention a few recent exercises without making the summary too long."""
    if not recent_titles:
        return "- Recent exercises: none yet."
    return f"- Recent exercises: {', '.join(recent_titles)}."


def _format_recent_improvement_line(
    improved_rows: list[tuple[str, float]],
) -> str:
    """Mention the latest KC with positive mastery movement."""
    if not improved_rows:
        return "- Recent mastery movement: no increase recorded yet."
    name, delta = improved_rows[0]
    return f"- Recent mastery movement: {name} increased by {_format_percent(delta)}."


def _format_percent(value: float) -> str:
    """Display a mastery value as a whole-number percentage."""
    return f"{round(value * 100)}%"


def _build_answer_policy_response(
    db: Session,
    student_id: str,
    current_exercise_id: str | None,
    exercises: list[Exercise],
    intent: AssistantChatIntent,
) -> AssistantChatResponse:
    """Apply the progressive answer policy before normal recommendation."""
    exercise = _find_exercise_by_id(exercises, current_exercise_id)
    if exercise is None:
        return AssistantChatResponse(
            message=(
                "I can help with the current exercise, but I could not find "
                "which exercise is open. Please open an exercise and try again."
            ),
            intent=intent,
            recommendedExercise=None,
            exactMatch=False,
        )

    if not _has_submitted_attempt(db, student_id, exercise.id):
        return AssistantChatResponse(
            message=_build_pseudocode_message(exercise),
            intent=intent,
            recommendedExercise=None,
            exactMatch=True,
        )

    return AssistantChatResponse(
        message=_build_review_mode_message(exercise),
        intent=intent,
        recommendedExercise=None,
        exactMatch=True,
    )


def _find_exercise_by_id(
    exercises: list[Exercise],
    exercise_id: str | None,
) -> Exercise | None:
    """Find the currently open exercise inside the eligible exercise list."""
    if not exercise_id:
        return None
    return next(
        (exercise for exercise in exercises if exercise.id == exercise_id),
        None,
    )


def _has_submitted_attempt(
    db: Session,
    student_id: str,
    exercise_id: str,
) -> bool:
    """Check whether the learner has already submitted the current exercise."""
    submission_id = db.scalar(
        select(Submission.id)
        .where(
            Submission.student_id == student_id,
            Submission.exercise_id == exercise_id,
        )
        .limit(1)
    )
    return submission_id is not None


def _build_pseudocode_message(exercise: Exercise) -> str:
    """Give guidance without revealing the full reference solution."""
    pseudocode_lines = [
        _build_pseudocode_signature(exercise),
        *_build_pseudocode_steps(exercise),
        "END FUNCTION",
    ]
    return (
        "I cannot show the full code before you submit an attempt. "
        "Here is pseudocode to guide you:\n\n"
        "```text\n"
        f"{chr(10).join(pseudocode_lines)}\n"
        "```\n\n"
        "Submit your attempt first. After that, Review Mode can show "
        "reference code for comparison."
    )


def _build_pseudocode_signature(exercise: Exercise) -> str:
    """Create a language-neutral function header from the starter code."""
    signature_match = re.search(
        r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\)",
        exercise.starter_code or "",
    )
    if signature_match:
        function_name = signature_match.group(1)
        parameters = signature_match.group(2)
    else:
        function_name = exercise.function_name or "solution"
        parameters = "input"
    return f"FUNCTION {function_name}({parameters})"


def _build_pseudocode_steps(exercise: Exercise) -> list[str]:
    """Convert stored exercise hints into pseudocode-style algorithm steps."""
    hints = [
        str(hint).strip().rstrip(".")
        for hint in (exercise.hints or [])
        if str(hint).strip()
    ]
    if hints:
        return [f"    {hint.upper()}" for hint in hints]
    return [
        "    READ THE INPUTS",
        "    HANDLE ANY EMPTY OR SPECIAL CASE",
        "    BUILD THE RESULT STEP BY STEP",
        "    RETURN THE FINAL RESULT",
    ]


def _build_review_mode_message(exercise: Exercise) -> str:
    """Show the reference solution only after a submission exists."""
    if not exercise.solution:
        return (
            "Review Mode: you have submitted an attempt, but this exercise "
            "does not have a reference solution stored yet."
        )
    return (
        "Review Mode: reference solution shown after your submitted attempt. "
        "Use this to compare your approach, not as a first answer.\n\n"
        f"```python\n{exercise.solution.strip()}\n```"
    )


def _get_mastery_by_kc(db: Session, student_id: str) -> dict[str, float]:
    """Load the student's latest mastery value for each KC."""
    rows = db.execute(
        select(StudentMastery.kc_id, StudentMastery.mastery)
        .where(StudentMastery.student_id == student_id)
        .order_by(StudentMastery.kc_id)
    ).all()
    return {kc_id: mastery for kc_id, mastery in rows}


def _get_weakest_kc(mastery_by_kc: dict[str, float]) -> str | None:
    """Choose the lowest mastery KC with a stable tie break by KC code."""
    if not mastery_by_kc:
        return None
    return min(mastery_by_kc, key=lambda code: (mastery_by_kc[code], code))


def _exclude_current_when_possible(
    exercises: list[Exercise],
    current_exercise_id: str | None,
) -> list[Exercise]:
    """Remove the current exercise unless it is the only available option."""
    if not current_exercise_id:
        return exercises
    alternatives = [
        exercise for exercise in exercises if exercise.id != current_exercise_id
    ]
    return alternatives or exercises


def _find_named_exercise(
    exercises: list[Exercise],
    message: str,
) -> Exercise | None:
    """Prefer an exercise explicitly named by id, title, or function name."""
    normalized_message = _normalize_lookup_text(message)

    for exercise in exercises:
        candidates = (
            exercise.id,
            exercise.title,
            exercise.function_name,
        )
        if any(
            _contains_lookup_phrase(normalized_message, candidate)
            for candidate in candidates
            if candidate
        ):
            return exercise

    return None


def _score_exercise(
    exercise: Exercise,
    target_kc: str | None,
    difficulty: str | None,
    mastery_by_kc: dict[str, float],
) -> float:
    """Score exercises by requested topic, difficulty, then weaker mastery."""
    score = 0.0
    if target_kc and exercise.kc_id == target_kc:
        score += 100.0
    if difficulty and exercise.difficulty == difficulty:
        score += 30.0
    score += (1.0 - mastery_by_kc.get(exercise.kc_id, 0.0)) * 10.0
    return score


def _build_message(
    exercise: Exercise,
    target_kc: str | None,
    difficulty: str | None,
    exact_match: bool,
) -> str:
    """Create a short learner-facing reason for the chosen exercise."""
    if not exact_match:
        return (
            "I could not find an exact match, so I selected the closest "
            "available exercise."
        )
    if target_kc and difficulty:
        return (
            f"This {exercise.difficulty} exercise matches the topic and "
            "difficulty you requested."
        )
    if target_kc:
        return "This exercise matches the topic you requested."
    return "This exercise targets one of your lowest-mastery knowledge areas."


def _normalize_lookup_text(value: str) -> str:
    """Normalize ids, titles, and function names for user-message matching."""
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _contains_lookup_phrase(message: str, candidate: str) -> bool:
    """Match complete normalized exercise names instead of loose substrings."""
    normalized_candidate = _normalize_lookup_text(candidate)
    if not normalized_candidate:
        return False
    return f" {normalized_candidate} " in f" {message} "
