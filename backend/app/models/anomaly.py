"""SQLAlchemy Anomaly Model"""

from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Text, Numeric, Date, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class Anomaly(Base, TimestampMixin):
    __tablename__ = "anomalies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)  # spike, duplicate, supplier_price, overdue_udhaar
    severity: Mapped[str] = mapped_column(String(16), nullable=False)  # info, warning, critical
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    # Strict NUMERIC(14, 2) variance impact
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)

    period: Mapped[str] = mapped_column(String(128), nullable=False)
    transaction_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    source_refs: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    detected_at: Mapped[date] = mapped_column(Date, nullable=False)

    workspace = relationship("Workspace", back_populates="anomalies")
