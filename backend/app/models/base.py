"""Base model utilities and mixins."""

from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


def utc_now() -> datetime:
    """Returns current UTC timestamp with timezone."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Standard audit timestamps mixin for all operational tables."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
