from fastapi import APIRouter, HTTPException, Depends, status

from app.database.core import DbSession
from app.auth.service import get_current_user
from app.contest.models import (
    ContestCreate,
    ContestUpdate,
    ContestRead,
    ContestSummary,
    ContestProblemCreate,
    ContestProblemRead,
    ContestParticipantRead,
    StandingsEntry,
)
from app.contest import service as contest_service

router = APIRouter(tags=["contests"], prefix="/contests")


@router.get("", response_model=list[ContestSummary])
def list_contests(
    db_session: DbSession,
    skip: int = 0,
    limit: int = 50,
):
    return contest_service.get_all(db_session, skip=skip, limit=limit)


@router.post("", response_model=ContestRead, status_code=status.HTTP_201_CREATED)
def create_contest(
    contest_in: ContestCreate,
    db_session: DbSession,
    current_user=Depends(get_current_user),
):
    return contest_service.create(db_session, contest_in)


@router.get("/{contest_id}", response_model=ContestRead)
def get_contest(
    contest_id: int,
    db_session: DbSession,
):
    contest = contest_service.get_by_id(db_session, contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    return contest


@router.put("/{contest_id}", response_model=ContestRead)
def update_contest(
    contest_id: int,
    contest_in: ContestUpdate,
    db_session: DbSession,
    current_user=Depends(get_current_user),
):
    contest = contest_service.get_by_id(db_session, contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    return contest_service.update(db_session, contest, contest_in)


@router.delete("/{contest_id}")
def delete_contest(
    contest_id: int,
    db_session: DbSession,
    current_user=Depends(get_current_user),
):
    contest = contest_service.get_by_id(db_session, contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    contest_service.delete(db_session, contest)
    return {"message": "Contest deleted"}


# --- Contest Problems ---

@router.post("/{contest_id}/problems", response_model=ContestProblemRead, status_code=status.HTTP_201_CREATED)
def add_problem_to_contest(
    contest_id: int,
    cp_in: ContestProblemCreate,
    db_session: DbSession,
    current_user=Depends(get_current_user),
):
    contest = contest_service.get_by_id(db_session, contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    return contest_service.add_problem(db_session, contest_id, cp_in)


@router.delete("/{contest_id}/problems/{problem_id}")
def remove_problem_from_contest(
    contest_id: int,
    problem_id: int,
    db_session: DbSession,
    current_user=Depends(get_current_user),
):
    contest_service.remove_problem(db_session, contest_id, problem_id)
    return {"message": "Problem removed from contest"}


# --- Participants ---

@router.post("/{contest_id}/register", response_model=ContestParticipantRead, status_code=status.HTTP_201_CREATED)
def register_for_contest(
    contest_id: int,
    db_session: DbSession,
    current_user=Depends(get_current_user),
):
    contest = contest_service.get_by_id(db_session, contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    existing = contest_service.get_participant(db_session, contest_id, current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Already registered")

    return contest_service.register_participant(db_session, contest_id, current_user.id)


@router.get("/{contest_id}/standings", response_model=list[StandingsEntry])
def get_standings(
    contest_id: int,
    db_session: DbSession,
):
    contest = contest_service.get_by_id(db_session, contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    participants = contest_service.get_standings(db_session, contest_id)
    return [
        StandingsEntry(
            user_id=p.user_id,
            username=p.user.username,
            score=p.score,
            penalty=p.penalty,
            rank=i + 1,
        )
        for i, p in enumerate(participants)
    ]
