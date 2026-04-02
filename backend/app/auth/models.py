from pydantic import BaseModel, ConfigDict, EmailStr
from app.database.core import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import TimeStampMixin
import bcrypt 


def hash_password(password: str):
    """Hash a password using bcrypt."""
    pw = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)


class User(Base, TimeStampMixin):
    """SQLAlchemy model for a user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes]

    email: Mapped[str] = mapped_column(String(255), unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]

    submissions: Mapped[list["Submission"]] = relationship(back_populates="user")
    contest_participations: Mapped[list["ContestParticipant"]] = relationship(back_populates="user")

    def verify_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        if not password or not self.password:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    def set_password(self, password: str) -> None:
        """Set a new password for the user."""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password = hash_password(password)


class UserBase(BaseModel):
    """Base Pydantic model for user data."""
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: EmailStr

class UserRegister(UserBase):
    """Pydantic model for user registration data."""
    first_name: str
    last_name: str
    password: str

class UserPublic(UserBase):
    first_name: str
    last_name: str
    

class RefreshTokenRequest(BaseModel):
    refresh_token: str