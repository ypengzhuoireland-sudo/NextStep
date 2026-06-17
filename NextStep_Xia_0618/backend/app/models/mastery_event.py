from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MasteryEvent(Base):
    __tablename__ = "mastery_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("users.student_id"), nullable=False)
    exercise_id: Mapped[str] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
    )
    kc_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_components.id", ondelete="CASCADE"),
        nullable=False,
    )
    old_mastery: Mapped[float] = mapped_column(Float, nullable=False)
    new_mastery: Mapped[float] = mapped_column(Float, nullable=False)
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False)
    bkt_prior: Mapped[float] = mapped_column(Float, nullable=False)
    bkt_learn: Mapped[float] = mapped_column(Float, nullable=False)
    bkt_guess: Mapped[float] = mapped_column(Float, nullable=False)
    bkt_slip: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
