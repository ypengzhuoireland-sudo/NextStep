from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KnowledgeComponentBKTParameters(Base):
    __tablename__ = "kc_bkt_parameters"

    kc_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_components.id", ondelete="CASCADE"),
        primary_key=True,
    )
    prior: Mapped[float] = mapped_column(Float, nullable=False, default=0.2)
    learn: Mapped[float] = mapped_column(Float, nullable=False, default=0.15)
    guess: Mapped[float] = mapped_column(Float, nullable=False, default=0.2)
    slip: Mapped[float] = mapped_column(Float, nullable=False, default=0.1)
