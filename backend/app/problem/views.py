from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status

from app.database.core import DbSession
from app.auth.service import get_current_user
from app.problem.models import ProblemRead, ProblemSummary
from app.problem import service as problem_service

router = APIRouter(tags=["problems"], prefix="/problems")


@router.get("", response_model=list[ProblemSummary])
def list_problems(
    db_session: DbSession,
    skip: int = 0,
    limit: int = 50,
):
    return problem_service.get_all(db_session, skip=skip, limit=limit)


@router.get("/{problem_id}")
def get_problem(
    problem_id: int,
    db_session: DbSession,
):
    problem = problem_service.get_by_id(db_session, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    return ProblemRead.model_validate(problem).model_copy(update={
        "statement": problem_service.get_statement(problem),
        "test_count": problem_service.get_test_count(problem),
    })


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_problem(
    db_session: DbSession,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Upload must be a .zip file")

    try:
        zip_bytes = file.file.read()
        problem = problem_service.import_polygon_package(db_session, zip_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ProblemRead.model_validate(problem).model_copy(update={
        "test_count": problem_service.get_test_count(problem),
    })


@router.delete("/{problem_id}")
def delete_problem(
    problem_id: int,
    db_session: DbSession,
    current_user=Depends(get_current_user),
):
    problem = problem_service.get_by_id(db_session, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    problem_service.delete(db_session, problem)
    return {"message": "Problem deleted"}
