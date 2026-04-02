from sqlalchemy.engine.url import make_url
import re
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session, DeclarativeBase, declared_attr
from fastapi import Depends
from typing import Annotated
from app import config


# Create the default engine with standard timeout
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

def get_db():
    with Session(engine) as session:
        yield session

DbSession = Annotated[Session, Depends(get_db)]

class Base(DeclarativeBase):
   pass

def init_db():
    from app.auth.models import User
    from app.problem.models import Problem
    from app.submission.models import Submission
    from app.contest.models import Contest, ContestProblem, ContestParticipant
    Base.metadata.create_all(engine)
