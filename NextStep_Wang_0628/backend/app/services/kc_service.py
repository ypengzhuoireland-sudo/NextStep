from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.exercise import ExerciseKnowledgeComponent
from app.models.knowledge_component import KnowledgeComponent
from app.schemas.kcs import (
    KnowledgeComponentDetail,
    KnowledgeComponentItem,
    KnowledgeComponentListResponse,
)


def list_knowledge_components(db: Session) -> KnowledgeComponentListResponse:
    rows = db.execute(
        select(
            KnowledgeComponent.id,
            KnowledgeComponent.name,
            KnowledgeComponent.short_name,
            KnowledgeComponent.description,
            func.count(ExerciseKnowledgeComponent.exercise_id),
        )
        .outerjoin(
            ExerciseKnowledgeComponent,
            ExerciseKnowledgeComponent.kc_id == KnowledgeComponent.id,
        )
        .group_by(
            KnowledgeComponent.id,
            KnowledgeComponent.name,
            KnowledgeComponent.short_name,
            KnowledgeComponent.description,
        )
        .order_by(KnowledgeComponent.id)
    ).all()

    items = [
        KnowledgeComponentItem(
            code=kc_id,
            name=name,
            shortName=short_name,
            description=description or "",
            exerciseCount=exercise_count,
        )
        for kc_id, name, short_name, description, exercise_count in rows
    ]

    return KnowledgeComponentListResponse(items=items, total=len(items))


def get_knowledge_component_by_code(
    db: Session,
    code: str,
) -> KnowledgeComponentDetail | None:
    kc = db.get(KnowledgeComponent, code)

    if kc is None:
        return None

    exercise_ids = db.scalars(
        select(ExerciseKnowledgeComponent.exercise_id)
        .where(ExerciseKnowledgeComponent.kc_id == code)
        .order_by(ExerciseKnowledgeComponent.exercise_id)
    ).all()

    return KnowledgeComponentDetail(
        code=kc.id,
        name=kc.name,
        shortName=kc.short_name,
        description=kc.description or "",
        exerciseCount=len(exercise_ids),
        exerciseIds=list(exercise_ids),
    )
