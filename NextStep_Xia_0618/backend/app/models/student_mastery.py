from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


# Store one student's mastery value for one knowledge component.
class StudentMastery(Base):
    __tablename__ = "student_mastery"

    student_id: Mapped[str] = mapped_column(ForeignKey("users.student_id"), primary_key=True)
    kc_id: Mapped[str] = mapped_column(ForeignKey("knowledge_components.id"), primary_key=True)
    mastery: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
