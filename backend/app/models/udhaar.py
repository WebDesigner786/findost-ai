"""SQLAlchemy UdhaarRecord Model"""

from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Text, Numeric, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class UdhaarRecord(Base, TimestampMixin):
    __tablename__ = "udhaar_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    issued_at: Mapped[date] = mapped_column(Date, nullable=False)
    due_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Strict NUMERIC(14, 2) for exact PKR balance
    outstanding: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    status: Mapped[str] = mapped_column(String(32), default="current", nullable=False, index=True)  # current, overdue, settled
    age_bucket: Mapped[str] = mapped_column(String(16), default="30d", nullable=False)  # 30d, 60d, 90d+
    source_ref: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    workspace = relationship("Workspace", back_populates="udhaar_records")
