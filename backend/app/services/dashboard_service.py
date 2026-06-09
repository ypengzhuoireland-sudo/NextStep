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
from app.services.recommendation_service import choose_recommended_exercise


# Build the dashboard response using the authenticated user and PostgreSQL data.
def build_dashboard_response(db: Session, current_user: UserProfile) -> DashboardResponse:
    kcs = list_dashboard_mastery(db, current_user.student_id)
    exercises = list_dashboard_exercises(db)
    mastery_average = round(sum(kc.mastery for kc in kcs) / len(kcs), 2) if kcs else 0.0
    recommended = choose_recommended_exercise(exercises)

    return DashboardResponse(
        student_name=current_user.name,
        active_goal="Practice weak Python concepts",
        backend_status="connected",
        mastery_average=mastery_average,
        recommended_exercise_id=recommended.id,
        knowledge_components=kcs,
        exercises=exercises,
    )


# Read the current student's KC mastery values from PostgreSQL.
def list_dashboard_mastery(db: Session, student_id: str) -> list[KnowledgeComponent]:
    rows = db.execute(
        select(
            KnowledgeComponentModel.id,
            KnowledgeComponentModel.name,
            StudentMastery.mastery,
        )
        .join(StudentMastery, StudentMastery.kc_id == KnowledgeComponentModel.id)
        .where(StudentMastery.student_id == student_id)
        .order_by(KnowledgeComponentModel.id)
    ).all()

    return [
        KnowledgeComponent(
            id=row.id,
            name=row.name,
            mastery=row.mastery,
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
            difficulty=exercise.difficulty,
            status=exercise.status,
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
            studentId=user.student_id,
            displayName=user.name,
            kcCode=kc.id,
            kcName=kc.name,
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

    return ClassDashboardSummary(
        classId=class_id,
        updatedAt=datetime.now(timezone.utc).isoformat(),
        totals=DashboardTotals(
            students=len(users),
            averageMastery=round(average_mastery, 2),
            submissions7d=0,
            hintRequests7d=0,
            atRiskCount=len(risk_students),
        ),
        heatmap=heatmap,
        riskStudents=risk_students,
        weakKcs=weak_kcs,
        recentSubmissions=[],
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
                studentId=user.student_id,
                displayName=user.name,
                averageMastery=round(average_mastery, 2),
                failedAttempts7d=0,
                hintsUsed7d=0,
                weakestKc=weakest_kc.name if weakest_kc is not None else "No KC data",
                lastActiveAt="No recent activity",
            )
        )

    return sorted(risk_students, key=lambda student: student.averageMastery)


def build_weak_kcs(
    users: list[User],
    kcs: list[KnowledgeComponentModel],
    mastery_by_student_kc: dict[tuple[str, str], float],
) -> list[WeakKcSummary]:
    weak_kcs = [
        WeakKcSummary(
            kcCode=kc.id,
            kcName=kc.name,
            averageMastery=round(
                average(mastery_by_student_kc.get((user.student_id, kc.id), 0.0) for user in users),
                2,
            ),
            affectedStudents=sum(
                1
                for user in users
                if mastery_by_student_kc.get((user.student_id, kc.id), 0.0) < 0.6
            ),
            trend=0.0,
        )
        for kc in kcs
    ]

    return sorted(weak_kcs, key=lambda kc: kc.averageMastery)


def average(values: Iterable[float]) -> float:
    items = list(values)

    if not items:
        return 0.0

    return sum(items) / len(items)
