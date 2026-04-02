from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.contest.models import (
    Contest,
    ContestProblem,
    ContestParticipant,
    ContestCreate,
    ContestUpdate,
    ContestProblemCreate,
    ScoringType,
)


def get_all(db_session: Session, skip: int = 0, limit: int = 50) -> list[Contest]:
    return (
        db_session.query(Contest)
        .order_by(Contest.start_time.desc())
        .offset(skip).limit(limit).all()
    )


def get_by_id(db_session: Session, contest_id: int) -> Contest | None:
    return db_session.query(Contest).filter(Contest.id == contest_id).first()


def create(db_session: Session, contest_in: ContestCreate) -> Contest:
    contest = Contest(
        title=contest_in.title,
        description=contest_in.description,
        start_time=contest_in.start_time,
        end_time=contest_in.end_time,
        scoring_type=contest_in.scoring_type,
    )
    db_session.add(contest)
    db_session.flush()

    for cp in contest_in.problems:
        db_session.add(ContestProblem(
            contest_id=contest.id,
            problem_id=cp.problem_id,
            label=cp.label,
        ))

    db_session.commit()
    db_session.refresh(contest)
    return contest


def update(db_session: Session, contest: Contest, contest_in: ContestUpdate) -> Contest:
    for field, value in contest_in.model_dump(exclude_unset=True).items():
        setattr(contest, field, value)
    db_session.commit()
    db_session.refresh(contest)
    return contest


def delete(db_session: Session, contest: Contest) -> None:
    db_session.delete(contest)
    db_session.commit()


# --- Contest Problems ---

def add_problem(db_session: Session, contest_id: int, cp_in: ContestProblemCreate) -> ContestProblem:
    cp = ContestProblem(contest_id=contest_id, problem_id=cp_in.problem_id, label=cp_in.label)
    db_session.add(cp)
    db_session.commit()
    db_session.refresh(cp)
    return cp


def remove_problem(db_session: Session, contest_id: int, problem_id: int) -> None:
    cp = (
        db_session.query(ContestProblem)
        .filter(ContestProblem.contest_id == contest_id, ContestProblem.problem_id == problem_id)
        .first()
    )
    if cp:
        db_session.delete(cp)
        db_session.commit()


# --- Participants ---

def register_participant(db_session: Session, contest_id: int, user_id: int) -> ContestParticipant:
    participant = ContestParticipant(contest_id=contest_id, user_id=user_id)
    db_session.add(participant)
    db_session.commit()
    db_session.refresh(participant)
    return participant


def get_participant(db_session: Session, contest_id: int, user_id: int) -> ContestParticipant | None:
    return (
        db_session.query(ContestParticipant)
        .filter(
            ContestParticipant.contest_id == contest_id,
            ContestParticipant.user_id == user_id,
        )
        .first()
    )


def is_contest_running(contest: Contest) -> bool:
    now = datetime.now(timezone.utc)
    return contest.start_time <= now <= contest.end_time


# --- Standings ---

def get_standings(db_session: Session, contest_id: int) -> list[ContestParticipant]:
    return (
        db_session.query(ContestParticipant)
        .filter(ContestParticipant.contest_id == contest_id)
        .order_by(
            ContestParticipant.score.desc(),
            ContestParticipant.penalty.asc(),
        )
        .all()
    )


def recalculate_participant_score(
    db_session: Session, contest: Contest, user_id: int
) -> ContestParticipant | None:
    from app.submission.models import Submission, Verdict

    participant = get_participant(db_session, contest.id, user_id)
    if not participant:
        return None

    contest_subs = (
        db_session.query(Submission)
        .filter(Submission.contest_id == contest.id, Submission.user_id == user_id)
        .order_by(Submission.created_at)
        .all()
    )

    if contest.scoring_type == ScoringType.ICPC:
        solved = set()
        total_penalty = 0
        for sub in contest_subs:
            if sub.problem_id in solved:
                continue
            if sub.verdict == Verdict.ACCEPTED:
                solved.add(sub.problem_id)
                minutes = int((sub.created_at - contest.start_time).total_seconds() / 60)
                wrong_attempts = sum(
                    1 for s in contest_subs
                    if s.problem_id == sub.problem_id
                    and s.verdict != Verdict.ACCEPTED
                    and s.created_at < sub.created_at
                )
                total_penalty += minutes + (wrong_attempts * 20)
        participant.score = len(solved)
        participant.penalty = total_penalty
    else:
        solved = set()
        for sub in contest_subs:
            if sub.verdict == Verdict.ACCEPTED:
                solved.add(sub.problem_id)
        participant.score = len(solved)
        participant.penalty = 0

    db_session.commit()
    db_session.refresh(participant)
    return participant
