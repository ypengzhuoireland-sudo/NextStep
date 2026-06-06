from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


# Store one coding exercise and its runnable test cases.
class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kc_id: Mapped[str] = mapped_column(ForeignKey("knowledge_components.id"), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ready")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    starter_code: Mapped[str] = mapped_column(Text, nullable=False)
    test_cases: Mapped[list[dict[str, str]]] = mapped_column(JSON, nullable=False, default=list)
