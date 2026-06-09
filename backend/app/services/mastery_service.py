from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_component import KnowledgeComponent
from app.models.student_mastery import StudentMastery
from app.models.user import User
from app.schemas.mastery import MasteryKnowledgeComponent, StudentMasteryProfile


def get_student_mastery_profile(
    db: Session,
    student_id: str,
) -> StudentMasteryProfile | None:
    user = db.query(User).filter(User.student_id == student_id).one_or_none()

    if user is None:
        return None

    rows = db.execute(
        select(
            KnowledgeComponent,
            StudentMastery.mastery,
            StudentMastery.updated_at,
        )
        .outerjoin(
            StudentMastery,
            (StudentMastery.kc_id == KnowledgeComponent.id)
            & (StudentMastery.student_id == student_id),
        )
        .order_by(KnowledgeComponent.id)
    ).all()

    latest_update = max(
        (updated_at for _, _, updated_at in rows if updated_at is not None),
        default=datetime.now(timezone.utc),
    )

    return StudentMasteryProfile(
        studentId=student_id,
        updatedAt=latest_update.isoformat(),
        items=[
            MasteryKnowledgeComponent(
                code=kc.id,
                name=kc.name,
                description=kc.description or "",
                mastery=mastery or 0.0,
                trend=0.0,
                state=mastery_state(mastery or 0.0),
            )
            for kc, mastery, _ in rows
        ],
    )


def mastery_state(mastery: float) -> str:
    if mastery >= 0.75:
        return "mastered"
    if mastery >= 0.6:
        return "almost_there"
    return "needs_practice"
