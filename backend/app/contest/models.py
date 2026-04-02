from enum import Enum as PyEnum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import String, Text, Integer, ForeignKey, Enum, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.core import Base
from app.models import TimeStampMixin


class ScoringType(str, PyEnum):
    ICPC = "icpc"
    IOI = "ioi"


class Contest(Base, TimeStampMixin):
    __tablename__ = "contests"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scoring_type: Mapped[str] = mapped_column(
        Enum(ScoringType, native_enum=False), default=ScoringType.ICPC
    )

    contest_problems: Mapped[list["ContestProblem"]] = relationship(
        back_populates="contest", cascade="all, delete-orphan",
        order_by="ContestProblem.label"
    )
    participants: Mapped[list["ContestParticipant"]] = relationship(
        back_populates="contest", cascade="all, delete-orphan"
    )
    submissions: Mapped[list["Submission"]] = relationship(back_populates="contest")


class ContestProblem(Base):
    __tablename__ = "contest_problems"
    __table_args__ = (
        UniqueConstraint("contest_id", "problem_id", name="uq_contest_problem"),
        UniqueConstraint("contest_id", "label", name="uq_contest_label"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id", ondelete="CASCADE"))
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"))
    label: Mapped[str] = mapped_column(String(5))

    contest: Mapped["Contest"] = relationship(back_populates="contest_problems")
    problem: Mapped["Problem"] = relationship(back_populates="contest_problems")


class ContestParticipant(Base, TimeStampMixin):
    __tablename__ = "contest_participants"
    __table_args__ = (
        UniqueConstraint("contest_id", "user_id", name="uq_contest_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[int] = mapped_column(Integer, default=0)
    penalty: Mapped[int] = mapped_column(Integer, default=0)

    contest: Mapped["Contest"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship(back_populates="contest_participations")


# --- Pydantic schemas ---

class ContestProblemCreate(BaseModel):
    problem_id: int
    label: str


class ContestProblemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    problem_id: int
    label: str


class ContestCreate(BaseModel):
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    scoring_type: ScoringType = ScoringType.ICPC
    problems: list[ContestProblemCreate] = []

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v, info):
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class ContestUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    scoring_type: ScoringType | None = None


class ContestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime
    scoring_type: ScoringType
    contest_problems: list[ContestProblemRead]
    created_at: datetime
    updated_at: datetime


class ContestSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    start_time: datetime
    end_time: datetime
    scoring_type: ScoringType


class ContestParticipantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    score: int
    penalty: int
    created_at: datetime


class StandingsEntry(BaseModel):
    user_id: int
    username: str
    score: int
    penalty: int
    rank: int
