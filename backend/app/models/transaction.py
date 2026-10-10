"""SQLAlchemy Transaction Model"""

from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Text, Numeric, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    occurred_at: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    merchant: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Strict NUMERIC(14, 2) for exact PKR values
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    
    direction: Mapped[str] = mapped_column(String(16), nullable=False)  # inflow, outflow
    category: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), default=Decimal("1.000"), nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), default="confirmed", nullable=False)  # confirmed, needs_review
    source_ref: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)

    # Human-in-the-loop Audit Trail
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    original_merchant: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    original_category: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    original_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    correction_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    workspace = relationship("Workspace", back_populates="transactions")
