"""SQLAlchemy Forecast and ForecastPoint Models"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import String, Integer, Date, DateTime, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin, utc_now


class Forecast(Base, TimestampMixin):
    __tablename__ = "forecasts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    horizon_days: Mapped[int] = mapped_column(Integer, default=90, nullable=False)
    assumptions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    source: Mapped[str] = mapped_column(String(16), default="api", nullable=False)

    workspace = relationship("Workspace", back_populates="forecasts")
    points: Mapped[List["ForecastPoint"]] = relationship(
        "ForecastPoint", back_populates="forecast", cascade="all, delete-orphan", order_by="ForecastPoint.point_date"
    )


class ForecastPoint(Base):
    __tablename__ = "forecast_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    forecast_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("forecasts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    point_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Strict NUMERIC(14, 2) amounts
    baseline: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    p10: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    p50: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    p90: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    simulated: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)

    forecast = relationship("Forecast", back_populates="points")
