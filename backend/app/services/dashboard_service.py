from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise as ExerciseModel
from app.models.knowledge_component import KnowledgeComponent as KnowledgeComponentModel
from app.models.student_mastery import StudentMastery
from app.schemas.dashboard import DashboardResponse, Exercise, KnowledgeComponent
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
