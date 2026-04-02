from enum import Enum as PyEnum
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Text, Integer, Float, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.core import Base
from app.models import TimeStampMixin


class Verdict(str, PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT = "time_limit"
    MEMORY_LIMIT = "memory_limit"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"


class Language(str, PyEnum):
    CPP = "cpp"
    PYTHON = "python"
    JAVA = "java"


class Submission(Base, TimeStampMixin):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"))
    contest_id: Mapped[int | None] = mapped_column(ForeignKey("contests.id"), nullable=True)

    language: Mapped[str] = mapped_column(Enum(Language, native_enum=False))
    source_code: Mapped[str] = mapped_column(Text)

    verdict: Mapped[str] = mapped_column(
        Enum(Verdict, native_enum=False), default=Verdict.PENDING
    )
    time_used: Mapped[float | None] = mapped_column(Float, nullable=True)
    memory_used: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship(back_populates="submissions")
    problem: Mapped["Problem"] = relationship(back_populates="submissions")
    contest: Mapped["Contest | None"] = relationship(back_populates="submissions") 


# --- Pydantic schemas ---

class SubmissionCreate(BaseModel):
    problem_id: int
    contest_id: int | None = None
    language: Language
    source_code: str


class SubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    problem_id: int
    contest_id: int | None
    language: Language
    source_code: str
    verdict: Verdict
    time_used: float | None
    memory_used: int | None
    created_at: datetime
    updated_at: datetime


class SubmissionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    problem_id: int
    contest_id: int | None
    language: Language
    verdict: Verdict
    time_used: float | None
    memory_used: int | None
    created_at: datetime


class SubmissionVerdictUpdate(BaseModel):
    verdict: Verdict
    time_used: float | None = None
    memory_used: int | None = None
