from fastapi import APIRouter

from app.auth.views import router as auth_router
from app.problem.views import router as problem_router
from app.submission.views import router as submission_router
from app.contest.views import router as contest_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(problem_router)
api_router.include_router(submission_router)
api_router.include_router(contest_router)

