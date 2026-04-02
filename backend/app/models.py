from datetime import datetime, timedelta, timezone
from sqlalchemy import DateTime, event
from sqlalchemy.orm import Mapped, mapped_column

class TimeStampMixin:
    """Timestamping mixin for created_at and updated_at fields."""

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), sort_order=9998)
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc),
        sort_order=9998
    )
    