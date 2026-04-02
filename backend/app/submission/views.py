from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status

from app.database.core import DbSession
from app.auth.service import get_current_user
from app.problem import service as problem_service
from app.contest import service as contest_service
from app.submission.models import SubmissionCreate, SubmissionRead, SubmissionSummary
from app.submission import service as submission_service
from app.judge.service import judge_submission

router = APIRouter(tags=["submissions"], prefix="/submissions")


@router.post("", response_model=SubmissionRead, status_code=status.HTTP_201_CREATED)
def create_submission(
    submission_in: SubmissionCreate,
    db_session: DbSession,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    # Validate problem exists
    problem = problem_service.get_by_id(db_session, submission_in.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Contest validation if submitting to a contest
    if submission_in.contest_id:
        contest = contest_service.get_by_id(db_session, submission_in.contest_id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        if not contest_service.is_contest_running(contest):
            raise HTTPException(status_code=400, detail="Contest is not running")
        if not contest_service.get_participant(db_session, contest.id, current_user.id):
            raise HTTPException(status_code=403, detail="Not registered for this contest")
        # Check problem belongs to contest
        contest_problem_ids = {cp.problem_id for cp in contest.contest_problems}
        if submission_in.problem_id not in contest_problem_ids:
            raise HTTPException(status_code=400, detail="Problem not in this contest")

    submission = submission_service.create(db_session, current_user.id, submission_in)
    background_tasks.add_task(judge_submission, submission.id)
    return submission


@router.get("/me", response_model=list[SubmissionSummary])
def my_submissions(
    db_session: DbSession,
    current_user=Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
):
    return submission_service.get_by_user(db_session, current_user.id, skip=skip, limit=limit)


@router.get("/{submission_id}", response_model=SubmissionRead)
def get_submission(
    submission_id: int,
    db_session: DbSession,
    current_user=Depends(get_current_user),
):
    submission = submission_service.get_by_id(db_session, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.get("/problem/{problem_id}", response_model=list[SubmissionSummary])
def submissions_by_problem(
    problem_id: int,
    db_session: DbSession,
    skip: int = 0,
    limit: int = 50,
):
    return submission_service.get_by_problem(db_session, problem_id, skip=skip, limit=limit)
