"""SQLAlchemy Recommendation Model"""

from decimal import Decimal
from sqlalchemy import String, Text, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    plain_reason: Mapped[str] = mapped_column(Text, nullable=False)

    # Strict NUMERIC(14, 2) estimated liquidity impact
    estimated_impact: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    time_horizon: Mapped[str] = mapped_column(String(64), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)  # cash_flow, supplier, collections, tax
    evidence_transaction_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    evidence_source_refs: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    assumptions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    workspace = relationship("Workspace", back_populates="recommendations")
