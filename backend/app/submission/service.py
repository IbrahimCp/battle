from sqlalchemy.orm import Session

from app.submission.models import Submission, SubmissionCreate, SubmissionVerdictUpdate


def create(db_session: Session, user_id: int, submission_in: SubmissionCreate) -> Submission:
    submission = Submission(
        user_id=user_id,
        problem_id=submission_in.problem_id,
        contest_id=submission_in.contest_id,
        language=submission_in.language,
        source_code=submission_in.source_code,
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    return submission


def get_by_id(db_session: Session, submission_id: int) -> Submission | None:
    return db_session.query(Submission).filter(Submission.id == submission_id).first()


def get_by_user(db_session: Session, user_id: int, skip: int = 0, limit: int = 50) -> list[Submission]:
    return (
        db_session.query(Submission)
        .filter(Submission.user_id == user_id)
        .order_by(Submission.created_at.desc())
        .offset(skip).limit(limit).all()
    )


def get_by_problem(db_session: Session, problem_id: int, skip: int = 0, limit: int = 50) -> list[Submission]:
    return (
        db_session.query(Submission)
        .filter(Submission.problem_id == problem_id)
        .order_by(Submission.created_at.desc())
        .offset(skip).limit(limit).all()
    )


def get_by_contest(db_session: Session, contest_id: int, skip: int = 0, limit: int = 50) -> list[Submission]:
    return (
        db_session.query(Submission)
        .filter(Submission.contest_id == contest_id)
        .order_by(Submission.created_at.desc())
        .offset(skip).limit(limit).all()
    )


def update_verdict(db_session: Session, submission: Submission, verdict_in: SubmissionVerdictUpdate) -> Submission:
    submission.verdict = verdict_in.verdict
    if verdict_in.time_used is not None:
        submission.time_used = verdict_in.time_used
    if verdict_in.memory_used is not None:
        submission.memory_used = verdict_in.memory_used
    db_session.commit()
    db_session.refresh(submission)
    return submission
