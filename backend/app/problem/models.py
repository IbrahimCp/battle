from datetime import datetime

from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.core import Base
from app.models import TimeStampMixin


class Problem(Base, TimeStampMixin):
    __tablename__ = "problems"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    short_name: Mapped[str] = mapped_column(String(255), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    time_limit: Mapped[float] = mapped_column(Float, default=1.0)
    memory_limit: Mapped[int] = mapped_column(Integer, default=256)
    test_count: Mapped[int] = mapped_column(Integer, default=0)

    submissions: Mapped[list["Submission"]] = relationship(back_populates="problem")  # type: ignore[name-defined]
    contest_problems: Mapped[list["ContestProblem"]] = relationship(back_populates="problem")  # type: ignore[name-defined]


# --- Pydantic schemas ---

class ProblemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    short_name: str
    title: str
    time_limit: float
    memory_limit: int
    test_count: int
    statement: str = ""
    created_at: datetime
    updated_at: datetime


class ProblemSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    short_name: str
    title: str
    time_limit: float
    memory_limit: int
