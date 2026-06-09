from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


# Store one coding exercise and its runnable test cases.
class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="coding")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kc_id: Mapped[str] = mapped_column(ForeignKey("knowledge_components.id"), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ready")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    function_name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    starter_code: Mapped[str] = mapped_column(Text, nullable=False)
    test_cases: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    hidden_tests: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hints: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    solution: Mapped[str | None] = mapped_column(Text)


# Store the full many-to-many mapping between exercises and knowledge components.
class ExerciseKnowledgeComponent(Base):
    __tablename__ = "exercise_kcs"

    exercise_id: Mapped[str] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"),
        primary_key=True,
    )
    kc_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_components.id", ondelete="CASCADE"),
        primary_key=True,
    )
