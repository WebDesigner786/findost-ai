"""SQLAlchemy Workspace Model"""

from decimal import Decimal
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.document import Document
    from app.models.udhaar import UdhaarRecord
    from app.models.forecast import Forecast
    from app.models.anomaly import Anomaly
    from app.models.recommendation import Recommendation


class Workspace(Base, TimestampMixin):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # student, household, sme, enterprise
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="PKR", nullable=False)
    timezone: Mapped[str] = mapped_column(String(32), default="Asia/Karachi", nullable=False)
    
    # Strict NUMERIC(14,2) for exact PKR balance representation
    starting_balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    
    features: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Relationships
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="workspace", cascade="all, delete-orphan"
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="workspace", cascade="all, delete-orphan"
    )
    udhaar_records: Mapped[List["UdhaarRecord"]] = relationship(
        "UdhaarRecord", back_populates="workspace", cascade="all, delete-orphan"
    )
    forecasts: Mapped[List["Forecast"]] = relationship(
        "Forecast", back_populates="workspace", cascade="all, delete-orphan"
    )
    anomalies: Mapped[List["Anomaly"]] = relationship(
        "Anomaly", back_populates="workspace", cascade="all, delete-orphan"
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation", back_populates="workspace", cascade="all, delete-orphan"
    )
