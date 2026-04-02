from enum import Enum as PyEnum
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Float, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.core import Base
from app.models import TimeStampMixin


class CheckerType(str, PyEnum):
    EXACT = "exact"
    FLOAT = "float"
    SPECIAL = "special"
    INTERACTIVE = "interactive"


class Problem(Base, TimeStampMixin):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    time_limit: Mapped[float] = mapped_column(Float, default=1.0)
    memory_limit: Mapped[int] = mapped_column(Integer, default=256)
    checker_type: Mapped[str] = mapped_column(
        Enum(CheckerType, native_enum=False), default=CheckerType.EXACT
    )
    storage_path: Mapped[str] = mapped_column(String(512))

    submissions: Mapped[list["Submission"]] = relationship(back_populates="problem")
    contest_problems: Mapped[list["ContestProblem"]] = relationship(back_populates="problem")


# --- Pydantic schemas ---

class ProblemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    time_limit: float
    memory_limit: int
    checker_type: CheckerType
    storage_path: str
    created_at: datetime
    updated_at: datetime
    statement: str = ""
    test_count: int = 0


class ProblemSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    time_limit: float
    memory_limit: int
