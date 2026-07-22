from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ClassEnrollment(Base):
    __tablename__ = "class_enrollments"

    class_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.student_id", ondelete="CASCADE"),
        primary_key=True,
    )
