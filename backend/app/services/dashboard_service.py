from datetime import datetime, timezone
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise as ExerciseModel
from app.models.knowledge_component import KnowledgeComponent as KnowledgeComponentModel
from app.models.student_mastery import StudentMastery
from app.models.user import User
from app.schemas.dashboard import (
    ClassDashboardSummary,
    ClassHeatmapCell,
    DashboardResponse,
    DashboardTotals,
    Exercise,
    KnowledgeComponent,
    RiskStudent,
    WeakKcSummary,
)
from app.schemas.sessions import UserProfile
from app.services.exercise_service import to_frontend_status
from app.services.mastery_service import mastery_state
from app.services.recommendation_service import choose_recommended_exercise


# Build the dashboard response using the authenticated user and PostgreSQL data.
def build_dashboard_response(db: Session, current_user: UserProfile) -> DashboardResponse:
    kcs = list_dashboard_mastery(db, current_user.student_id)
    exercises = list_dashboard_exercises(db)
    mastery_average = round(sum(kc.mastery for kc in kcs) / len(kcs), 2) if kcs else 0.0
    recommended = choose_recommended_exercise(exercises)
    recommended_exercise_id = recommended.id if recommended is not None else ""
    active_goal = "Practice weak Python concepts"
    backend_status = "connected"
    learning_path = sorted(kcs, key=lambda kc: kc.mastery)[:5]

    return DashboardResponse(
        studentId=current_user.student_id,
        studentName=current_user.name,
        activeGoal=active_goal,
        backendStatus=backend_status,
        masteryAverage=mastery_average,
        recommendedExerciseId=recommended_exercise_id,
        recommendedExercise=recommended,
        masteryProfile=kcs,
        learningPath=learning_path,
    )


# Read the current student's KC mastery values from PostgreSQL.
def list_dashboard_mastery(db: Session, student_id: str) -> list[KnowledgeComponent]:
    rows = db.execute(
        select(
            KnowledgeComponentModel.id,
            KnowledgeComponentModel.name,
            KnowledgeComponentModel.description,
            StudentMastery.mastery,
        )
        .join(StudentMastery, StudentMastery.kc_id == KnowledgeComponentModel.id)
        .where(StudentMastery.student_id == student_id)
        .order_by(KnowledgeComponentModel.id)
    ).all()

    return [
        KnowledgeComponent(
            id=row.id,
            code=row.id,
            name=row.name,
            description=row.description or "",
            mastery=row.mastery,
            trend=0.0,
            state=mastery_state(row.mastery),
        )
        for row in rows
    ]


# Read exercise summaries from PostgreSQL for the dashboard queue.
def list_dashboard_exercises(db: Session) -> list[Exercise]:
    exercises = db.scalars(select(ExerciseModel).order_by(ExerciseModel.id)).all()

    return [
        Exercise(
            id=exercise.id,
            title=exercise.title,
            kc=exercise.kc_id,
            primaryKc=exercise.kc_id,
            difficulty=exercise.difficulty,
            estimatedMinutes=exercise.estimated_minutes,
            status=to_frontend_status(exercise.status),
        )
        for exercise in exercises
    ]


def build_class_dashboard_summary(db: Session, class_id: str) -> ClassDashboardSummary:
    users = db.scalars(
        select(User)
        .where(User.is_active.is_(True))
        .order_by(User.student_id)
    ).all()
    kcs = db.scalars(select(KnowledgeComponentModel).order_by(KnowledgeComponentModel.id)).all()
    mastery_rows = db.scalars(select(StudentMastery)).all()
    mastery_by_student_kc = {
        (row.student_id, row.kc_id): row.mastery
        for row in mastery_rows
    }

    heatmap = [
        ClassHeatmapCell(
            student_id=user.student_id,
            display_name=user.name,
            kc_code=kc.id,
            kc_name=kc.name,
            mastery=mastery_by_student_kc.get((user.student_id, kc.id), 0.0),
        )
        for user in users
        for kc in kcs
    ]
    student_averages = {
        user.student_id: average(
            mastery_by_student_kc.get((user.student_id, kc.id), 0.0)
            for kc in kcs
        )
        for user in users
    }
    risk_students = build_risk_students(users, kcs, mastery_by_student_kc, student_averages)
    weak_kcs = build_weak_kcs(users, kcs, mastery_by_student_kc)
    average_mastery = average(cell.mastery for cell in heatmap)

    updated_at = datetime.now(timezone.utc).isoformat()

    return ClassDashboardSummary(
        class_id=class_id,
        updated_at=updated_at,
        totals=DashboardTotals(
            students=len(users),
            average_mastery=round(average_mastery, 2),
            submissions_7d=0,
            hint_requests_7d=0,
            at_risk_count=len(risk_students),
        ),
        heatmap=heatmap,
        risk_students=risk_students,
        weak_kcs=weak_kcs,
        recent_submissions=[],
    )


def build_risk_students(
    users: list[User],
    kcs: list[KnowledgeComponentModel],
    mastery_by_student_kc: dict[tuple[str, str], float],
    student_averages: dict[str, float],
) -> list[RiskStudent]:
    risk_students: list[RiskStudent] = []

    for user in users:
        average_mastery = student_averages[user.student_id]

        if average_mastery >= 0.6:
            continue

        weakest_kc = min(
            kcs,
            key=lambda kc: mastery_by_student_kc.get((user.student_id, kc.id), 0.0),
            default=None,
        )

        risk_students.append(
            RiskStudent(
                student_id=user.student_id,
                display_name=user.name,
                average_mastery=round(average_mastery, 2),
                failed_attempts_7d=0,
                hints_used_7d=0,
                weakest_kc=weakest_kc.name if weakest_kc is not None else "No KC data",
                last_active_at="No recent activity",
            )
        )

    return sorted(risk_students, key=lambda student: student.average_mastery)


def build_weak_kcs(
    users: list[User],
    kcs: list[KnowledgeComponentModel],
    mastery_by_student_kc: dict[tuple[str, str], float],
) -> list[WeakKcSummary]:
    weak_kcs = [
        WeakKcSummary(
            kc_code=kc.id,
            kc_name=kc.name,
            average_mastery=round(
                average(mastery_by_student_kc.get((user.student_id, kc.id), 0.0) for user in users),
                2,
            ),
            affected_students=sum(
                1
                for user in users
                if mastery_by_student_kc.get((user.student_id, kc.id), 0.0) < 0.6
            ),
            trend=0.0,
        )
        for kc in kcs
    ]

    return sorted(weak_kcs, key=lambda kc: kc.average_mastery)


def average(values: Iterable[float]) -> float:
    items = list(values)

    if not items:
        return 0.0

    return sum(items) / len(items)
